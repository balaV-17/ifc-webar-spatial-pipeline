"""Batch export IFC elements by semantic categories per storey"""

import ifcopenshell
import ifcopenshell.geom
import trimesh
import numpy as np
import json
from pathlib import Path
from collections import defaultdict

# ============================================================
# CATEGORY MAPPING (from your IFC analysis)
# ============================================================

CATEGORY_MAPPING = {
    # STRUCTURE category
    'structure': ['IfcWall', 'IfcWallStandardCase', 'IfcSlab', 'IfcBeam', 'IfcColumn'],
    
    # OPENINGS category
    'openings': ['IfcDoor', 'IfcWindow'],
    
    # CIRCULATION category
    'circulation': ['IfcStair', 'IfcStairFlight', 'IfcRailing'],
    
    # MEP category
    'mep': ['IfcFlowTerminal', 'IfcFlowController'],
    
    # SPACES (exported as JSON, not mesh)
    'spaces': ['IfcSpace']
}

# ============================================================
# Helper Functions
# ============================================================

def get_storey_name(element, ifc_file):
    """Extract storey name from an element"""
    try:
        # Get the containing storey
        if hasattr(element, 'ContainedInStructure'):
            rels = element.ContainedInStructure
            if rels:
                for rel in rels:
                    if rel.is_a('IfcRelContainedInSpatialStructure'):
                        storey = rel.RelatingStructure
                        return getattr(storey, 'Name', 'Unknown')
        
        # Fallback: get from element's ObjectPlacement
        if hasattr(element, 'ObjectPlacement'):
            placement = element.ObjectPlacement
            if placement and hasattr(placement, 'PlacementRelTo'):
                # Traverse up to find storey
                pass
    except:
        pass
    return 'Unknown_Storey'

def extract_mesh(element, settings):
    """Extract mesh from a single IFC element"""
    try:
        shape = ifcopenshell.geom.create_shape(settings, element)
        vertices = shape.geometry.verts
        faces = shape.geometry.faces
        
        if vertices and faces:
            vertices_array = np.array(vertices).reshape(-1, 3)
            faces_array = np.array(faces).reshape(-1, 3)
            
            mesh = trimesh.Trimesh(
                vertices=vertices_array,
                faces=faces_array,
                process=False  # Keep original geometry
            )
            
            # Add metadata
            mesh.metadata['name'] = getattr(element, 'Name', 'Unnamed')
            mesh.metadata['ifc_type'] = element.is_a()
            
            return mesh
    except Exception as e:
        # Silently skip elements that fail
        pass
    return None

def simplify_mesh(mesh, target_faces=None):
    """Simplify mesh for performance (especially railings)"""
    if target_faces and len(mesh.faces) > target_faces:
        try:
            # Reduce to target_faces (1/4 of original)
            reduction_ratio = 1 - (target_faces / len(mesh.faces))
            simplified = mesh.simplify_quadratic_decimation(target_faces)
            return simplified
        except:
            pass
    return mesh

# ============================================================
# Main Export Function
# ============================================================

def export_by_category_and_storey(ifc_path, output_dir='output'):
    """Main export function"""
    
    print(f"Opening IFC file: {ifc_path}")
    ifc_file = ifcopenshell.open(ifc_path)
    
    # Geometry settings (optimized for performance)
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)  # CRITICAL: skip expensive boolean cuts
    
    # Store elements by (storey, category)
    storey_categories = defaultdict(lambda: defaultdict(list))
    spaces_data = defaultdict(list)
    
    print("\nProcessing elements...")
    
    # Process each category
    for category, ifc_types in CATEGORY_MAPPING.items():
        print(f"\n  Processing {category}...")
        
        for ifc_type in ifc_types:
            elements = ifc_file.by_type(ifc_type)
            print(f"    Found {len(elements)} {ifc_type}")
            
            for element in elements:
                if ifc_type == 'IfcSpace':
                    # Handle spaces differently (JSON only)
                    storey = get_storey_name(element, ifc_file)
                    space_info = {
                        'guid': element.GlobalId if hasattr(element, 'GlobalId') else None,
                        'type': ifc_type,
                        'name': getattr(element, 'Name', 'Unnamed'),
                        'storey': storey,
                        'area': getattr(element, 'NetFloorArea', None),
                        'volume': getattr(element, 'Volume', None),
                        'center': None  # Will calculate from geometry if possible
                    }
                    spaces_data[storey].append(space_info)
                else:
                    # Extract mesh
                    mesh = extract_mesh(element, settings)
                    if mesh:
                        # Simplify railings aggressively
                        if ifc_type == 'IfcRailing':
                            mesh = simplify_mesh(mesh, target_faces=500)
                        
                        storey = get_storey_name(element, ifc_file)
                        storey_categories[storey][category].append(mesh)
    
    # ============================================================
    # Export GLB files per storey and category
    # ============================================================
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*50)
    print("Exporting GLB files...")
    print("="*50)
    
    exported_files = []
    
        # Define sanitization function outside the loop (once)
    def sanitize_folder_name(name):
        """Remove invalid characters for Windows folder names"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        # Also remove trailing spaces and dots
        name = name.rstrip(' .')
        # Limit length
        if len(name) > 100:
            name = name[:100]
        return name

    for storey, categories in storey_categories.items():
        # Create storey folder with sanitized name
        sanitized_name = sanitize_folder_name(storey)
        storey_folder = output_path / sanitized_name
        storey_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 Storey: {storey}")
        
        for category, meshes in categories.items():
            if not meshes:
                continue
            
            # Merge all meshes in this category
            print(f"  Merging {len(meshes)} meshes for {category}...")
            
            try:
                # Handle single vs multiple meshes
                if len(meshes) == 1:
                    combined = meshes[0]
                else:
                    combined = trimesh.util.concatenate(meshes)
                
                # Export filename
                filename = f"{storey}_{category}.glb"
                filepath = storey_folder / filename
                
                combined.export(filepath, file_type='glb')
                
                file_size = filepath.stat().st_size / 1024  # KB
                print(f"    ✓ Exported: {filename} ({file_size:.1f} KB)")
                print(f"      Vertices: {len(combined.vertices)}, Faces: {len(combined.faces)}")
                
                exported_files.append(str(filepath))
                
            except Exception as e:
                print(f"    ✗ Failed to export {category}: {e}")
        
        # Export spaces JSON for this storey
        if spaces_data.get(storey):
            spaces_file = storey_folder / f"{storey}_spaces.json"
            with open(spaces_file, 'w') as f:
                json.dump(spaces_data[storey], f, indent=2)
            print(f"    ✓ Exported spaces: {spaces_file.name}")
    
    # ============================================================
    # Summary
    # ============================================================
    
    print("\n" + "="*50)
    print("EXPORT SUMMARY")
    print("="*50)
    print(f"Total files exported: {len(exported_files)}")
    print("\nOutput directory:", output_path.absolute())
    
    return exported_files

# ============================================================
# Run Export
# ============================================================

if __name__ == "__main__":
    import sys
    
    ifc_path = 'data/sample.ifc'
    output_dir = 'output'
    
    if len(sys.argv) > 1:
        ifc_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    try:
        exported = export_by_category_and_storey(ifc_path, output_dir)
        print("\n🎉 BATCH EXPORT COMPLETE!")
        print("\nNext step: Open in Three.js viewer")
        
    except FileNotFoundError:
        print(f"Error: IFC file not found at {ifc_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()