"""Export IFC geometry to GLB format using trimesh"""

import ifcopenshell
import ifcopenshell.geom
import trimesh
import numpy as np
from pathlib import Path

def extract_mesh_from_slabs(ifc_file):
    """Extract mesh geometry from all IfcSlab elements"""
    slabs = ifc_file.by_type('IfcSlab')
    
    if not slabs:
        print("No slabs found in IFC file")
        return None
    
    settings = ifcopenshell.geom.settings()
    all_meshes = []
    
    for i, slab in enumerate(slabs):
        try:
            # Extract geometry
            shape = ifcopenshell.geom.create_shape(settings, slab)
            vertices = shape.geometry.verts
            faces = shape.geometry.faces
            
            # Convert to numpy arrays
            vertices_array = np.array(vertices).reshape(-1, 3)
            faces_array = np.array(faces).reshape(-1, 3)
            
            if len(vertices_array) > 0 and len(faces_array) > 0:
                # Create trimesh object
                mesh = trimesh.Trimesh(
                    vertices=vertices_array,
                    faces=faces_array,
                    process=False  # Don't process (keep original geometry)
                )
                
                # Add metadata
                mesh.metadata['name'] = getattr(slab, 'Name', f'Slab_{i+1}')
                mesh.metadata['ifc_type'] = 'IfcSlab'
                
                all_meshes.append(mesh)
                print(f"  ✓ Added {mesh.metadata['name']}: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
            
        except Exception as e:
            print(f"  ✗ Error processing slab {i+1}: {e}")
    
    return all_meshes

def merge_and_export(meshes, output_path):
    """Merge multiple meshes and export to GLB"""
    if not meshes:
        print("No meshes to export")
        return False
    
    print(f"\nMerging {len(meshes)} meshes...")
    
    # Merge all meshes into one
    combined_mesh = trimesh.util.concatenate(meshes)
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Export to GLB
    print(f"Exporting to {output_path}...")
    combined_mesh.export(output_path, file_type='glb')
    
    # Verify export
    if Path(output_path).exists():
        file_size = Path(output_path).stat().st_size / 1024  # KB
        print(f"\n✓ Export successful!")
        print(f"  File: {output_path}")
        print(f"  Size: {file_size:.2f} KB")
        print(f"  Total vertices: {len(combined_mesh.vertices)}")
        print(f"  Total faces: {len(combined_mesh.faces)}")
        return True
    else:
        print(f"✗ Export failed")
        return False

# Main execution
if __name__ == "__main__":
    try:
        # Open IFC file
        ifc_file = ifcopenshell.open('data/sample.ifc')
        print("✓ Opened IFC file")
        
        print("\nExtracting geometry from slabs...")
        meshes = extract_mesh_from_slabs(ifc_file)
        
        if meshes:
            # Export to GLB
            success = merge_and_export(meshes, 'output/walls.glb')
            
            if success:
                print("\n🎉 MILESTONE ACHIEVED! 🎉")
                print("You now have output/walls.glb")
                print("This is your first true milestone: IFC → GLB conversion working!")
        else:
            print("\n✗ No geometry extracted from slabs")
            
    except FileNotFoundError:
        print("Error: data/sample.ifc not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()