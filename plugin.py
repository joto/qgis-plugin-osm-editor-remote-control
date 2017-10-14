#!python
from os.path import join, dirname
from PyQt4.QtGui import QAction, QIcon, QMessageBox
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
import urllib

# This value is very permissive and unlikely to work in high data-density areas
# 0.0015 sq deg seems to be reasonable for cities
MAX_DOWNLOAD_AREA_DEG = 0.1


class OSMEditorRemoteControlPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.action = None

    # noinspection PyPep8Naming
    def initGui(self):
        self.action = QAction(
            QIcon(join(dirname(__file__), 'icons', 'josm_icon.svg')),
            'OSM Editor Remote Control',
            self.iface.mainWindow())
        self.action.setEnabled(False)
        help = 'Send remote control command to OSM editor to load data at ' \
               'current map view.'
        self.action.setWhatsThis(help)
        self.action.setStatusTip(help)
        self.action.triggered.connect(self.run)
        self.iface.mapCanvas().layersChanged.connect(self.change_status)
        self.iface.mapCanvas().extentsChanged.connect(self.change_status)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)

    def get_lon_lat_extent(self):
        map_canvas = self.iface.mapCanvas()
        extent = map_canvas.mapSettings().extent()
        if map_canvas.hasCrsTransformEnabled():
            crs_map = map_canvas.mapSettings().destinationCrs()
        else:
            crs_map = map_canvas.currentLayer().crs()
        if crs_map.authid() != u'EPSG:4326':
            crs_4326 = QgsCoordinateReferenceSystem()
            crs_4326.createFromSrid(4326)
            return QgsCoordinateTransform(crs_map, crs_4326).transform(extent)
        return extent

    def change_status(self):
        if not self.iface.mapCanvas().currentLayer():
            self.action.setEnabled(False)
        else:
            extent = self.get_lon_lat_extent()
            self.action.setEnabled(
                extent.width() * extent.height() < MAX_DOWNLOAD_AREA_DEG)

    def run(self):
        extent = self.get_lon_lat_extent()
        url = 'http://localhost:8111/load_and_zoom?'
        query_string = 'left=%f&right=%f&top=%f&bottom=%f' % (
            extent.xMinimum(), extent.xMaximum(), extent.yMaximum(),
            extent.yMinimum())
        url += query_string
        try:
            f = urllib.urlopen(url, proxies={})
            result = f.read()
            f.close()
            if result.strip().upper() != 'OK':
                self.report_error('OSM reported: %s' % result)
        except IOError:
            self.report_error(
                'Could not connect to the OSM editor. Is the OSM editor '
                'running?')

    def report_error(self, error_message):
        QMessageBox.warning(
            self.iface.mainWindow(),
            'OSM Editor Remote Control Plugin', error_message)
