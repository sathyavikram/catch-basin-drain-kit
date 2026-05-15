import FreeCAD as App
import Part
import os
import sys

try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
except NameError:
    pass

import config
import importlib
importlib.reload(config)

from part_01_catch_basin import create_basin
from part_05_outlet_adapter_pvc import create_outlet_adapter
from part_03_plug import create_plug
from part_04_grate import create_grate

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_BASE = os.path.join(CURRENT_DIR, "exports")

def get_part_shape(construct_func, step_filename):
    step_path = os.path.join(EXPORT_BASE, step_filename)
    if os.path.exists(step_path):
        print(f"Loading {step_filename} from {EXPORT_BASE}...")
        shape = Part.Shape()
        shape.read(step_path)
        return shape
    else:
        print(f"Building {step_filename} from source...")
        return construct_func()

def main():
    doc = App.newDocument("Assembly")
    
    basin_shape = get_part_shape(create_basin, "part_01_catch_basin.step")
    adapter_shape = get_part_shape(create_outlet_adapter, "part_05_outlet_adapter_pvc.step")
    plug_shape = get_part_shape(create_plug, "part_03_plug.step")
    grate_shape = get_part_shape(create_grate, "part_04_grate.step")
    
    # Adapter placed on the X=-15 side (inserted into external threaded collar)
    adapter_shape.Placement = App.Placement(
        App.Vector(-20.0, config.BASIN_SIZE/2, config.OUTLET_HEIGHT_OFFSET + config.OUTLET_DIAMETER/2),
        App.Rotation(App.Vector(0,1,0), -90)
    )
    
    # Plug placed on the external collar
    plug_shape.Placement = App.Placement(
        App.Vector(config.BASIN_SIZE + 20.0, config.BASIN_SIZE/2, config.OUTLET_HEIGHT_OFFSET + config.OUTLET_DIAMETER/2),
        App.Rotation(App.Vector(0,1,0), 90)
    )

    # Grate placement
    grate_shape.Placement = App.Placement(App.Vector(
        config.WALL_THICKNESS/2.0 + 0.5,
        config.WALL_THICKNESS/2.0 + 0.5,
        config.BASIN_HEIGHT - config.GRATE_THICKNESS
    ), App.Rotation(App.Vector(0,0,1), 0))
    
    body1 = doc.addObject('App::Part', 'Part_Basin')
    p1 = doc.addObject("Part::Feature", "Shape_Basin")
    p1.Shape = basin_shape
    body1.addObject(p1)
    if p1.ViewObject: p1.ViewObject.ShapeColor = (0.2, 0.2, 0.2)
    
    body2 = doc.addObject('App::Part', 'Part_Adapter')
    p2 = doc.addObject("Part::Feature", "Shape_Adapter")
    p2.Shape = adapter_shape
    body2.addObject(p2)
    if p2.ViewObject: p2.ViewObject.ShapeColor = (0.1, 0.1, 0.1)
    
    body3 = doc.addObject('App::Part', 'Part_Grate')
    p3 = doc.addObject("Part::Feature", "Shape_Grate")
    p3.Shape = grate_shape
    body3.addObject(p3)
    if p3.ViewObject: p3.ViewObject.ShapeColor = (0.1, 0.5, 0.1)
    
    body4 = doc.addObject('App::Part', 'Part_Plug')
    p4 = doc.addObject("Part::Feature", "Shape_Plug")
    p4.Shape = plug_shape
    body4.addObject(p4)
    if p4.ViewObject: p4.ViewObject.ShapeColor = (0.2, 0.2, 0.2)
    
    os.makedirs(EXPORT_BASE, exist_ok=True)
    import Import
    Import.export([body1, body2, body3, body4], os.path.join(EXPORT_BASE, "assembly_pvc.step"))
    assembly_compound = Part.makeCompound([basin_shape, adapter_shape, grate_shape, plug_shape])
    assembly_compound.exportStl(os.path.join(EXPORT_BASE, "assembly_pvc.stl"))

if __name__ == "__main__" or __name__ in ("assembly", "assembly_pvc"):
    main()
