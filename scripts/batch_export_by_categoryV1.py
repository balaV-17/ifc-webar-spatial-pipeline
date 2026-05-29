"""Batch export IFC elements by semantic categories per storey
Fixed version with XR material system, proper storey detection, and German name mapping
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
# XR MATERIAL SYSTEM
# ============================================================

# Mobile-safe PBR materials for WebXR visualization
# Format: [R, G, B, A] where A is 0-255 alpha
XR_MATERIALS = {
    "structure": {
        "color": [231, 76, 60, 150],      # Structural Red, 60% opacity
    },
    "circulation": {
        "color": [46, 204, 113, 150],     # Safety Green, 60% opacity
    },
    "openings": {
        "color": [0, 210, 255, 115],      # Electric Cyan, 45% opacity
    },
    "mep": {
        "color": [44, 62, 80, 102],       # Deep Indigo, 40% opacity
    },
    "spaces": {
        "color": [248, 249, 249, 64],     # Ghost Frost White, 25% opacity
    },
    "roof": {
        "color": [84, 110, 122, 150],     # Slate Gray, 60% opacity
    }
}

# Category mapping (IFC types to semantic categories)
CATEGORY_MAP = {
    "IfcWall": "structure",
    "IfcWallStandardCase": "structure",
    "IfcSlab": "structure",
    "IfcColumn": "structure",
    "IfcBeam": "structure",

    "IfcDoor": "openings",
    "IfcWindow": "openings",

    "IfcStair": "circulation",
    "IfcStairFlight": "circulation",
    "IfcRailing": "circulation",

    "IfcFlowTerminal": "mep",
    "IfcFlowController": "mep",

    "IfcSpace": "spaces",

    "IfcRoof": "roof"
}

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
    name = name.rstrip(' .')
    if len(name) > 100:
        name = name[:100]
    return name

def clean_storey_name(name):
    """Convert German storey codes to clean English names"""
    if not name:
        return "Unknown"
    
    for de, en in STOREY_MAPPING.items():
        if de in name.upper():
            return en
    
    match = re.search(r'OG(\d+)', name, re.IGNORECASE)
    if match:
        return f"Level_{int(match.group(1)):02d}"
    
    match = re.search(r'EG', name, re.IGNORECASE)
    if match:
        return "GroundFloor"
    
    match = re.search(r'TH(\d+)', name, re.IGNORECASE)
    if match:
        return f"TechnicalFloor_{match.group(1)}"
    
    clean = re.sub(r'[_\d]+$', '', name)
    clean = clean.replace('_', ' ').strip()
    return clean if clean else "Unknown"

def get_storey_name(element, ifc_file):
    """Extract storey name from an element — only from IfcBuildingStorey"""
    try:
        if element.is_a() == 'IfcBuildingStorey':
            return getattr(element, 'Name', None)
        
        if hasattr(element, 'ContainedInStructure'):
            for rel in element.ContainedInStructure:
                if rel.is_a() == 'IfcRelContainedInSpatialStructure':
                    container = rel.RelatingStructure
                    if container.is_a() == 'IfcBuildingStorey':
                        return getattr(container, 'Name', None)
        
        if hasattr(element, 'Decomposes'):
            for rel in element.Decomposes:
                if rel.is_a() == 'IfcRelAggregates':
                    parent = rel.RelatingObject
                    if parent.is_a() == 'IfcBuildingStorey':
                        return getattr(parent, 'Name', None)
                    return get_storey_name(parent, ifc_file)
                    
    except Exception:
        pass
    
    return None

def get_category(element):
    """Get semantic category for an IFC element using CATEGORY_MAP"""
    ifc_type = element.is_a()
    return CATEGORY_MAP.get(ifc_type, None)

def create_xr_material(category):
    """Create mobile-safe PBR material for WebXR"""
    if category not in XR_MATERIALS:
        return None
    
    color = XR_MATERIALS[category]["color"]
    r, g, b, a = color
    
    # Convert 0-255 to 0.0-1.0 for glTF
    material = trimesh.visual.material.PBRMaterial(
        baseColorFactor=[
            r / 255.0,
            g / 255.0,
            b / 255.0,
            a / 255.0
        ],
        metallicFactor=0.0,      # Non-metallic for buildings
        roughnessFactor=1.0,     # Fully rough for performance
        alphaMode='BLEND'        # Enable transparency
    )
    
    return material

def extract_mesh(element, settings):
    """Extract mesh from a single IFC element with XR material"""
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
            
            # Assign XR material based on category
            category = get_category(element)
            if category:
                material = create_xr_material(category)
                if material:
                    mesh.visual.material = material
            
            # Add metadata
            mesh.metadata['name'] = getattr(element, 'Name', 'Unnamed')
            mesh.metadata['ifc_type'] = element.is_a()
            mesh.metadata['category'] = category or 'unknown'
            
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

def extract_mesh(element, settings, ifc_file):
    """Extract mesh from IFC element with XR material and coordinate normalization"""
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
            
            # STEP 1: Normalize units to meters
            mesh = normalize_units(mesh, ifc_file)
            
            # STEP 2: Convert Z-up to Y-up
            mesh = convert_to_y_up(mesh)
            
            # STEP 3: Center at origin
            mesh = normalize_coordinates(mesh)
            
            # STEP 4: Assign XR material
            category = get_category(element)
            if category:
                material = create_xr_material(category)
                if material:
                    mesh.visual.material = material
            
            # Metadata
            mesh.metadata['name'] = getattr(element, 'Name', 'Unnamed')
            mesh.metadata['ifc_type'] = element.is_a()
            mesh.metadata['category'] = category or 'unknown'
            
            return mesh
    except Exception as e:
        print(f"    Warning: Failed to extract mesh: {e}")
    return None

#Coordinate normalization and Y-up transform

def normalize_coordinates(mesh):
    """Center mesh at origin and convert to meters-scale"""
    if mesh is None or len(mesh.vertices) == 0:
        return mesh
    
    # Get bounding box
    bounds = mesh.bounds  # [[min_x, min_y, min_z], [max_x, max_y, max_z]]
    center = (bounds[0] + bounds[1]) / 2.0
    
    # Translate to center at origin
    mesh.vertices -= center
    
    # Store original center as metadata for AR placement
    mesh.metadata['original_center'] = center.tolist()
    mesh.metadata['bounds'] = bounds.tolist()
    
    return mesh

def convert_to_y_up(mesh):
    """Rotate from IFC Z-up to glTF/Three.js Y-up"""
    if mesh is None:
        return mesh
    
    # IFC: Z is up, Y is forward
    # Three.js/glTF: Y is up, -Z is forward
    # Rotation: -90° around X axis
    
    rotation_matrix = np.array([
        [1,  0,  0],
        [0,  0,  1],
        [0, -1,  0]
    ])
    
    mesh.vertices = np.dot(mesh.vertices, rotation_matrix.T)
    
    # Recompute normals after rotation
    mesh.fix_normals()
    
    mesh.metadata['coordinate_system'] = 'Y-up (glTF/Three.js)'
    
    return mesh

def normalize_units(mesh, ifc_file):
    """Convert IFC project units to meters"""
    try:
        # Get project unit assignment
        project = ifc_file.by_type('IfcProject')[0]
        units = project.UnitsInContext.Units if hasattr(project, 'UnitsInContext') else []
        
        scale_factor = 1.0  # default: already in meters
        
        for unit in units:
            if unit.is_a('IfcSIUnit'):
                if unit.UnitType == 'LENGTHUNIT':
                    prefix = getattr(unit, 'Prefix', None)
                    # Common prefixes
                    prefix_scale = {
                        'MILLI': 0.001,
                        'CENTI': 0.01,
                        'DECI': 0.1,
                        None: 1.0,
                        'KILO': 1000.0
                    }
                    scale_factor = prefix_scale.get(prefix, 1.0)
                    break
            elif unit.is_a('IfcConversionBasedUnit'):
                # Handle imperial or other units
                if 'foot' in unit.Name.lower() or 'ft' in unit.Name.lower():
                    scale_factor = 0.3048
                elif 'inch' in unit.Name.lower() or 'in' in unit.Name.lower():
                    scale_factor = 0.0254
        
        if scale_factor != 1.0:
            mesh.vertices *= scale_factor
            mesh.metadata['unit_scale'] = scale_factor
            print(f"    Applied unit scale: {scale_factor} (to meters)")
            
    except Exception as e:
        print(f"    Warning: Could not detect units, assuming meters: {e}")
        mesh.metadata['unit_scale'] = 1.0
    
    return mesh



# ============================================================
# MAIN EXPORT FUNCTION
# ============================================================

def export_by_category_and_storey(ifc_path, output_dir='output'):
    """Main export function with XR materials"""
    
    print(f"Opening IFC file: {ifc_path}")
    ifc_file = ifcopenshell.open(ifc_path)
    
    # Get all building storeys
    building_storeys = ifc_file.by_type('IfcBuildingStorey')
    print(f"Found {len(building_storeys)} building storeys")
    
    # Geometry settings (optimized for performance)
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)
    
    # Store elements by (storey, category)
    storey_categories = defaultdict(lambda: defaultdict(list))
    spaces_data = defaultdict(list)
    
    print("\nProcessing elements...")
    
    # Process all IFC elements that have a category mapping
    all_elements = []
    for ifc_type in CATEGORY_MAP.keys():
        elements = ifc_file.by_type(ifc_type)
        print(f"  Found {len(elements)} {ifc_type}")
        all_elements.extend(elements)
    
    for element in all_elements:
        ifc_type = element.is_a()
        category = get_category(element)
        
        if not category:
            continue
        
        if ifc_type == 'IfcSpace':
            # Handle spaces as JSON metadata
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
                    'category': category
                }
                spaces_data[storey].append(space_info)
        else:
            # Skip if no valid storey
            storey = get_storey_name(element, ifc_file)
            if not storey:
                continue
            
            # Extract mesh with XR material
            mesh = extract_mesh(element, settings, ifc_file)
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
    print("Exporting GLB files with XR materials...")
    print("="*50)
    
    exported_files = []
    
    for storey, categories in storey_categories.items():
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
                
                # Ensure material is preserved after merge
                # Use the first mesh's material as the combined material
                if meshes[0].visual.material:
                    combined.visual.material = meshes[0].visual.material
                
                # Export filename
                filename = f"{sanitized_name}_{category}.glb"
                filepath = storey_folder / filename
                
                combined.export(filepath, file_type='glb')
                
                file_size = filepath.stat().st_size / 1024
                print(f"    ✓ Exported: {filename} ({file_size:.1f} KB)")
                print(f"      Vertices: {len(combined.vertices)}, Faces: {len(combined.faces)}")
                print(f"      Material: {category} -> {XR_MATERIALS.get(category, {}).get('color', 'none')}")
                
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
    print("\nXR Materials applied:")
    for category, mat in XR_MATERIALS.items():
        r, g, b, a = mat["color"]
        print(f"  {category:12s}: RGB({r},{g},{b}) A={a}")
    print("\nOutput directory:", output_path.absolute())
    
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
        print("XR materials injected for WebXR visualization")
        
    except FileNotFoundError:
        print(f"Error: IFC file not found at {ifc_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()