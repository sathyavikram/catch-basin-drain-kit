import FreeCAD
import Part
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_BASE = os.path.join(CURRENT_DIR, "exports")
IMPORTS_BASE = os.path.join(CURRENT_DIR, "exports")

def export_test_pieces():
    os.makedirs(EXPORT_BASE, exist_ok=True)
    
    # --- 1. Adapter Thread Section ---
    print("Loading full adapter from STEP...")
    adapter_shape = Part.Shape()
    adapter_shape.read(os.path.join(IMPORTS_BASE, "part_02_outlet_adapter.step"))
    
    # The adapter goes from approx Z=-24 to Z=84. 
    # We will keep from Z=-40 to Z=25 to give a small grip but cut off the long tube
    box_adapter = Part.makeBox(200, 200, 65)
    box_adapter.translate(FreeCAD.Vector(-100, -100, -40))
    adapter_test = adapter_shape.common(box_adapter)
    
    adapter_stl = os.path.join(EXPORT_BASE, "test_adapter_threads.stl")
    adapter_step = os.path.join(EXPORT_BASE, "test_adapter_threads.step")
    adapter_test.exportStl(adapter_stl)
    adapter_test.exportStep(adapter_step)
    print(f"Exported Adapter Test Piece to {adapter_stl}")
    
    # --- 2. Basin Collar Thread Section ---
    print("Loading full basin from STEP...")
    basin_shape = Part.Shape()
    basin_shape.read(os.path.join(IMPORTS_BASE, "part_01_catch_basin.step"))
    
    # We want just the collar at X=0
    # From config: BASIN_SIZE = 130.0, OUTLET_HEIGHT_OFFSET = 25.0, OUTLET_DIAMETER = 106.0
    y_center = 130.0 / 2
    z_center = 25.0 + 106.0 / 2
    
    # Make a box around this collar. X from -30 up to +20 inside basin.
    # Y and Z giving about 140x140 square face.
    box_basin = Part.makeBox(50, 140, 140)
    box_basin.translate(FreeCAD.Vector(-30, y_center - 70, z_center - 70))
    basin_test = basin_shape.common(box_basin)
    
    basin_stl = os.path.join(EXPORT_BASE, "test_basin_collar.stl")
    basin_step = os.path.join(EXPORT_BASE, "test_basin_collar.step")
    basin_test.exportStl(basin_stl)
    basin_test.exportStep(basin_step)
    print(f"Exported Basin Collar Test Piece to {basin_stl}")
    
    # For visualization in MCP
    doc = FreeCAD.newDocument("TestPieces")
    
    # Offset the basin test so they don't overlap in visualization
    basin_test.translate(FreeCAD.Vector(100, 0, 0))
    
    doc.addObject("Part::Feature", "Adapter_Test").Shape = adapter_test
    doc.addObject("Part::Feature", "Basin_Test").Shape = basin_test
    doc.recompute()

if __name__ in ['__main__', '__builtin__', 'export_thread_test_pieces']:
    export_test_pieces()
