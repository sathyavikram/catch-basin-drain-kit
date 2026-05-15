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
EXPORT_STEP = os.path.join(EXPORT_BASE, "part_03_plug.step")
EXPORT_STL = os.path.join(EXPORT_BASE, "part_03_plug.stl")

def create_plug():
    from config import PLUG_FLANGE_DIAMETER, WALL_THICKNESS, PLUG_DIAMETER, PLUG_THICKNESS
    
    def make_rounded_cylinder(r, h, radius=2.0):
        import Part
        cyl = Part.makeCylinder(r, h)
        edges = []
        for e in cyl.Edges:
            try:
                if 'Circle' in str(type(e.Curve)):
                    edges.append(e)
            except: pass
        if edges:
            try: cyl = cyl.makeFillet(radius, edges)
            except: pass
        return cyl

    # Flange
    flange = make_rounded_cylinder(PLUG_FLANGE_DIAMETER / 2, WALL_THICKNESS, 2.0)
    
    from config import ADAPTER_TOLERANCE
    # Insertion Neck
    insertion_len = WALL_THICKNESS + 20.0
    plug_neck = Part.makeCylinder(PLUG_DIAMETER / 2 - ADAPTER_TOLERANCE, insertion_len)
    plug_neck.translate(FreeCAD.Vector(0, 0, -insertion_len))
    
    # Plug body capping it off
    plug_body = make_rounded_cylinder(PLUG_DIAMETER / 2, PLUG_THICKNESS, 2.0)
    # Could just be part of the cap, but we'll put it at the very inner end:
    plug_body.translate(FreeCAD.Vector(0, 0, -insertion_len - PLUG_THICKNESS))
    
    plug_part = flange.fuse(plug_neck).fuse(plug_body)
    
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
        # Bevel the tip so it threads beautifully
        chamfer = Part.makeCone(t_radius + 2.0, t_r_inner, t_pitch/2 + 1, FreeCAD.Vector(0,0, t_length - t_pitch/2 - 1))
        cutter = Part.makeCylinder(t_radius + 5.0, t_pitch + 2.0, FreeCAD.Vector(0,0, t_length - 1))
        res = res.cut(cutter.cut(chamfer))
        chamfer_start = Part.makeCone(t_r_inner, t_radius + 2.0, t_pitch/2 + 1, FreeCAD.Vector(0,0, 0))
        cutter_start = Part.makeCylinder(t_radius + 5.0, t_pitch + 4.0, FreeCAD.Vector(0,0, -t_pitch))
        res = res.cut(cutter_start.cut(chamfer_start))
        
        try: res = res.removeSplitter()
        except: pass
        return res

    from config import THREAD_NOMINAL_RADIUS
    thread = create_lofted_thread(THREAD_NOMINAL_RADIUS, 4.0, WALL_THICKNESS + 20.0, True)
    thread.translate(FreeCAD.Vector(0, 0, -insertion_len))
    plug_part = plug_part.fuse(thread)
    
    os.makedirs(EXPORT_BASE, exist_ok=True)
    plug_part.exportStep(EXPORT_STEP)
    plug_part.exportStl(EXPORT_STL)
    print(f"Exported Plug to {EXPORT_STEP} and {EXPORT_STL}")
    
    return plug_part
def main():
    doc = FreeCAD.newDocument("part_03_plug")
    obj = doc.addObject("Part::Feature", "Plug")
    obj.Shape = create_plug()
    doc.recompute()

if __name__ == '__main__':
    main()
