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
EXPORT_STEP = os.path.join(EXPORT_BASE, "part_02_outlet_adapter.step")
EXPORT_STL = os.path.join(EXPORT_BASE, "part_02_outlet_adapter.stl")

def create_outlet_adapter():
    from config import ADAPTER_FLANGE_DIAMETER, WALL_THICKNESS, ADAPTER_OUTER_DIAMETER, ADAPTER_LENGTH, ADAPTER_INNER_DIAMETER, ADAPTER_TOLERANCE, OUTLET_DIAMETER
    
    # helper for filleting cylinders
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

    # 1. External Flange (sits on the outside of basin wall)
    flange = make_rounded_cylinder(ADAPTER_FLANGE_DIAMETER / 2, WALL_THICKNESS, 2.0)
    
    # 2. Outer pipe (sticks outward away from basin)
    outer_pipe = make_rounded_cylinder(ADAPTER_OUTER_DIAMETER / 2, ADAPTER_LENGTH, 2.0)
    outer_pipe.translate(FreeCAD.Vector(0, 0, WALL_THICKNESS))
    
    # 2a. Add outer detent lugs/clips
    def make_outer_lug(r, z_pos):
        import math
        lug_length = 12.0
        lug_height = 4.0
        lug_width = 15.0
        
        v1 = FreeCAD.Vector(r, 0, z_pos)
        v2 = FreeCAD.Vector(r + lug_height, 0, z_pos - lug_length)
        v3 = FreeCAD.Vector(r, 0, z_pos - lug_length)
        
        wire = Part.makePolygon([v1, v2, v3, v1])
        face = Part.Face(wire)
        
        swept = face.revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), (lug_width / r) * 180 / math.pi)
        
        ang = - ((lug_width / r) * 180 / math.pi) / 2.0
        swept.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), ang)
        
        return swept

    lugs = []
    num_lugs = 6
    for i in range(num_lugs):
        angle = i * (360.0 / num_lugs)
        
        # Row 1 (near rim, facing the connecting pipe)
        lug1 = make_outer_lug(ADAPTER_OUTER_DIAMETER / 2, WALL_THICKNESS + ADAPTER_LENGTH - 10.0)
        lug1.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), angle)
        lugs.append(lug1)
        
        # Row 2 (staggered, further down the adapter)
        lug2 = make_outer_lug(ADAPTER_OUTER_DIAMETER / 2, WALL_THICKNESS + ADAPTER_LENGTH - 35.0)
        lug2.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), angle + (180.0 / num_lugs))
        lugs.append(lug2)

    outer_lugs_comp = Part.makeCompound(lugs)
    outer_pipe = outer_pipe.fuse(outer_lugs_comp)

    # 3. Insertion Neck (goes into the basin wall)
    insertion_len = WALL_THICKNESS + 20.0  # long enough to thread into external collar extensions
    insertion_neck = Part.makeCylinder(OUTLET_DIAMETER / 2 - ADAPTER_TOLERANCE, insertion_len)
    insertion_neck.translate(FreeCAD.Vector(0, 0, -insertion_len))
    
    # 4. Transition Cone (gradual taper from flange to the outward pipe for strength/flow)
    taper_length = 20.0
    from config import THREAD_NOMINAL_RADIUS
    # Start the cone at the flange (Z = WALL_THICKNESS) going outward to the outer pipe
    transition_cone = Part.makeCone(THREAD_NOMINAL_RADIUS, ADAPTER_OUTER_DIAMETER / 2, taper_length)
    transition_cone.translate(FreeCAD.Vector(0, 0, WALL_THICKNESS))

    adapter_body = flange.fuse(outer_pipe).fuse(insertion_neck).fuse(transition_cone)
    
    
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
        cutter_start = Part.makeCylinder(t_radius + 5.0, t_pitch + 2.0, FreeCAD.Vector(0,0, -1))
        res = res.cut(cutter_start.cut(chamfer_start))
        
        try: res = res.removeSplitter()
        except: pass
        return res

    from config import THREAD_NOMINAL_RADIUS
    thread = create_lofted_thread(THREAD_NOMINAL_RADIUS, 4.0, WALL_THICKNESS + 20.0, True)
    thread.translate(FreeCAD.Vector(0, 0, -insertion_len))
    adapter_body = adapter_body.fuse(thread)

    # 5. Central hollow bore going entirely through
    bore_len = ADAPTER_LENGTH + WALL_THICKNESS + insertion_len + 10
    inner_bore = Part.makeCylinder(ADAPTER_INNER_DIAMETER / 2, bore_len)
    inner_bore.translate(FreeCAD.Vector(0, 0, -(insertion_len + 5)))
    
    adapter_body = adapter_body.cut(inner_bore)
    
    os.makedirs(EXPORT_BASE, exist_ok=True)
    adapter_body.exportStep(EXPORT_STEP)
    adapter_body.exportStl(EXPORT_STL)
    print(f"Exported Outlet Adapter to {EXPORT_STEP} and {EXPORT_STL}")
    
    return adapter_body
def main():
    doc = FreeCAD.newDocument("part_02_outlet_adapter")
    obj = doc.addObject("Part::Feature", "Outlet_Adapter")
    obj.Shape = create_outlet_adapter()
    doc.recompute()

if __name__ == '__main__':
    main()
