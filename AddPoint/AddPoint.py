
# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QDoubleValidator
from qgis.PyQt.QtWidgets import (
    QAction, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox
)

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
)

class AddPointPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self._dock = None
        self._action = None
        self._layers_combo = None
        self._lon_edit = None
        self._lat_edit = None

    # ----------------------------
    # QGIS plugin lifecycle
    # ----------------------------
    def initGui(self):
        # Akcija za vklop/izklop panela
        self._action = QAction("AddPoint panel", self.iface.mainWindow())
        self._action.setCheckable(True)
        self._action.setChecked(True)
        self._action.triggered.connect(self._toggle_dock)

        # Dodaj v meni in orodno vrstico (Plugins)
        self.iface.addPluginToMenu("AddPoint", self._action)
        self.iface.addToolBarIcon(self._action)

        # Ustvari in prikaži dock/panel
        self._create_dock()
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self._dock)
        self._action.setChecked(True)

        # Posodabljaj seznam slojev ob spremembah v projektu
        QgsProject.instance().layersAdded.connect(self._populate_layers_combo)
        QgsProject.instance().layersRemoved.connect(self._populate_layers_combo)

    def unload(self):
        # Odklopi signale (varno, tudi če niso povezani)
        try:
            QgsProject.instance().layersAdded.disconnect(self._populate_layers_combo)
        except Exception:
            pass
        try:
            QgsProject.instance().layersRemoved.disconnect(self._populate_layers_combo)
        except Exception:
            pass

        # Odstrani GUI elemente
        if self._action:
            self.iface.removeToolBarIcon(self._action)
            self.iface.removePluginMenu("AddPoint", self._action)
            self._action = None
        if self._dock:
            self.iface.removeDockWidget(self._dock)
            self._dock.deleteLater()
            self._dock = None

    # ----------------------------
    # UI
    # ----------------------------
    def _create_dock(self):
        self._dock = QDockWidget("AddPoint", self.iface.mainWindow())
        self._dock.setObjectName("AddPointDock")
        self._dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        container = QWidget(self._dock)
        vbox = QVBoxLayout(container)

        # Vnos koordinat (WGS84 lon, lat)
        form = QFormLayout()
        self._lon_edit = QLineEdit()
        self._lat_edit = QLineEdit()
        self._lon_edit.setPlaceholderText("npr. 14.50597")
        self._lat_edit.setPlaceholderText("npr. 46.05695")

        # Dovoljene vrednosti (lon: -180..180, lat: -90..90)
        lon_validator = QDoubleValidator(-180.0, 180.0, 8)
        lat_validator = QDoubleValidator(-90.0, 90.0, 8)
        self._lon_edit.setValidator(lon_validator)
        self._lat_edit.setValidator(lat_validator)

        form.addRow(QLabel("Longitude (X) [WGS84]:"), self._lon_edit)
        form.addRow(QLabel("Latitude (Y) [WGS84]:"), self._lat_edit)
        vbox.addLayout(form)

        # Izbira obstoječega točkovnega sloja
        self._layers_combo = QComboBox()
        self._layers_combo.setToolTip("Izberi točkovni sloj, kamor želiš dodati točko.")
        vbox.addWidget(QLabel("Obstoječi točkovni sloj:"))
        vbox.addWidget(self._layers_combo)

        # Gumbi
        btn_row = QHBoxLayout()
        create_btn = QPushButton("Create point layer")
        add_btn = QPushButton("Add point to existing layer")
        btn_row.addWidget(create_btn)
        btn_row.addWidget(add_btn)
        vbox.addLayout(btn_row)

        # Povezave
        create_btn.clicked.connect(self._on_create_layer)
        add_btn.clicked.connect(self._on_add_point)

        # Zaključi
        container.setLayout(vbox)
        self._dock.setWidget(container)

        # Napolni seznam slojev
        self._populate_layers_combo()

    def _toggle_dock(self, checked):
        if not self._dock:
            return
        self._dock.setVisible(checked)

    # ----------------------------
    # Logika
    # ----------------------------
    def _parse_inputs(self):
        """Vrne (lon, lat) kot float ali sproži ValueError."""
        lon_text = (self._lon_edit.text() or "").strip().replace(",", ".")
        lat_text = (self._lat_edit.text() or "").strip().replace(",", ".")
        if lon_text == "" or lat_text == "":
            raise ValueError("Vnesi obe vrednosti: longitude in latitude.")
        lon = float(lon_text)
        lat = float(lat_text)
        if lon < -180 or lon > 180 or lat < -90 or lat > 90:
            raise ValueError("Koordinate izven obsega: lon ∈ [-180, 180], lat ∈ [-90, 90].")
        return lon, lat

    def _populate_layers_combo(self, *args, **kwargs):
        """Napolni combobox s točkovnimi vektorskimi sloji v projektu."""
        if not self._layers_combo:
            return
        self._layers_combo.blockSignals(True)
        self._layers_combo.clear()
        project = QgsProject.instance()
        for layer in project.mapLayers().values():
            try:
                if hasattr(layer, "geometryType") and layer.geometryType() == QgsWkbTypes.PointGeometry:
                    self._layers_combo.addItem(layer.name(), layer.id())
            except Exception:
                continue
        self._layers_combo.blockSignals(False)

    def _on_create_layer(self):
        """Ustvari nov scratch (memory) točkovni sloj v EPSG:4326 in ga doda v projekt."""
        layer_name = "AddPoint_Scratch"
        uri = "Point?crs=EPSG:4326"
        mem_layer = QgsVectorLayer(uri, layer_name, "memory")
        if not mem_layer or not mem_layer.isValid():
            self._message("Neuspešna tvorba memory sloja.", level="critical")
            return

        QgsProject.instance().addMapLayer(mem_layer)
        self._message(f"Ustvarjen nov scratch sloj: {layer_name}", level="info")
        # Osveži in izberi pravkar ustvarjen sloj
        self._populate_layers_combo()
        idx = self._layers_combo.findText(layer_name)
        if idx >= 0:
            self._layers_combo.setCurrentIndex(idx)

    def _on_add_point(self):
        """Doda vneseno WGS84 točko v izbran obstoječi točkovni sloj (s transformacijo v CRS sloja)."""
        # Preberi koordinate
        try:
            lon, lat = self._parse_inputs()
        except Exception as ex:
            self._message(str(ex), level="warning")
            return

        # Dobi ciljni sloj
        idx = self._layers_combo.currentIndex()
        if idx < 0:
            self._message("Ni izbranega točkovnega sloja.", level="warning")
            return
        layer_id = self._layers_combo.itemData(idx)
        layer = QgsProject.instance().mapLayer(layer_id)
        if layer is None:
            self._message("Izbrani sloj ne obstaja več.", level="warning")
            self._populate_layers_combo()
            return

        # Preveri geometrijo
        if not hasattr(layer, "geometryType") or layer.geometryType() != QgsWkbTypes.PointGeometry:
            self._message("Izbrani sloj ni točkovni sloj.", level="warning")
            return

        # Pripravi geometrijo v CRS sloja (transformacija iz WGS84)
        src_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        dst_crs = layer.crs()
        try:
            xform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())
            pt_dst = xform.transform(QgsPointXY(lon, lat))
        except Exception as ex:
            self._message(f"Neuspešna transformacija koordinat: {ex}", level="critical")
            return

        feat = QgsFeature(layer.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(pt_dst))

        # Dodajanje v sloj (z urejanjem, če je potrebno)
        must_commit = False
        if not layer.isEditable():
            if not layer.startEditing():
                self._message("Sloja ni možno dati v urejanje.", level="critical")
                return
            must_commit = True

        ok = layer.addFeature(feat)
        if not ok:
            self._message("Dodajanje točke je spodletelo.", level="critical")
            if must_commit:
                layer.rollBack()
            return

        if must_commit:
            if not layer.commitChanges():
                self._message("Shranjevanje sprememb je spodletelo.", level="critical")
                layer.rollBack()
                return

        self._message(f"Točka dodana v sloj: {layer.name()}", level="info")
        layer.triggerRepaint()

    # ----------------------------
    # Pomožne metode
    # ----------------------------
    def _message(self, text, level="info", duration=4):
        bar = self.iface.messageBar()
        from qgis.core import Qgis
        levels = {
            "info": Qgis.Info,
            "warning": Qgis.Warning,
            "critical": Qgis.Critical
        }
        bar.pushMessage("AddPoint", text, level=levels.get(level, Qgis.Info), duration=duration)
