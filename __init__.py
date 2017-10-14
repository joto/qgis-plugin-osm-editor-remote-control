#!python


# noinspection PyPep8Naming
def classFactory(iface):
    from plugin import OSMEditorRemoteControlPlugin
    return OSMEditorRemoteControlPlugin(iface)

