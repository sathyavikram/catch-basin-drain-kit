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
    


    # Slots pattern
    slot_x_len = 30.0
    slot_y_len = 12.0
    rib_thickness = GRATE_RIB_THICKNESS
    
    row_step_y = slot_y_len + rib_thickness
    col_step_x = slot_x_len + rib_thickness
    
    cut_bodies = []
    
    start_x = rib_thickness * 2
    start_y = rib_thickness * 2
    max_x = grate_size - rib_thickness * 2
    max_y = grate_size - rib_thickness * 2
    
    y = start_y
    row_idx = 0
    while y + slot_y_len <= max_y:
        x_offset = start_x
        if row_idx % 2 == 1:
            x_offset += col_step_x / 2.0
            
        x = x_offset
        while x + slot_x_len <= max_x:
            slot = Part.makeBox(slot_x_len, slot_y_len, GRATE_THICKNESS * 3)
            slot.translate(FreeCAD.Vector(x, y, -GRATE_THICKNESS))
            cut_bodies.append(slot)
            x += col_step_x
            
        # Edge half-slots for the odd rows
        if row_idx % 2 == 1:
            left_len = col_step_x / 2.0 - rib_thickness
            if left_len > 0:
                slot_left = Part.makeBox(left_len, slot_y_len, GRATE_THICKNESS * 3)
                slot_left.translate(FreeCAD.Vector(start_x, y, -GRATE_THICKNESS))
                cut_bodies.append(slot_left)
                
            right_len = max_x - x
            if right_len > rib_thickness:
                slot_right = Part.makeBox(right_len, slot_y_len, GRATE_THICKNESS * 3)
                slot_right.translate(FreeCAD.Vector(x, y, -GRATE_THICKNESS))
                cut_bodies.append(slot_right)

        y += row_step_y
        row_idx += 1
        
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
