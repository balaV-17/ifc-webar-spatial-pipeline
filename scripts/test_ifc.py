"""Minimal IFC parser - updated for architectural model"""

import ifcopenshell

try:
    ifc_file = ifcopenshell.open('data/sample.ifc')
    
    # Get project name
    project = ifc_file.by_type('IfcProject')[0]
    print(f"Project Name: {getattr(project, 'Name', 'Undefined')}")
    
    # Count architectural elements (not just walls/slabs)
    element_counts = {
        'IfcWall': len(ifc_file.by_type('IfcWall')),
        'IfcWallStandardCase': len(ifc_file.by_type('IfcWallStandardCase')),
        'IfcSlab': len(ifc_file.by_type('IfcSlab')),
        'IfcColumn': len(ifc_file.by_type('IfcColumn')),
        'IfcBeam': len(ifc_file.by_type('IfcBeam')),
        'IfcDoor': len(ifc_file.by_type('IfcDoor')),
        'IfcWindow': len(ifc_file.by_type('IfcWindow')),
        'IfcStair': len(ifc_file.by_type('IfcStair')),
        'IfcRailing': len(ifc_file.by_type('IfcRailing')),
        'IfcSpace': len(ifc_file.by_type('IfcSpace'))
    }
    
    print("\n=== Element Counts ===")
    for element_type, count in element_counts.items():
        if count > 0:
            print(f"  {element_type}: {count}")
    
    total_elements = sum(element_counts.values())
    print(f"\nTotal architectural elements: {total_elements}")
    
except FileNotFoundError:
    print("Error: data/sample.ifc not found")
except Exception as e:
    print(f"Error: {e}")