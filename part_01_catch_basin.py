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
EXPORT_STEP = os.path.join(EXPORT_BASE, "part_01_catch_basin.step")
EXPORT_STL = os.path.join(EXPORT_BASE, "part_01_catch_basin.stl")

def create_basin():
    # Outer box
    outer_box = Part.makeBox(BASIN_SIZE, BASIN_SIZE, BASIN_HEIGHT)
    try:
        outer_box = outer_box.makeFillet(5.0, outer_box.Edges)
    except: pass
    
    # Inner box (hollow)
    inner_box = Part.makeBox(
        BASIN_SIZE - 2*WALL_THICKNESS, 
        BASIN_SIZE - 2*WALL_THICKNESS, 
        BASIN_HEIGHT
    )
    try:
        inner_box = inner_box.makeFillet(3.0, inner_box.Edges)
    except: pass
    inner_box.translate(FreeCAD.Vector(WALL_THICKNESS, WALL_THICKNESS, WALL_THICKNESS))
    
    # Main body
    basin_body = outer_box.cut(inner_box)

    # Grate lip shelf cutoff
    lip_box = Part.makeBox(
        BASIN_SIZE - 2*(WALL_THICKNESS/2.0),
        BASIN_SIZE - 2*(WALL_THICKNESS/2.0),
        GRATE_THICKNESS / 2.0
    )
    try:
        lip_box = lip_box.makeFillet(2.0, lip_box.Edges)
    except: pass
    lip_box.translate(FreeCAD.Vector(WALL_THICKNESS/2.0, WALL_THICKNESS/2.0, BASIN_HEIGHT - (GRATE_THICKNESS / 2.0)))
    basin_body = basin_body.cut(lip_box)
    
    # Add external collars for threads
    import math
    def create_lofted_thread(nominal_radius, t_pitch, t_length, is_male, extra_clearance=THREAD_CLEARANCE):
        import math
        t_radius = nominal_radius
        if is_male:
            t_radius -= extra_clearance
            
        t_r_inner = t_radius - (t_pitch * 0.45)
        inner_X = t_r_inner - 2.0
        
        if is_male:
            p1 = FreeCAD.Vector(inner_X, 0, -t_pitch*0.35)
            p2 = FreeCAD.Vector(t_radius - 0.2, 0, -t_pitch*0.1)
            p3 = FreeCAD.Vector(t_radius - 0.2, 0,  t_pitch*0.1)
            p4 = FreeCAD.Vector(inner_X, 0,  t_pitch*0.35)
        else:
            p1 = FreeCAD.Vector(inner_X, 0, -t_pitch*0.35)
            p2 = FreeCAD.Vector(t_radius, 0, -t_pitch*0.1)
            p3 = FreeCAD.Vector(t_radius, 0,  t_pitch*0.1)
            p4 = FreeCAD.Vector(inner_X, 0,  t_pitch*0.35)
            
        t_wire = Part.Wire(Part.makePolygon([p1, p2, p3, p4, p1]))
        t_helix = Part.makeHelix(t_pitch, t_length, t_r_inner, 0)
        t_sweep = Part.Wire(t_helix).makePipeShell([t_wire], True, True)
        
        t_core = Part.makeCylinder(t_r_inner, t_length, FreeCAD.Vector(0,0,0))
        res = t_core.fuse(t_sweep)
        try: res = res.removeSplitter()
        except: pass
        return res

    y_center = BASIN_SIZE/2
    z_center = OUTLET_HEIGHT_OFFSET + OUTLET_DIAMETER/2
    
    # Outer collars
    collar_len = 20.0
    collar_outer = OUTLET_DIAMETER/2 + WALL_THICKNESS + 5.0
    
    collar1 = Part.makeCylinder(collar_outer, collar_len)
    # Z points inward when adapter is rotated, wait
    # adapter is rotated -90 around Y. So its Z points -X.
    # The adapter neck goes to Z < 0. So it goes in +X direction.
    # Collar sticks out in -X direction.
    # Local cylinder Z points to +X if we use Z=-collar_len, or Z points to -X if we rotate it
    collar1.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), -90)
    collar1.translate(FreeCAD.Vector(0, y_center, z_center))
    
    collar2 = Part.makeCylinder(collar_outer, collar_len)
    collar2.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
    collar2.translate(FreeCAD.Vector(BASIN_SIZE, y_center, z_center))
    
    basin_body = basin_body.fuse(collar1).fuse(collar2)
    
    # Side Openings bore hole
    c1 = Part.makeCylinder(OUTLET_DIAMETER / 2, BASIN_SIZE + 2*collar_len + 2.0)
    c1.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
    c1.translate(FreeCAD.Vector(-collar_len - 1.0, y_center, z_center))
    basin_body = basin_body.cut(c1)
    
    # Cut internal grooves using exactly the thread geometry plus clearance
    # ADAPTER_TOLERANCE is defined in config, usually 0.5
    from config import ADAPTER_TOLERANCE
    
    thread_h = WALL_THICKNESS + 20.0  # Same as insertion_len
    t1 = create_lofted_thread(THREAD_NOMINAL_RADIUS, 4.0, thread_h, False)
    t1.translate(FreeCAD.Vector(0, 0, -thread_h))
    t1.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), -90)
    t1.translate(FreeCAD.Vector(-collar_len, y_center, z_center))
    
    t2 = create_lofted_thread(THREAD_NOMINAL_RADIUS, 4.0, thread_h, False)
    t2.translate(FreeCAD.Vector(0, 0, -thread_h))
    t2.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
    t2.translate(FreeCAD.Vector(BASIN_SIZE + collar_len, y_center, z_center))
    
    basin_body = basin_body.cut(t1).cut(t2)
    
    # Bottom Cutout Guide
    bottom_cut = Part.makeCylinder(OUTLET_DIAMETER / 2, WALL_THICKNESS - CUTOUT_GUIDE_THICKNESS)
    bottom_cut.translate(FreeCAD.Vector(BASIN_SIZE/2, BASIN_SIZE/2, -0.1))
    basin_body = basin_body.cut(bottom_cut)
    

    

    
    os.makedirs(EXPORT_BASE, exist_ok=True)
    basin_body.exportStep(EXPORT_STEP)
    basin_body.exportStl(EXPORT_STL)
    print(f"Exported Catch Basin to {EXPORT_STEP} and {EXPORT_STL}")
    
    return basin_body

def main():
    doc = FreeCAD.newDocument("part_01_catch_basin")
    obj = doc.addObject("Part::Feature", "Catch_Basin")
    obj.Shape = create_basin()
    doc.recompute()

if __name__ == '__main__':
    main()
