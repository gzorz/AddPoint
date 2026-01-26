
# -*- coding: utf-8 -*-

def classFactory(iface):
    """Vstopna točka za QGIS plugin."""
    from .AddPoint import AddPointPlugin
    return AddPointPlugin(iface)
