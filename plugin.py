#!python
from os.path import join, dirname
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import urllib

# This value is very permissive and unlikely to work in high data-density areas
# 0.0015 sq deg seems to be reasonable for cities
MAX_DOWLOAD_AREA_DEG = 0.1

class OSMEditorRemoteControlPlugin:
  def __init__(self, iface):
    self.iface = iface
  def initGui(self):
    self.action = QAction(QIcon(join(dirname(__file__), 'josm_icon.svg')), "OSM Editor Remote Control", self.iface.mainWindow())
    self.action.setEnabled(False);
    self.action.setWhatsThis("Send remote control command to OSM editor to load data at current map view")
    self.action.setStatusTip("Send remote control command to OSM editor to load data at current map view")
    QObject.connect(self.action, SIGNAL("triggered()"), self.run)
    QObject.connect(self.iface.mapCanvas(), SIGNAL("layersChanged()"), self.changeStatus)
    QObject.connect(self.iface.mapCanvas(), SIGNAL("extentsChanged()"), self.changeStatus)
    self.iface.addToolBarIcon(self.action)
  def unload(self):
    self.iface.removeToolBarIcon(self.action)
  def getLonLatExtent(self):
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
  def changeStatus(self):
    if not self.iface.mapCanvas().currentLayer():
      self.action.setEnabled(False);
    else:
      extent = self.getLonLatExtent()
      self.action.setEnabled(extent.width() * extent.height() < MAX_DOWLOAD_AREA_DEG)
  def run(self):
    extent = self.getLonLatExtent()
    url = 'http://localhost:8111/load_and_zoom?left=%f&right=%f&top=%f&bottom=%f' % (extent.xMinimum(), extent.xMaximum(), extent.yMaximum(), extent.yMinimum())
    print "OSMEditorRemoteControl plugin calling " + url
    try:
      f = urllib.urlopen(url, proxies={})
      result = f.read()
      f.close()
      if result.strip().upper() != 'OK':
        self.reportError("OSM reported: %s" % result)
    except IOError:
      self.reportError("Could not connect to the OSM editor. Is the OSM editor running?")
  def reportError(self, errorMessage):
      QMessageBox.warning(self.iface.mainWindow(), "OSM Editor Remote Control Plugin", errorMessage)
