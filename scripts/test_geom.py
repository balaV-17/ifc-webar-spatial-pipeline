#!/usr/bin/env python
"""Test ifcopenshell.geom functionality"""

import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import ifcopenshell
    print(f"IfcOpenShell version: {ifcopenshell.version}")
    print(f"Has geom attribute: {hasattr(ifcopenshell, 'geom')}")
    
    if hasattr(ifcopenshell, 'geom'):
        import ifcopenshell.geom
        print("✓ ifcopenshell.geom imported successfully")
        
        # Try to open IFC file
        ifc_file = ifcopenshell.open('data/sample.ifc')
        print(f"✓ Opened IFC file: {ifc_file}")
        
        # Try to get geometry settings
        settings = ifcopenshell.geom.settings()
        print(f"✓ Geometry settings created: {settings}")
        
        # Try to process a slab
        slabs = ifc_file.by_type('IfcSlab')
        print(f"Found {len(slabs)} slabs")
        
        if slabs:
            shape = ifcopenshell.geom.create_shape(settings, slabs[0])
            print(f"✓ Created shape for first slab")
            print(f"  Vertices: {len(shape.geometry.verts)}")
            print(f"  Faces: {len(shape.geometry.faces)}")
        
    else:
        print("✗ ifcopenshell.geom is NOT available")
        print("  Try reinstalling ifcopenshell:")
        print("  pip uninstall ifcopenshell")
        print("  pip install ifcopenshell")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()