
# -*- coding: utf-8 -*-

def classFactory(iface):
    """
    Obvezen vstopni kavelj za QGIS; vrne instanco našega plugin-a.
    """
    from .AddPoint import AddPointPlugin
    return AddPointPlugin(iface)
