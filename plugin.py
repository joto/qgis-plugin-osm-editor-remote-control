#!python
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import urllib
# initialize Qt resources from file resouces.py
import resources
class OSMEditorRemoteControlPlugin:
  def __init__(self, iface):
    self.iface = iface
  def initGui(self):
    self.action = QAction(QIcon(":/plugins/OSMEditorRemoteControl/icon.png"), "OSM Editor Remote Control", self.iface.mainWindow())
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
    extent = map_canvas.mapRenderer().extent()
    if map_canvas.hasCrsTransformEnabled():
        crs_map = map_canvas.mapRenderer().destinationCrs()
    else:
        crs_map = map_canvas.currentLayer().crs()
    if crs_map.authid() != u'EPSG:4326':
        crs_4326 = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
        return QgsCoordinateTransform(crs_map, crs_4326).transform(extent)
    return extent
  def changeStatus(self):
    if self.iface.mapCanvas().currentLayer() == None:
      self.action.setEnabled(False);
    else:
      extent = self.getLonLatExtent()
      self.action.setEnabled(extent.width() * extent.height() < 0.1)
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
      self.reportError("Could not connect to the OSM editor. Did you start it?")
  def reportError(self, errorMessage):
      QMessageBox.warning(self.iface.mainWindow(), "OSM Editor Remote Control Plugin", errorMessage)
