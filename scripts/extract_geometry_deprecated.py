"""Extract geometry from IFC slabs"""

import ifcopenshell
import ifcopenshell.geom
import numpy as np

def extract_slab_geometry(ifc_file):
    """Extract geometry from IfcSlab elements"""
    slabs = ifc_file.by_type('IfcSlab')
    
    if not slabs:
        print("No slabs found in IFC file")
        return
    
    settings = ifcopenshell.geom.settings()
    total_vertices = 0
    total_faces = 0
    
    for i, slab in enumerate(slabs):
        try:
            # Extract geometry
            shape = ifcopenshell.geom.create_shape(settings, slab)
            vertices = shape.geometry.verts
            faces = shape.geometry.faces
            
            # Convert to numpy arrays
            vertices_array = np.array(vertices).reshape(-1, 3)
            faces_array = np.array(faces).reshape(-1, 3)
            
            total_vertices += len(vertices_array)
            total_faces += len(faces_array)
            
            # Calculate bounding box
            if len(vertices_array) > 0:
                bbox_min = vertices_array.min(axis=0)
                bbox_max = vertices_array.max(axis=0)
                
                print(f"\nSlab {i+1}:")
                print(f"  Name: {getattr(slab, 'Name', 'Unnamed')}")
                print(f"  Vertices: {len(vertices_array)}")
                print(f"  Faces: {len(faces_array)}")
                print(f"  BBox Min: [{bbox_min[0]:.2f}, {bbox_min[1]:.2f}, {bbox_min[2]:.2f}]")
                print(f"  BBox Max: [{bbox_max[0]:.2f}, {bbox_max[1]:.2f}, {bbox_max[2]:.2f}]")
        
        except Exception as e:
            print(f"Error processing slab {i+1}: {e}")
    
    print(f"\n=== Summary ===")
    print(f"Total vertices across all slabs: {total_vertices}")
    print(f"Total faces across all slabs: {total_faces}")
    return total_vertices > 0

# Main execution
if __name__ == "__main__":
    try:
        ifc_file = ifcopenshell.open('data/sample.ifc')
        print("Successfully opened IFC file")
        success = extract_slab_geometry(ifc_file)
        
        if success:
            print("\n✓ Geometry extraction successful!")
        else:
            print("\n✗ No geometry extracted")
            
    except FileNotFoundError:
        print("Error: data/sample.ifc not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()