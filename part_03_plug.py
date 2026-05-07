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
