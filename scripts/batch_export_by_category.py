"""Batch export IFC elements by semantic categories per storey
V5: World-coordinate preservation per storey GLB
Fixes (cumulative from V4):
  - Suppress 'Representation is NULL' noise: skip elements with no body geometry
  - spaces.json includes elevation_m (storey elevation in meters)
  - [V5] DO NOT center individual meshes to origin — world X/Z preserved from IFC
  - [V5] Per-storey GLB: subtract only storey base elevation from Y so each
    storey's floor sits at Y=0 locally; X and Z remain in IFC world space
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
    ifc_type = element.is_a()
    return CATEGORY_MAP.get(ifc_type, None)

def get_unit_scale(ifc_file):
    """Return the length unit scale factor to convert IFC units → meters."""
    try:
        project = ifc_file.by_type('IfcProject')[0]
        units = project.UnitsInContext.Units if hasattr(project, 'UnitsInContext') else []
        for unit in units:
            if unit.is_a('IfcSIUnit') and unit.UnitType == 'LENGTHUNIT':
                prefix_scale = {
                    'MILLI': 0.001, 'CENTI': 0.01, 'DECI': 0.1,
                    None: 1.0, 'KILO': 1000.0
                }
                return prefix_scale.get(getattr(unit, 'Prefix', None), 1.0)
            elif unit.is_a('IfcConversionBasedUnit'):
                name = unit.Name.lower()
                if 'foot' in name or name == 'ft':
                    return 0.3048
                elif 'inch' in name or name == 'in':
                    return 0.0254
    except Exception:
        pass
    return 1.0

def get_storey_elevation(storey_name, ifc_file, unit_scale):
    """Return the elevation of the named IfcBuildingStorey in meters, or None."""
    try:
        for storey in ifc_file.by_type('IfcBuildingStorey'):
            if getattr(storey, 'Name', None) == storey_name:
                elev = getattr(storey, 'Elevation', None)
                if elev is not None:
                    return round(float(elev) * unit_scale, 4)
    except Exception:
        pass
    return None

def has_body_representation(element):
    """Return True only if the element has at least one Body/SweptSolid/Brep representation."""
    try:
        rep = getattr(element, 'Representation', None)
        if rep is None:
            return False
        for item in rep.Representations:
            if getattr(item, 'RepresentationIdentifier', None) in ('Body', 'Facetation', 'Box'):
                return True
        # Accept any representation if none is explicitly Body-tagged
        return len(rep.Representations) > 0
    except Exception:
        return False

def create_xr_material(category):
    if category not in XR_MATERIALS:
        return None
    color = XR_MATERIALS[category]["color"]
    r, g, b, a = color
    material = trimesh.visual.material.PBRMaterial(
        baseColorFactor=[
            r / 255.0,
            g / 255.0,
            b / 255.0,
            a / 255.0
        ],
        metallicFactor=0.0,
        roughnessFactor=1.0,
        alphaMode='BLEND'
    )
    return material

# ============================================================
# COORDINATE & UNIT TRANSFORMS
# ============================================================

def normalize_units(mesh, ifc_file):
    """Convert IFC project units to meters (Unity/Unreal 1:1 scale)"""
    scale_factor = get_unit_scale(ifc_file)
    if scale_factor != 1.0:
        mesh.vertices *= scale_factor
        print(f"    Applied unit scale: {scale_factor} (to meters)")
    mesh.metadata['unit_scale'] = scale_factor
    return mesh


def convert_to_y_up(mesh):
    """Rotate from IFC Z-up to glTF/Three.js Y-up (same as Unity/Unreal)"""
    if mesh is None:
        return mesh

    rotation_matrix = np.array([
        [1,  0,  0],
        [0,  0,  1],
        [0, -1,  0]
    ])

    mesh.vertices = np.dot(mesh.vertices, rotation_matrix.T)
    mesh.fix_normals()
    mesh.metadata['coordinate_system'] = 'Y-up (glTF/Unity/Unreal)'

    return mesh

def apply_storey_elevation_offset(mesh, storey_elevation_m):
    """Shift the merged storey mesh so its floor sits at Y=0 locally.

    Called ONCE on the already-concatenated storey mesh — NOT on individual
    elements.  X and Z remain in IFC world space so all elements keep their
    correct horizontal positions relative to each other.

    Args:
        mesh: trimesh.Trimesh — the merged, already Y-up, already scaled mesh
        storey_elevation_m: float — IfcBuildingStorey.Elevation in meters
    """
    if mesh is None or len(mesh.vertices) == 0 or storey_elevation_m is None:
        return mesh

    # After convert_to_y_up(), IFC Z (up) maps to glTF Y.
    # Subtract only the Y component (storey base elevation).
    mesh.vertices[:, 1] -= storey_elevation_m
    mesh.metadata['storey_elevation_offset_m'] = storey_elevation_m
    return mesh

def extract_mesh(element, settings, ifc_file):
    # --- FIX: skip elements with no 3D body geometry (avoids "Representation is NULL" spam)
    if not has_body_representation(element):
        return None
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

            # STEP 1: Normalize units to meters (Unity/Unreal 1:1)
            mesh = normalize_units(mesh, ifc_file)

            # STEP 2: Convert Z-up to Y-up
            # NOTE: world X/Z coords are intentionally preserved here.
            # Storey elevation is subtracted later, once per merged GLB.
            mesh = convert_to_y_up(mesh)

            # STEP 3: Assign XR material
            # (normalize_coordinates removed — centering destroyed world positions)
            category = get_category(element)
            if category:
                material = create_xr_material(category)
                if material:
                    mesh.visual.material = material

            mesh.metadata['name'] = getattr(element, 'Name', 'Unnamed')
            mesh.metadata['ifc_type'] = element.is_a()
            mesh.metadata['category'] = category or 'unknown'

            return mesh
    except Exception as e:
        print(f"    Warning: Failed to extract mesh: {e}")
    return None

def simplify_mesh(mesh, target_faces=None):
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
    print(f"Opening IFC file: {ifc_path}")
    ifc_file = ifcopenshell.open(ifc_path)

    building_storeys = ifc_file.by_type('IfcBuildingStorey')
    print(f"Found {len(building_storeys)} building storeys")

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)

    # Compute unit scale once — reused for mesh vertices, elevations, and offsets
    unit_scale = get_unit_scale(ifc_file)
    print(f"Unit scale detected: {unit_scale} (IFC units → meters)")

    # Build storey elevation lookup: raw IFC storey name → elevation in meters
    # Used during GLB export to zero-out each storey's Y baseline.
    storey_elevations = {}
    for s in building_storeys:
        name = getattr(s, 'Name', None)
        elev = getattr(s, 'Elevation', None)
        if name is not None and elev is not None:
            storey_elevations[name] = round(float(elev) * unit_scale, 4)
    print(f"Storey elevations (m): { {k: v for k, v in sorted(storey_elevations.items(), key=lambda x: x[1])} }")

    storey_categories = defaultdict(lambda: defaultdict(list))
    spaces_data = defaultdict(list)

    print("\nProcessing elements...")

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
            storey = get_storey_name(element, ifc_file)
            if storey:
                elevation_m = get_storey_elevation(storey, ifc_file, unit_scale)
                space_info = {
                    'guid': getattr(element, 'GlobalId', None),
                    'type': ifc_type,
                    'name': getattr(element, 'Name', 'Unnamed'),
                    'long_name': getattr(element, 'LongName', ''),
                    'storey': storey,
                    'elevation_m': elevation_m,
                    'area': float(getattr(element, 'NetFloorArea', 0)) if getattr(element, 'NetFloorArea', None) else None,
                    'volume': float(getattr(element, 'Volume', 0)) if getattr(element, 'Volume', None) else None,
                    'category': category
                }
                spaces_data[storey].append(space_info)
        else:
            storey = get_storey_name(element, ifc_file)
            if not storey:
                continue

            mesh = extract_mesh(element, settings, ifc_file)
            if mesh and len(mesh.vertices) > 0:
                if ifc_type == 'IfcRailing':
                    mesh = simplify_mesh(mesh, target_faces=500)

                storey_categories[storey][category].append(mesh)

    # ============================================================
    # Export per-storey GLB files
    # ============================================================

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*50)
    print("Exporting per-storey GLB files...")
    print("="*50)

    exported_files = []

    for storey, categories in storey_categories.items():
        clean_name = clean_storey_name(storey)
        sanitized_name = sanitize_folder_name(clean_name)
        storey_folder = output_path / sanitized_name
        storey_folder.mkdir(parents=True, exist_ok=True)

        # Elevation to subtract so this storey's floor sits at Y=0 locally
        elev_m = storey_elevations.get(storey, 0.0)
        print(f"\n📁 Storey: {storey} -> {sanitized_name}  (elevation offset: -{elev_m:.3f} m)")

        for category, meshes in categories.items():
            if not meshes:
                continue

            print(f"  Merging {len(meshes)} meshes for {category}...")

            try:
                if len(meshes) == 1:
                    combined = meshes[0].copy()
                else:
                    combined = trimesh.util.concatenate(meshes)

                # Re-apply material after concatenate (trimesh may drop it)
                if meshes[0].visual.material:
                    combined.visual.material = meshes[0].visual.material

                # Subtract storey base elevation from Y only.
                # X and Z stay in IFC world space — this is the core fix.
                combined = apply_storey_elevation_offset(combined, elev_m)

                filename = f"{sanitized_name}_{category}.glb"
                filepath = storey_folder / filename

                combined.export(filepath, file_type='glb')

                file_size = filepath.stat().st_size / 1024
                print(f"    ✓ Exported: {filename} ({file_size:.1f} KB)")
                print(f"      Vertices: {len(combined.vertices)}, Faces: {len(combined.faces)}")

                exported_files.append(str(filepath))

            except Exception as e:
                print(f"    ✗ Failed to export {category}: {e}")

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
    print("\nTransforms applied:")
    print("  ✓ Unit scaling: IFC units → meters (Unity/Unreal 1:1)")
    print("  ✓ Coordinate system: IFC Z-up → Y-up (glTF/Three.js)")
    print("  ✓ World X/Z preserved: elements keep real IFC horizontal positions")
    print("  ✓ Storey elevation offset: each storey floor zeroed to Y=0 locally")
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
        print("XR materials + Y-up + meter scale + per-storey GLBs ready for WebXR")

    except FileNotFoundError:
        print(f"Error: IFC file not found at {ifc_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()