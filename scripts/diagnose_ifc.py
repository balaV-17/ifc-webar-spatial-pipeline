import ifcopenshell
from collections import Counter

try:
    # Open the IFC file
    ifc_file = ifcopenshell.open('data/sample.ifc')
    
    # Count all elements by their type
    element_types = Counter()
    
    # Iterate through all elements and collect their type
    for element in ifc_file.by_type('IfcProduct'):
        element_type = element.is_a()
        element_types[element_type] += 1
    
    # Print top 20 most common element types
    print("=== IFC File Contents ===\n")
    print(f"Total elements: {sum(element_types.values())}\n")
    print("Top 20 element types by count:")
    for elem_type, count in element_types.most_common(20):
        print(f"  {elem_type}: {count}")
    
    # Specifically check for walls and slabs with detailed info
    print("\n=== Detailed Check ===\n")
    walls = ifc_file.by_type('IfcWall')
    slabs = ifc_file.by_type('IfcSlab')
    
    print(f"IfcWall elements: {len(walls)}")
    if walls:
        for i, wall in enumerate(walls[:3]):  # Show first 3 walls
            print(f"  Wall {i+1}: Name={getattr(wall, 'Name', 'N/A')}")
    
    print(f"\nIfcSlab elements: {len(slabs)}")
    if slabs:
        for i, slab in enumerate(slabs[:3]):
            print(f"  Slab {i+1}: Name={getattr(slab, 'Name', 'N/A')}")
    
except FileNotFoundError:
    print("Error: data/sample.ifc not found")
except Exception as e:
    print(f"Error: {e}")