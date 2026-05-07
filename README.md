# 9-in Square Catch Basin Drain Kit

## Overview
This project contains parametric FreeCAD Python scripts to generate a generic 9-inch Square Catch Basin Drain Kit with a 2-opening catch basin. The models are designed to be fully parametric, robust, and 3D printable on standard FDM printers (256x256x256mm build volume at scale=1).

## Features
- **Catch Basin**: 9-inch square design with 2 keyed side openings and a bottom cutout guide.
- **Drain Pipe Compatibility**: Connects to standard 3-inch and 4-inch drain pipes for a soil-tight fit.
- **Components Included**:
  - Catch Basin Body
  - 2x Outlet Adapters (3-inch/4-inch compatible)
  - 1x Plug
  - Square Plastic Grate
- **Parametric Design**: All base dimensions, tolerances, and thicknesses are driven by a central `config.py` file and can be scaled easily using the `SCALE` parameter.

## Project Structure
- `config.py`: Contains all the parametric variables and dimensions.
- `part_01_catch_basin.py`: Script to generate the main catch basin solid.
- `part_02_outlet_adapter.py`: Script to generate the outlet adapter locking mechanisms.
- `part_03_plug.py`: Script to generate the plug for unused keyed openings.
- `part_04_grate.py`: Script to generate the top slotted grate.
- `assembly.py`: Script that imports all individual parts and positions them into a final assembled state.
- `export_all.py`: Utility script to orchestrate generating and exporting all parts, including the assembly.
- `exports/`: Directory where generated `.step` and `.stl` files are saved.

## How to Use
To generate the 3D models from the source code, simply execute the Python scripts using FreeCAD's Python environment. 

For example, to generate the full assembly:
```bash
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "import runpy; runpy.run_path('export_all.py', run_name='__main__')"
```
Alternatively, open any of the scripts directly within the FreeCAD GUI / Python console and run them to visualize the output and automatically export the STL and STEP files to the `exports/` folder.
