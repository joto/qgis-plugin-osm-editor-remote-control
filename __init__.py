#!python
def name():
 return "OSMEditorRemoteControl"
def description():
 return "OSM Editor remote control."
def version():
 return "Version 0.1"
def qgisMinimumVersion(): 
 return "1.5"
def authorName():
 return "Jochen Topf"
def classFactory(iface):
 from plugin import OSMEditorRemoteControlPlugin
 return OSMEditorRemoteControlPlugin(iface)
