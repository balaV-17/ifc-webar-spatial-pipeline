"""Batch export IFC elements by semantic categories per storey
Fixed version with proper storey detection and German name mapping
"""

import ifcopenshell
import ifcopenshell.geom
import trimesh
import numpy as np
import json
import re
from pathlib import Path
from collections import defaultdict

# ============================================================
# CONFIGURATION
# ============================================================

# Map German storey codes to clean English names
STOREY_MAPPING = {
    'EG': 'GroundFloor',
    'OG1': 'Level_01',
    'OG2': 'Level_02',
    'OG3': 'Level_03',
    'OG4': 'Level_04',
    'OG5': 'Level_05',
    'DA': 'Roof',
    'DG': 'Roof',
    'Keller': 'Basement',
    'UK': 'Basement',
}

# Category mapping (IFC types to semantic categories)
CATEGORY_MAPPING = {
    'structure': ['IfcWall', 'IfcWallStandardCase', 'IfcSlab', 'IfcBeam', 'IfcColumn'],
    'openings': ['IfcDoor', 'IfcWindow'],
    'circulation': ['IfcStair', 'IfcStairFlight', 'IfcRailing'],
    'mep': ['IfcFlowTerminal', 'IfcFlowController'],
    'spaces': ['IfcSpace']
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def sanitize_folder_name(name):
    """Remove invalid characters for Windows folder names"""
    if not name:
        return "Unknown"
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove trailing spaces and dots
    name = name.rstrip(' .')
    # Limit length
    if len(name) > 100:
        name = name[:100]
    return name

def clean_storey_name(name):
    """Convert German storey codes to clean English names"""
    if not name:
        return "Unknown"
    
    # Check for exact matches in mapping
    for de, en in STOREY_MAPPING.items():
        if de in name.upper():
            return en
    
    # Extract pattern like "OKRD OG1" -> "Level_01"
    match = re.search(r'OG(\d+)', name, re.IGNORECASE)
    if match:
        return f"Level_{int(match.group(1)):02d}"
    
    # Extract pattern like "OKRD EG"
    match = re.search(r'EG', name, re.IGNORECASE)
    if match:
        return "GroundFloor"
    
    # Extract pattern like "8.0.TH4" (technical floor)
    match = re.search(r'TH(\d+)', name, re.IGNORECASE)
    if match:
        return f"TechnicalFloor_{match.group(1)}"
    
    # Default: clean up the name
    clean = re.sub(r'[_\d]+$', '', name)  # Remove trailing numbers
    clean = clean.replace('_', ' ').strip()
    return clean if clean else "Unknown"

def get_storey_name(element, ifc_file):
    """Extract storey name from an element — only from IfcBuildingStorey"""
    try:
        # Method 1: Check if element is itself a storey
        if element.is_a() == 'IfcBuildingStorey':
            return getattr(element, 'Name', None)
        
        # Method 2: Direct containment in IfcBuildingStorey
        if hasattr(element, 'ContainedInStructure'):
            for rel in element.ContainedInStructure:
                if rel.is_a() == 'IfcRelContainedInSpatialStructure':
                    container = rel.RelatingStructure
                    # Only use IfcBuildingStorey, ignore IfcSpace
                    if container.is_a() == 'IfcBuildingStorey':
                        return getattr(container, 'Name', None)
        
        # Method 3: Traverse up through spatial decomposition
        if hasattr(element, 'Decomposes'):
            for rel in element.Decomposes:
                if rel.is_a() == 'IfcRelAggregates':
                    parent = rel.RelatingObject
                    if parent.is_a() == 'IfcBuildingStorey':
                        return getattr(parent, 'Name', None)
                    # Recursively check parent
                    return get_storey_name(parent, ifc_file)
                    
    except Exception:
        pass
    
    return None

def extract_mesh(element, settings):
    """Extract mesh from a single IFC element"""
    try:
        shape = ifcopenshell.geom.create_shape(settings, element)
        vertices = shape.geometry.verts
        faces = shape.geometry.faces
        
        if vertices and faces and len(vertices) >= 3 and len(faces) >= 3:
            vertices_array = np.array(vertices).reshape(-1, 3)
            faces_array = np.array(faces).reshape(-1, 3)
            
            mesh = trimesh.Trimesh(
                vertices=vertices_array,
                faces=faces_array,
                process=False
            )
            
            # Add metadata
            mesh.metadata['name'] = getattr(element, 'Name', 'Unnamed')
            mesh.metadata['ifc_type'] = element.is_a()
            
            return mesh
    except Exception:
        pass
    return None

def simplify_mesh(mesh, target_faces=None):
    """Simplify mesh for performance (especially railings)"""
    if target_faces and len(mesh.faces) > target_faces:
        try:
            simplified = mesh.simplify_quadratic_decimation(target_faces)
            return simplified
        except Exception:
            pass
    return mesh

# ============================================================
# MAIN EXPORT FUNCTION
# ============================================================

def export_by_category_and_storey(ifc_path, output_dir='output'):
    """Main export function"""
    
    print(f"Opening IFC file: {ifc_path}")
    ifc_file = ifcopenshell.open(ifc_path)
    
    # Get all building storeys first
    building_storeys = ifc_file.by_type('IfcBuildingStorey')
    print(f"Found {len(building_storeys)} building storeys")
    
    # Geometry settings (optimized for performance)
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)  # Skip expensive boolean cuts
    
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
                    if storey:
                        space_info = {
                            'guid': getattr(element, 'GlobalId', None),
                            'type': ifc_type,
                            'name': getattr(element, 'Name', 'Unnamed'),
                            'long_name': getattr(element, 'LongName', ''),
                            'storey': storey,
                            'area': float(getattr(element, 'NetFloorArea', 0)) if getattr(element, 'NetFloorArea', None) else None,
                            'volume': float(getattr(element, 'Volume', 0)) if getattr(element, 'Volume', None) else None,
                        }
                        spaces_data[storey].append(space_info)
                else:
                    # Skip if no valid storey
                    storey = get_storey_name(element, ifc_file)
                    if not storey:
                        continue
                    
                    # Extract mesh
                    mesh = extract_mesh(element, settings)
                    if mesh and len(mesh.vertices) > 0:
                        # Simplify railings aggressively
                        if ifc_type == 'IfcRailing':
                            mesh = simplify_mesh(mesh, target_faces=500)
                        
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
    
    for storey, categories in storey_categories.items():
        # Clean and sanitize storey name for folder
        clean_name = clean_storey_name(storey)
        sanitized_name = sanitize_folder_name(clean_name)
        storey_folder = output_path / sanitized_name
        storey_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 Storey: {storey} -> {sanitized_name}")
        
        for category, meshes in categories.items():
            if not meshes:
                continue
            
            print(f"  Merging {len(meshes)} meshes for {category}...")
            
            try:
                # Merge all meshes in this category
                if len(meshes) == 1:
                    combined = meshes[0]
                else:
                    combined = trimesh.util.concatenate(meshes)
                
                # Export filename
                filename = f"{sanitized_name}_{category}.glb"
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
            spaces_file = storey_folder / f"{sanitized_name}_spaces.json"
            with open(spaces_file, 'w', encoding='utf-8') as f:
                json.dump(spaces_data[storey], f, indent=2, ensure_ascii=False)
            print(f"    ✓ Exported spaces: {spaces_file.name}")
    
    # ============================================================
    # Summary
    # ============================================================
    
    print("\n" + "="*50)
    print("EXPORT SUMMARY")
    print("="*50)
    print(f"Storeys exported: {len(storey_categories)}")
    print(f"Total files exported: {len(exported_files)}")
    print("\nOutput directory:", output_path.absolute())
    
    # List created folders
    print("\nCreated folders:")
    for folder in sorted(output_path.iterdir()):
        if folder.is_dir():
            glb_count = len(list(folder.glob("*.glb")))
            print(f"  📁 {folder.name}/ ({glb_count} GLB files)")
    
    return exported_files

# ============================================================
# RUN EXPORT
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