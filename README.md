<img width="768" height="512" alt="image" src="https://github.com/user-attachments/assets/56a81d9c-d43b-4edf-bbd6-d17b79b6400f" />

# AddPoint – Create Vector Layers from Coordinates (DD / DDM / DMS / EPSG:3794)

AddPoint is designed for everyday users who need the simplest possible way to create a point from a coordinate.
Instead of dealing with complex dialogs or coordinate conversions, the plugin provides a clean, intuitive panel where the user simply enters a coordinate — in any common format — and instantly creates a point or an entire vector layer.
AddPoint removes technical barriers and helps users who are not GIS experts quickly place accurate locations on the map, regardless of their familiarity with coordinate systems.

---
## Key Features

### Create vector layers directly from coordinates
- Instantly generate a new **scratch point layer** from any coordinate input.
- Layer is created in **EPSG:4326**, with the option to immediately insert the provided coordinate.
- Points can be added to **any existing point layer** as well.

### Multiple coordinate formats
- **DD** – Decimal Degrees (e.g. `46.05695`, `14.50597`)
- **DDM** – Degrees and Decimal Minutes (e.g. `14 30.3582 E`, `46°3.417′ N`)
- **DMS** – Degrees, Minutes, Seconds (e.g. `45°34′57.1″ N`, `13°51′55.6″ E`)
- **EPSG:3794** – D96/TM (Slovenian national grid, meters)

The parser accepts a wide range of symbols (° ′ ″ ’ '') and normalizes them automatically.

### Automatic CRS Transformation
- DD / DDM / DMS → always interpreted as **EPSG:4326 (WGS84)**.
- EPSG:3794 (meters) → **D96/TM Slovenia**.
- Coordinates are always transformed to the CRS of the selected target layer.

### SLO/EN language switch
A single **SLO/EN** button updates all labels, tooltips, placeholders, warnings, errors, and messages.

### Reliable point‑layer selection
- Uses `QgsMapLayerComboBox` and `QgsMapLayerProxyModel.PointLayer`.
- Shows only point layers.
- Includes a manual *Refresh layer list* button.

### Smart tools
- **Swap X ↔ Y** button
- Precision validators for each format
- Typical range check for EPSG:3794
- Clear QGIS Message Bar notifications

---
## Installation

1. Download the ZIP release.
2. Extract the folder `AddPoint` into your QGIS profile plugins directory:

**Windows**
```
%APPDATA%/QGIS/QGIS3/profiles/default/python/plugins/
```

**Linux**
```
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

3. Restart QGIS.
4. Enable the plugin in **Plugins → Manage and Install Plugins**.

---
## Usage

1. Open the *AddPoint* panel.
2. Choose the input format (DD / DDM / DMS / EPSG:3794).
3. Enter X and Y coordinates.
4. Select an existing point layer or create a new scratch layer.
5. Click **Create point layer** or **Add point to existing layer**.

---
## Requirements
- QGIS 3.16 or newer (tested on QGIS 3.40 LTR)

---
## License
MIT (or your chosen license).

---
