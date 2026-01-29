# -*- coding: utf-8 -*-
import re
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QDoubleValidator
from qgis.PyQt.QtWidgets import (
    QAction, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox
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
    QgsMessageLog,
    Qgis,
    edit,
    QgsMapLayerProxyModel
)

from qgis.gui import QgsMapLayerComboBox

LANG = {
    'sl': {
        'plugin_title': 'AddPoint',
        'toggle_lang': 'SLO/EN',
        'format_label': 'Format / vnosni CRS:',
        'format_dd': 'WGS84: Decimalne stopinje (DD)',
        'format_ddm': 'WGS84: Stopinje in decimalne minute (DDM)',
        'format_dms': 'WGS84: Stopinje, minute in sekunde (DMS)',
        'format_3794': 'D96/TM – Slovenija (EPSG:3794, metri)',
        'format_3857': 'Web Mercator (EPSG:3857, metri)',
        'format_utm': 'UTM',

        # Vnosni način
        'input_mode_single': 'Vnos v enem polju (E N)',
        'single_label': 'Koordinate:',
        'single_order_label': 'Vrstni red:',
        'single_order_en': 'E N',
        'single_order_ne': 'N E',

        # Labele: samo E in N
        'e_label': 'E:',
        'n_label': 'N:',

        # UTM zona
        'utm_zone_label': 'UTM cona:',

        'btn_swap': 'Zamenjaj E ↔ N',
        'existing_layer_label': 'Obstoječi točkovni sloj:',
        'btn_refresh_layers': 'Osveži seznam slojev',
        'chk_add_after': 'Po ustvarjanju sloja takoj dodaj vneseno točko',
        'btn_create': 'Ustvari točkovni sloj',
        'btn_add': 'Dodaj točko v obstoječi sloj',
        'msg_layer_created': 'Ustvarjen nov scratch sloj: {name}',

        'warn_enter_both': 'Vnesi obe vrednosti (E in N).',
        'warn_enter_two_single': 'Vnesi dve vrednosti v enem polju (npr. "E N" ali "N E").',

        'warn_no_point_layer': 'Ni izbranega točkovnega sloja.',
        'warn_not_point_layer': 'Izbrani sloj ni točkovni vektorski sloj.',
        'warn_range_lon': 'Longitude izven obsega [-180, 180].',
        'warn_range_lat': 'Latitude izven obsega [-90, 90].',

        'err_invalid_numeric_metric': 'Pričakovani numerični vrednosti.',
        'warn_values_outside_3794': 'Opozorilo: vnesene vrednosti EPSG:3794 (E={x}, N={y}) so izven tipičnega območja.',
        'warn_values_outside_3857': 'Opozorilo: vnesene vrednosti EPSG:3857 (E={x}, N={y}) so izven tipičnega območja.',
        'warn_values_outside_utm': 'Opozorilo: vnesene UTM vrednosti (E={x}, N={y}) so izven tipičnega območja.',

        'warn_parse_dd': 'Pričakovan format DD: npr. 14.50597 ali -14.50597',
        'warn_parse_ddm': 'Pričakovan format DDM: stopinje minute.dec (npr. 14 30.3582 E)',
        'warn_parse_dms': 'Pričakovan format DMS: stopinje minute sekunde (npr. 14 30 21.5 E)',
        'err_transform': 'Neuspešna transformacija koordinat: {err}',
        'err_add_feature': 'Dodajanje točke je spodletelo.',
        'msg_point_added': 'Točka dodana v sloj: {layer}',
        'err_mem_layer': 'Neuspešna tvorba memory sloja.'
    },
    'en': {
        'plugin_title': 'AddPoint',
        'toggle_lang': 'SLO/EN',
        'format_label': 'Format / input CRS:',
        'format_dd': 'WGS84: Decimal degrees (DD)',
        'format_ddm': 'WGS84: Degrees and decimal minutes (DDM)',
        'format_dms': 'WGS84: Degrees, minutes and seconds (DMS)',
        'format_3794': 'D96/TM – Slovenia (EPSG:3794, meters)',
        'format_3857': 'Web Mercator (EPSG:3857, meters)',
        'format_utm': 'UTM',

        # Input mode
        'input_mode_single': 'Single-field input',
        'single_label': 'Coordinates:',
        'single_order_label': 'Order:',
        'single_order_en': 'E N',
        'single_order_ne': 'N E',

        # Labels: E and N only
        'e_label': 'E:',
        'n_label': 'N:',

        # UTM zone
        'utm_zone_label': 'UTM zone:',

        'btn_swap': 'Swap E ↔ N',
        'existing_layer_label': 'Existing point layer:',
        'btn_refresh_layers': 'Refresh layer list',
        'chk_add_after': 'After creating layer, immediately add the entered point',
        'btn_create': 'Create point layer',
        'btn_add': 'Add point to existing layer',
        'msg_layer_created': 'Created new scratch layer: {name}',

        'warn_enter_both': 'Enter both values (E and N).',
        'warn_enter_two_single': 'Enter two values in one field (e.g. "E N" or "N E").',

        'warn_no_point_layer': 'No point layer selected.',
        'warn_not_point_layer': 'The selected layer is not a point vector layer.',
        'warn_range_lon': 'Longitude out of range [-180, 180].',
        'warn_range_lat': 'Latitude out of range [-90, 90].',

        'err_invalid_numeric_metric': 'Expected numeric values.',
        'warn_values_outside_3794': 'Warning: EPSG:3794 values (E={x}, N={y}) are outside typical range.',
        'warn_values_outside_3857': 'Warning: EPSG:3857 values (E={x}, N={y}) are outside typical range.',
        'warn_values_outside_utm': 'Warning: UTM values (E={x}, N={y}) are outside typical range.',

        'warn_parse_dd': 'Expected DD format: e.g. 14.50597 or -14.50597',
        'warn_parse_ddm': 'Expected DDM format: degrees minutes.dec (e.g. 14 30.3582 E)',
        'warn_parse_dms': 'Expected DMS format: degrees minutes seconds (e.g. 14 30 21.5 E)',
        'err_transform': 'Coordinate transformation failed: {err}',
        'err_add_feature': 'Adding point failed.',
        'msg_point_added': 'Point added to layer: {layer}',
        'err_mem_layer': 'Failed to create memory layer.'
    }
}


class AddPointPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self._dock = None
        self._action = None
        self._layers_combo = None

        # Two-field inputs (E, N)
        self._lon_edit = None  # E
        self._lat_edit = None  # N
        self._x_label = None
        self._y_label = None

        # Single-field input
        self._single_mode_chk = None
        self._one_label = None
        self._one_edit = None
        self._single_order_label = None
        self._single_order_combo = None

        # UTM zone dropdown
        self._utm_zone_label = None
        self._utm_zone_combo = None

        self._format_combo = None
        self._add_to_new_after_create = None
        self._btn_create = None
        self._btn_add = None
        self._btn_swap = None
        self._btn_refresh = None
        self._fmt_label = None
        self._existing_label = None
        self._lang_btn = None
        self._lang = 'sl'  # default Slovenian

    # ----------------------------
    # QGIS lifecycle
    # ----------------------------
    def initGui(self):
        self._action = QAction("AddPoint panel", self.iface.mainWindow())
        self._action.setCheckable(True)
        self._action.setChecked(True)
        self._action.triggered.connect(self._toggle_dock)

        self.iface.addPluginToMenu("AddPoint", self._action)
        self.iface.addToolBarIcon(self._action)

        self._create_dock()
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self._dock)
        self._action.setChecked(True)

    def unload(self):
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
        self._dock = QDockWidget(LANG[self._lang]['plugin_title'], self.iface.mainWindow())
        self._dock.setObjectName("AddPointDock")
        self._dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        container = QWidget(self._dock)
        vbox = QVBoxLayout(container)

        # Top row: language + format
        top_row = QHBoxLayout()
        self._lang_btn = QPushButton(LANG[self._lang]['toggle_lang'])
        self._lang_btn.setToolTip('SLO/EN')
        self._lang_btn.clicked.connect(self._toggle_language)
        top_row.addWidget(self._lang_btn)

        self._fmt_label = QLabel(LANG[self._lang]['format_label'])
        self._format_combo = QComboBox()
        self._rebuild_format_combo()
        self._format_combo.currentIndexChanged.connect(self._on_format_changed)
        top_row.addWidget(self._fmt_label)
        top_row.addWidget(self._format_combo)
        vbox.addLayout(top_row)

        # Input mode checkbox
        self._single_mode_chk = QCheckBox()
        self._single_mode_chk.stateChanged.connect(self._on_input_mode_changed)
        vbox.addWidget(self._single_mode_chk)

        # UTM zone row (only visible when UTM)
        utm_row = QHBoxLayout()
        self._utm_zone_label = QLabel()
        self._utm_zone_combo = QComboBox()
        self._build_utm_zone_combo()
        utm_row.addWidget(self._utm_zone_label)
        utm_row.addWidget(self._utm_zone_combo)
        vbox.addLayout(utm_row)

        # Single-field order row (only visible when single-field)
        order_row = QHBoxLayout()
        self._single_order_label = QLabel()
        self._single_order_combo = QComboBox()
        order_row.addWidget(self._single_order_label)
        order_row.addWidget(self._single_order_combo)
        vbox.addLayout(order_row)

        # Coordinate inputs
        form = QFormLayout()

        # Single-field widgets
        self._one_label = QLabel()
        self._one_edit = QLineEdit()
        form.addRow(self._one_label, self._one_edit)

        # Two-field widgets
        self._lon_edit = QLineEdit()
        self._lat_edit = QLineEdit()
        self._x_label = QLabel()
        self._y_label = QLabel()
        form.addRow(self._x_label, self._lon_edit)
        form.addRow(self._y_label, self._lat_edit)

        vbox.addLayout(form)

        # Swap button (two-field only)
        swap_row = QHBoxLayout()
        self._btn_swap = QPushButton()
        self._btn_swap.clicked.connect(self._on_swap_values)
        swap_row.addWidget(self._btn_swap)
        vbox.addLayout(swap_row)

        # Layer selection
        self._existing_label = QLabel()
        vbox.addWidget(self._existing_label)
        self._layers_combo = QgsMapLayerComboBox()
        self._layers_combo.setFilters(QgsMapLayerProxyModel.PointLayer)
        self._layers_combo.setAllowEmptyLayer(True)
        vbox.addWidget(self._layers_combo)

        # Refresh layers
        refresh_row = QHBoxLayout()
        self._btn_refresh = QPushButton()
        self._btn_refresh.clicked.connect(self._refresh_layers_combo)
        refresh_row.addWidget(self._btn_refresh)
        vbox.addLayout(refresh_row)

        # Checkbox: add after create
        self._add_to_new_after_create = QCheckBox()
        self._add_to_new_after_create.setChecked(True)
        vbox.addWidget(self._add_to_new_after_create)

        # Action buttons
        btn_row = QHBoxLayout()
        self._btn_create = QPushButton()
        self._btn_add = QPushButton()
        self._btn_create.clicked.connect(self._on_create_layer)
        self._btn_add.clicked.connect(self._on_add_point)
        btn_row.addWidget(self._btn_create)
        btn_row.addWidget(self._btn_add)
        vbox.addLayout(btn_row)

        # Apply localization + visibility + validators
        self._apply_localization()
        self._on_format_changed(self._format_combo.currentIndex())
        self._on_input_mode_changed()

        container.setLayout(vbox)
        self._dock.setWidget(container)

    def _rebuild_format_combo(self):
        current_code = self._format_combo.currentData() if self._format_combo.count() > 0 else 'DD'
        self._format_combo.blockSignals(True)
        self._format_combo.clear()
        self._format_combo.addItem(LANG[self._lang]['format_dd'], userData='DD')
        self._format_combo.addItem(LANG[self._lang]['format_ddm'], userData='DDM')
        self._format_combo.addItem(LANG[self._lang]['format_dms'], userData='DMS')
        self._format_combo.addItem(LANG[self._lang]['format_3794'], userData='EPSG:3794')
        self._format_combo.addItem(LANG[self._lang]['format_3857'], userData='EPSG:3857')
        self._format_combo.addItem(LANG[self._lang]['format_utm'], userData='UTM')

        idx = 0
        for i in range(self._format_combo.count()):
            if self._format_combo.itemData(i) == current_code:
                idx = i
                break
        self._format_combo.setCurrentIndex(idx)
        self._format_combo.blockSignals(False)

    def _build_utm_zone_combo(self):
        self._utm_zone_combo.blockSignals(True)
        self._utm_zone_combo.clear()

        for z in range(1, 61):
            epsg = f"EPSG:{32600 + z}"
            self._utm_zone_combo.addItem(f"{z:02d}N ({epsg})", userData=epsg)

        for z in range(1, 61):
            epsg = f"EPSG:{32700 + z}"
            self._utm_zone_combo.addItem(f"{z:02d}S ({epsg})", userData=epsg)

        # default: 33N
        default_epsg = "EPSG:32633"
        for i in range(self._utm_zone_combo.count()):
            if self._utm_zone_combo.itemData(i) == default_epsg:
                self._utm_zone_combo.setCurrentIndex(i)
                break

        self._utm_zone_combo.blockSignals(False)

    def _rebuild_single_order_combo(self):
        """
        Single-field order dropdown:
          - E N (default)
          - N E (Google Maps style)
        userData: 'EN' or 'NE'
        """
        L = LANG[self._lang]
        self._single_order_combo.blockSignals(True)
        current = self._single_order_combo.currentData() if self._single_order_combo.count() > 0 else 'EN'
        self._single_order_combo.clear()
        self._single_order_combo.addItem(L['single_order_en'], userData='EN')
        self._single_order_combo.addItem(L['single_order_ne'], userData='NE')
        # restore selection
        idx = 0
        for i in range(self._single_order_combo.count()):
            if self._single_order_combo.itemData(i) == current:
                idx = i
                break
        self._single_order_combo.setCurrentIndex(idx)
        self._single_order_combo.blockSignals(False)

    def _apply_localization(self):
        L = LANG[self._lang]
        self._dock.setWindowTitle(L['plugin_title'])
        if self._action:
            self._action.setText(f"{L['plugin_title']} panel")
        self._fmt_label.setText(L['format_label'])
        self._btn_swap.setText(L['btn_swap'])
        self._existing_label.setText(L['existing_layer_label'])
        self._btn_refresh.setText(L['btn_refresh_layers'])
        self._add_to_new_after_create.setText(L['chk_add_after'])
        self._btn_create.setText(L['btn_create'])
        self._btn_add.setText(L['btn_add'])

        self._single_mode_chk.setText(L['input_mode_single'])
        self._one_label.setText(L['single_label'])

        self._utm_zone_label.setText(L['utm_zone_label'])
        self._single_order_label.setText(L['single_order_label'])
        self._rebuild_single_order_combo()

        self._set_labels_and_placeholders(self._current_format())
        self._rebuild_format_combo()

    def _toggle_language(self):
        self._lang = 'en' if self._lang == 'sl' else 'sl'
        self._apply_localization()

    def _refresh_layers_combo(self):
        current = self._layers_combo.currentLayer()
        self._layers_combo.setFilters(QgsMapLayerProxyModel.PointLayer)
        if current is not None:
            try:
                self._layers_combo.setLayer(current)
            except Exception:
                pass

    def _on_input_mode_changed(self):
        single = self._single_mode_chk.isChecked()

        # show/hide single-field controls
        self._one_label.setVisible(single)
        self._one_edit.setVisible(single)

        self._single_order_label.setVisible(single)
        self._single_order_combo.setVisible(single)

        # show/hide two-field controls
        self._x_label.setVisible(not single)
        self._lon_edit.setVisible(not single)
        self._y_label.setVisible(not single)
        self._lat_edit.setVisible(not single)

        self._btn_swap.setEnabled(not single)
        self._btn_swap.setVisible(not single)

        self._apply_validators()

    def _apply_validators(self):
        fmt = self._current_format()
        single = self._single_mode_chk.isChecked()

        if single:
            # free-form (two numbers in one field)
            self._one_edit.setValidator(None)
            return

        if fmt == 'DD':
            e_validator = QDoubleValidator(-180.0, 180.0, 8)
            n_validator = QDoubleValidator(-90.0, 90.0, 8)
            self._lon_edit.setValidator(e_validator)  # E
            self._lat_edit.setValidator(n_validator)  # N
        elif fmt in ('DDM', 'DMS'):
            self._lon_edit.setValidator(None)
            self._lat_edit.setValidator(None)
        else:
            metric_validator = QDoubleValidator(-1e8, 1e8, 3)
            self._lon_edit.setValidator(metric_validator)
            self._lat_edit.setValidator(metric_validator)

    def _set_labels_and_placeholders(self, fmt):
        L = LANG[self._lang]
        self._x_label.setText(L['e_label'])
        self._y_label.setText(L['n_label'])

        # Remove placeholders/hints
        self._lon_edit.setPlaceholderText('')
        self._lat_edit.setPlaceholderText('')
        self._one_edit.setPlaceholderText('')

        self._apply_validators()

    def _on_format_changed(self, idx):
        fmt = self._current_format()
        self._set_labels_and_placeholders(fmt)

        is_utm = (fmt == 'UTM')
        self._utm_zone_label.setVisible(is_utm)
        self._utm_zone_combo.setVisible(is_utm)

        self._apply_validators()

    def _current_format(self):
        return self._format_combo.currentData()

    def _toggle_dock(self, checked):
        if self._dock:
            self._dock.setVisible(checked)

    # ----------------------------
    # Logic
    # ----------------------------
    def _on_swap_values(self):
        x = self._lon_edit.text()
        y = self._lat_edit.text()
        self._lon_edit.setText(y)
        self._lat_edit.setText(x)

    def _split_single_field(self, s: str):
        s = (s or '').strip()
        if not s:
            return None, None
        s = re.sub(r'[;,]', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        parts = s.split(' ')
        if len(parts) < 2:
            return None, None
        return parts[0].strip(), parts[1].strip()

    def _parse_inputs(self):
        L = LANG[self._lang]
        fmt = self._current_format()
        single = self._single_mode_chk.isChecked()

        if single:
            a_text, b_text = self._split_single_field(self._one_edit.text())
            if not a_text or not b_text:
                raise ValueError(L['warn_enter_two_single'])

            order = self._single_order_combo.currentData() or 'EN'
            # EN: first=E, second=N
            # NE: first=N, second=E (Google Maps style)
            if order == 'NE':
                x_text, y_text = b_text, a_text  # E = second, N = first
            else:
                x_text, y_text = a_text, b_text  # E = first, N = second
        else:
            x_text = (self._lon_edit.text() or '').strip()  # E
            y_text = (self._lat_edit.text() or '').strip()  # N
            if x_text == '' or y_text == '':
                raise ValueError(L['warn_enter_both'])

        if fmt in ('DD', 'DDM', 'DMS'):
            lon = self._parse_angle(x_text, kind='lon', fmt=fmt)  # E
            lat = self._parse_angle(y_text, kind='lat', fmt=fmt)  # N
            if lon < -180 or lon > 180:
                raise ValueError(L['warn_range_lon'])
            if lat < -90 or lat > 90:
                raise ValueError(L['warn_range_lat'])
            return lon, lat, 'EPSG:4326'

        try:
            x = float(x_text.replace(',', '.'))
            y = float(y_text.replace(',', '.'))
        except Exception:
            raise ValueError(L['err_invalid_numeric_metric'])

        if fmt == 'EPSG:3794':
            if not (300000 <= x <= 800000 and 4000000 <= y <= 6000000):
                QgsMessageLog.logMessage(L['warn_values_outside_3794'].format(x=x, y=y), 'AddPoint', Qgis.Warning)
            return x, y, 'EPSG:3794'

        if fmt == 'EPSG:3857':
            if not (-20037508.3428 <= x <= 20037508.3428 and -20037508.3428 <= y <= 20037508.3428):
                QgsMessageLog.logMessage(L['warn_values_outside_3857'].format(x=x, y=y), 'AddPoint', Qgis.Warning)
            return x, y, 'EPSG:3857'

        if fmt == 'UTM':
            zone_epsg = self._utm_zone_combo.currentData() or "EPSG:32633"
            if not (100000 <= x <= 900000 and 0 <= y <= 10000000):
                QgsMessageLog.logMessage(L['warn_values_outside_utm'].format(x=x, y=y), 'AddPoint', Qgis.Warning)
            return x, y, zone_epsg

        return x, y, 'EPSG:4326'

    def _normalize_angle_text(self, s_up: str) -> str:
        s_up = (s_up
                .replace('’', "'")
                .replace('′', "'")
                .replace('“', '"')
                .replace('”', '"')
                .replace('″', '"'))
        s_up = re.sub(r"''", '"', s_up)
        s_up = s_up.replace('°', ' ').replace("'", ' ').replace('"', ' ')
        s_up = re.sub(r'[;:,]', ' ', s_up)
        s_up = re.sub(r'\s+', ' ', s_up).strip()
        return s_up

    def _parse_angle(self, text, kind='lon', fmt='DD'):
        L = LANG[self._lang]
        s_up = text.strip().upper().replace(',', '.')
        hemi_match = re.findall(r'[NSEW]', s_up)
        hemi = hemi_match[-1] if hemi_match else None
        s_up = re.sub(r'[NSEW]', '', s_up)
        s_up = self._normalize_angle_text(s_up)
        tokens = s_up.split()
        nums = []
        for t in tokens:
            try:
                nums.append(float(t))
            except Exception:
                pass

        if fmt == 'DD':
            if len(nums) < 1:
                raise ValueError(L['warn_parse_dd'])
            deg = nums[0]
            minutes = seconds = 0.0
        elif fmt == 'DDM':
            if len(nums) < 2:
                raise ValueError(L['warn_parse_ddm'])
            deg, minutes = nums[0], nums[1]
            seconds = 0.0
            if not (0 <= abs(minutes) < 60):
                raise ValueError('Minute [0, 60).')
        else:
            if len(nums) < 3:
                raise ValueError(L['warn_parse_dms'])
            deg, minutes, seconds = nums[0], nums[1], nums[2]
            if not (0 <= abs(minutes) < 60):
                raise ValueError('Minute [0, 60).')
            if not (0 <= abs(seconds) < 60):
                raise ValueError('Seconds [0, 60).')

        sign = 1
        if deg < 0:
            sign *= -1
            deg = abs(deg)
        if kind == 'lon' and hemi in ('W',):
            sign = -1
        if kind == 'lat' and hemi in ('S',):
            sign = -1
        if kind == 'lon' and hemi in ('E',):
            sign = +1 if sign > 0 else -1
        if kind == 'lat' and hemi in ('N',):
            sign = +1 if sign > 0 else -1

        value = deg + (abs(minutes) / 60.0) + (abs(seconds) / 3600.0)
        value *= sign

        max_deg = 180 if kind == 'lon' else 90
        if deg > max_deg or (deg == max_deg and (abs(minutes) > 0 or abs(seconds) > 0)):
            raise ValueError('Degrees exceed allowed bounds.')
        return value

    def _on_create_layer(self):
        L = LANG[self._lang]
        try:
            layer_name = 'AddPoint_Scratch'
            mem_layer = QgsVectorLayer('Point?crs=EPSG:4326', layer_name, 'memory')
            if not mem_layer or not mem_layer.isValid():
                raise RuntimeError(L['err_mem_layer'])
            QgsProject.instance().addMapLayer(mem_layer)
            self._message(L['msg_layer_created'].format(name=layer_name), level='info')
            if self._add_to_new_after_create.isChecked():
                self._on_add_point(target_layer=mem_layer)
        except Exception as ex:
            self._message(str(ex), level='critical')
            QgsMessageLog.logMessage(f"_on_create_layer exception: {ex}", 'AddPoint', Qgis.Critical)

    def _on_add_point(self, target_layer=None):
        L = LANG[self._lang]
        try:
            x, y, src_epsg = self._parse_inputs()
        except Exception as ex:
            self._message(str(ex), level='warning')
            QgsMessageLog.logMessage(f"Parse inputs failed: {ex}", 'AddPoint', Qgis.Warning)
            return

        layer = target_layer or self._layers_combo.currentLayer()
        if layer is None:
            self._message(L['warn_no_point_layer'], level='warning')
            return

        if not isinstance(layer, QgsVectorLayer) or layer.geometryType() != QgsWkbTypes.PointGeometry:
            self._message(L['warn_not_point_layer'], level='warning')
            return

        try:
            src_crs = QgsCoordinateReferenceSystem(src_epsg)
            dst_crs = layer.crs()
            xform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())
            pt_dst = xform.transform(QgsPointXY(x, y))
        except Exception as ex:
            self._message(L['err_transform'].format(err=ex), level='critical')
            QgsMessageLog.logMessage(f"Transform failed: {ex}", 'AddPoint', Qgis.Critical)
            return

        try:
            feat = QgsFeature(layer.fields())
            feat.setGeometry(QgsGeometry.fromPointXY(pt_dst))
            with edit(layer):
                ok = layer.addFeature(feat)
                if not ok:
                    raise RuntimeError(L['err_add_feature'])
        except Exception as ex:
            self._message(str(ex), level='critical')
            QgsMessageLog.logMessage(f"Add feature failed: {ex}", 'AddPoint', Qgis.Critical)
            return

        self._message(L['msg_point_added'].format(layer=layer.name()), level='info')
        try:
            layer.triggerRepaint()
        except Exception:
            pass

    def _message(self, text, level='info', duration=5):
        bar = self.iface.messageBar()
        levels = {"info": Qgis.Info, "warning": Qgis.Warning, "critical": Qgis.Critical}
        bar.pushMessage('AddPoint', text, level=levels.get(level, Qgis.Info), duration=duration)
        QgsMessageLog.logMessage(text, 'AddPoint', levels.get(level, Qgis.Info))
