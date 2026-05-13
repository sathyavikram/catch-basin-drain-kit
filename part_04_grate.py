import FreeCAD
import Part
import math
import os
import sys

try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
except NameError:
    pass


from config import *

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_BASE = os.path.join(CURRENT_DIR, "exports")
EXPORT_STEP = os.path.join(EXPORT_BASE, "part_04_grate.step")
EXPORT_STL = os.path.join(EXPORT_BASE, "part_04_grate.stl")

def create_grate():
    def make_rounded_box(l, w, h, radius=2.0):
        import Part
        box = Part.makeBox(l, w, h)
        try: box = box.makeFillet(radius, box.Edges)
        except: pass
        return box

    # Base solid (sits in the lip_box cutout)
    grate_size = BASIN_SIZE - WALL_THICKNESS - 1.0  # 1mm tolerance clearance
    grate_body = make_rounded_box(grate_size, grate_size, GRATE_THICKNESS/2.0, 2.0)
    grate_body.translate(FreeCAD.Vector(0, 0, GRATE_THICKNESS/2.0))
    
    # Bottom lip to sit strictly inside the hollow basin wall
    inner_lip = make_rounded_box(
        BASIN_SIZE - 2*WALL_THICKNESS - 1.5, 
        BASIN_SIZE - 2*WALL_THICKNESS - 1.5, 
        GRATE_THICKNESS/2.0,
        2.0
    )
    inner_lip.translate(FreeCAD.Vector(
        (grate_size - (BASIN_SIZE - 2*WALL_THICKNESS - 1.5))/2,
        (grate_size - (BASIN_SIZE - 2*WALL_THICKNESS - 1.5))/2,
        0
    ))
    
    # Fuse them so we have the full solid block first
    grate_body = grate_body.fuse(inner_lip)
    


    # Slots pattern: Dynamic Full Holes
    rib_thickness = GRATE_RIB_THICKNESS
    margin = rib_thickness * 1.5
    avail = grate_size - 2 * margin
    
    cols = 4  # 4 slots wide
    rows = 7  # 7 slots high
    
    # Calculate exact safe sizing for full un-cut holes
    slot_x = (avail - (cols - 1) * rib_thickness) / cols
    slot_y = (avail - (rows - 1) * rib_thickness) / rows
    
    cut_bodies = []
    
    for r in range(rows):
        for c in range(cols):
            x = margin + c * (slot_x + rib_thickness)
            y = margin + r * (slot_y + rib_thickness)
            
            slot = Part.makeBox(slot_x, slot_y, GRATE_THICKNESS * 3)
            try:
                slot = slot.makeFillet(2.0, slot.Edges)
            except: pass
            
            slot.translate(FreeCAD.Vector(x, y, -GRATE_THICKNESS))
            cut_bodies.append(slot)
        
    if cut_bodies:
        compound_cut = Part.makeCompound(cut_bodies)
        grate_body = grate_body.cut(compound_cut)
    
    os.makedirs(EXPORT_BASE, exist_ok=True)
    grate_body.exportStep(EXPORT_STEP)
    grate_body.exportStl(EXPORT_STL)
    print(f"Exported Grate to {EXPORT_STEP} and {EXPORT_STL}")
    
    return grate_body
def main():
    doc = FreeCAD.newDocument("part_04_grate")
    obj = doc.addObject("Part::Feature", "Grate")
    obj.Shape = create_grate()
    doc.recompute()

if __name__ == '__main__':
    main()
