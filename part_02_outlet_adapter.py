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
    

    adapter_body = flange.fuse(outer_pipe).fuse(insertion_neck)
    
    
    import math
    def create_lofted_thread(nominal_radius, t_pitch, t_length, is_male, extra_clearance=0.6):
        import math
        t_radius = nominal_radius
        if is_male:
            t_radius -= extra_clearance
            
        t_r_inner = t_radius - (t_pitch * 0.45)
        inner_X = t_r_inner - 2.0
        
        if is_male:
            pts_local = [
                FreeCAD.Vector(inner_X, 0, -t_pitch*0.35),
                FreeCAD.Vector(t_radius - 0.2, 0, -t_pitch*0.1),
                FreeCAD.Vector(t_radius - 0.2, 0,  t_pitch*0.1),
                FreeCAD.Vector(inner_X, 0,  t_pitch*0.35)
            ]
        else:
            pts_local = [
                FreeCAD.Vector(inner_X, 0, -t_pitch*0.35),
                FreeCAD.Vector(t_radius, 0, -t_pitch*0.1),
                FreeCAD.Vector(t_radius, 0,  t_pitch*0.1),
                FreeCAD.Vector(inner_X, 0,  t_pitch*0.35)
            ]
            
        steps = 36
        num_pitches = t_length / t_pitch
        total_steps = int(num_pitches * steps) + 1
        
        vertices = []
        for i in range(total_steps):
            z = i * t_length / (total_steps - 1)
            a = z * 2 * math.pi / t_pitch
            
            step_verts = []
            for p in pts_local:
                xw = p.x * math.cos(a) - p.y * math.sin(a)
                yw = p.x * math.sin(a) + p.y * math.cos(a)
                step_verts.append(FreeCAD.Vector(xw, yw, z + p.z))
            vertices.append(step_verts)
            
        faces = []
        for i in range(total_steps - 1):
            for j in range(len(pts_local) - 1):
                p1, p2 = vertices[i][j], vertices[i+1][j]
                p3, p4 = vertices[i+1][j+1], vertices[i][j+1]
                faces.extend([
                    Part.Face(Part.makePolygon([p1, p2, p3, p1])),
                    Part.Face(Part.makePolygon([p1, p3, p4, p1]))
                ])
            p1, p2 = vertices[i][-1], vertices[i+1][-1]
            p3, p4 = vertices[i+1][0], vertices[i][0]
            faces.extend([
                Part.Face(Part.makePolygon([p1, p2, p3, p1])),
                Part.Face(Part.makePolygon([p1, p3, p4, p1]))
            ])
            
        faces.extend([
            Part.Face(Part.makePolygon(vertices[0] + [vertices[0][0]])),
            Part.Face(Part.makePolygon(vertices[-1][::-1] + [vertices[-1][-1]]))
        ])
        
        t_sweep = Part.Solid(Part.Shell(faces))
        t_core = Part.makeCylinder(t_r_inner, t_length, FreeCAD.Vector(0,0,0))
        return t_core.fuse(t_sweep).removeSplitter() if is_male else t_core.fuse(t_sweep)

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
