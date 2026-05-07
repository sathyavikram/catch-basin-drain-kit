You are an expert in FreeCAD Python scripting and parametric CAD design.
Your task is to generate clean, modular, and parametric FreeCAD Python 
code to do following

Design a “9-in Square Catch Basin Drain Kit with 2-Opening Catch Basin” with the following requirements.

-----------------------------------
FEATURES TO IMPLEMENT
-----------------------------------
Drain stormwater away before it causes property damage
Connects to 3-inch and 4-inch drain pipes for a soil-tight fit
Includes catch basin, 2 outlet adapters, plug, black grate
Collect stormwater runoff and standing water on your property and direct to drain pipes before it causes costly property damage
Manage moderate flows of water, ideal for lawns, landscaped areas, under downspouts, patios, walkways
The catch basin and grate, as part of a complete drainage system, connect to drain pipes to capture surface water and direct it away for proper release downstream
Lightweight and easy to install
Keyed side openings lock outlet adapters in place, cutout guide on bottom for additional keyed opening if needed, Catch basin made of polypropylene (PP) using a combination of virgin and recycled content treated with UV inhibitors to prevent fading and cracking
Kit includes 9 inch Catch Basin Drain with 2 side openings and cutout guide for bottom opening, 2 Outlet Adapters, 1 Plug, 9 inch Square Plastic Grate
Length (Inches) 9 Width Measurement 9-in Length Measurement 9-in
UNSPSC 21101500

-----------------------------------
GENERAL INSTRUCTIONS
-----------------------------------
- Use FreeCAD Python API (Part, PartDesign, Sketcher as needed)
- Split into parts to fit 3D printed build plate 256*256*256mm when sclae=1
- All paramaters should be driven by scale
- Code must be:
  - Fully parametric (all dimensions defined as variables at top)
  - Modular - generate separate file for each part
  - Generate final assembly file to use parts and create final assembly model 
  - Clean and readable
- The design should be robust and not rely on fragile geometry references
- Use proper thickness for real world daily use
- Avoid overly complex dependencies
- Prefer simple solids + boolean operations where possible
- Ensure the model recomputes without errors
- When part code is executed, also generate step and stl files into export folder
- When assembly is executed, also generate step and stl files into export/assembly folder. Generate files for each part and final assembly
- use execute_freecad_script mcp tool to visual verify designs in different angles
- visual verify using execute_freecad_script mcp tool of each part in different angles
- visual verify using execute_freecad_script mcp tool of assembly different angles

-----------------------------------
IMPORTANT
-----------------------------------
- Do NOT overcomplicate geometry
- Focus on functional, printable design
- Ensure all parts are manufacturable using standard FDM printers
-----------------------------------

Now generate the complete FreeCAD Python code following the above requirements.

Read requirements.md file and images from reference folder to design Square Catch Basin Drain Kit with 2-Opening Catch Basin.
Follow carry-bag-bin projecture (/Users/intelligentmachine/Documents/workspace/3d-models/carry-bag-bin) structure and orgnize parts and assembly 