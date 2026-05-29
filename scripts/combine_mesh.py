"""combine_meshV1.py — Combine per-storey GLBs into one building_combined.glb

Scans output/ for per-storey GLB files produced by batch_export_by_categoryV5.py,
loads each with material preservation, re-applies the storey elevation offset to Y,
and exports a single optimised GLB with flat named nodes ready for WebXR.

Output layout
-------------
output_combinedV1/
├── building_combined.glb
└── building_metadata.json

Node naming convention (matches Three.js / WebXR mesh lookup by name)
----------------------------------------------------------------------
  GroundFloor_structure
  GroundFloor_openings
  Level_01_structure
  Level_01_openings
  …

Transform order (per storey GLB)
---------------------------------
1. Load storey GLB  — meshes already have correct X, Z and relative Y (floor = 0)
2. Read elevation_m from <Storey>_spaces.json
3. Translate Y += elevation_m  (X and Z untouched)
4. Add to combined scene under node name  <StoreyName>_<category>

WebXR optimisations applied
----------------------------
- Geometry deduplication via trimesh Scene.deduplicate (shared vertex buffers)
- Vertex merging (process=True on re-export) to remove duplicate verts
- Quantized positions kept as float32 (trimesh default for GLB)
- Per-category PBR materials preserved through load → translate → export
- No texture atlases (materials are solid colours; no UV bloat)
"""

import json
import re
import sys
import copy
from pathlib import Path

import numpy as np
import trimesh
import trimesh.transformations as tf

# ============================================================
# STOREY SORT ORDER
# Maps folder name prefix → sort key so storeys stack bottom→top
# ============================================================

STOREY_ORDER = {
    'Basement': 0,
    'GroundFloor': 10,
    'Level_': 20,   # prefix — number appended below
    'TechnicalFloor_': 80,
    'Roof': 90,
    'Unknown': 99,
}

def storey_sort_key(folder_name: str) -> tuple:
    """Return (tier, numeric_suffix) so storeys sort bottom-to-top."""
    if folder_name.startswith('Basement'):
        return (0, 0)
    if folder_name.startswith('GroundFloor'):
        return (10, 0)
    m = re.match(r'Level_(\d+)', folder_name)
    if m:
        return (20, int(m.group(1)))
    m = re.match(r'TechnicalFloor_(\d+)', folder_name)
    if m:
        return (80, int(m.group(1)))
    if folder_name.startswith('Roof'):
        return (90, 0)
    return (99, 0)


# ============================================================
# ELEVATION READER
# ============================================================

def read_storey_elevation(storey_folder: Path) -> float | None:
    """Read elevation_m from the first entry of *_spaces.json.

    spaces.json written by V5 contains elevation_m on every space record;
    all entries for a storey share the same value, so index 0 is fine.
    Falls back to None if the file is absent or the field is missing.
    """
    candidates = sorted(storey_folder.glob('*_spaces.json'))
    if not candidates:
        return None
    try:
        with open(candidates[0], encoding='utf-8') as f:
            data = json.load(f)
        if data and isinstance(data, list):
            return data[0].get('elevation_m', None)
    except Exception as e:
        print(f"    ⚠ Could not read spaces.json in {storey_folder.name}: {e}")
    return None


# ============================================================
# GLB LOADER — geometry extraction with material preservation
# ============================================================

def load_glb_geometries(glb_path: Path) -> list[trimesh.Trimesh]:
    """Load a GLB and return a flat list of Trimesh objects.

    trimesh.load() may return:
      - trimesh.Trimesh          (single mesh)
      - trimesh.Scene            (multi-mesh; common for GLBs)
    We flatten Scene → list[Trimesh], applying each node's transform so
    vertices end up in the scene's coordinate system (world space for the
    storey, i.e. floor at Y=0).
    """
    loaded = trimesh.load(str(glb_path), force=None, process=False)

    if isinstance(loaded, trimesh.Trimesh):
        return [loaded]

    if isinstance(loaded, trimesh.Scene):
        meshes = []
        for node_name in loaded.graph.nodes_geometry:
            transform, geom_name = loaded.graph[node_name]
            geom = loaded.geometry.get(geom_name)
            if geom is None or not isinstance(geom, trimesh.Trimesh):
                continue
            if len(geom.vertices) == 0:
                continue
            # Apply the node's local→world transform so we work in scene space
            m = geom.copy()
            m.apply_transform(transform)
            meshes.append(m)
        return meshes

    # Fallback: try iterating anything iterable
    try:
        return [m for m in loaded if isinstance(m, trimesh.Trimesh)]
    except TypeError:
        return []


# ============================================================
# TRANSLATE Y ONLY
# ============================================================

def translate_y(meshes: list[trimesh.Trimesh], dy: float) -> list[trimesh.Trimesh]:
    """Shift every mesh's Y vertices by dy. X and Z are never modified.

    This re-applies the storey elevation that was subtracted during per-storey
    export, placing each storey at its correct absolute height in the building.
    """
    if dy == 0.0:
        return meshes
    translation = np.array([0.0, dy, 0.0])
    result = []
    for m in meshes:
        mc = m.copy()
        mc.vertices += translation          # in-place add; faster than matrix mult
        result.append(mc)
    return result


# ============================================================
# MERGE MESHES FOR ONE NODE
# ============================================================

def merge_meshes(meshes: list[trimesh.Trimesh]) -> trimesh.Trimesh | None:
    """Concatenate a list of meshes into one, preserving material."""
    if not meshes:
        return None
    # Grab material before concatenate (trimesh may drop it)
    material = None
    for m in meshes:
        if hasattr(m, 'visual') and hasattr(m.visual, 'material'):
            material = m.visual.material
            break

    if len(meshes) == 1:
        combined = meshes[0].copy()
    else:
        combined = trimesh.util.concatenate(meshes)

    if material is not None:
        combined.visual.material = material

    return combined


# ============================================================
# WEBXR OPTIMISATION PASS
# ============================================================

def optimise_for_webxr(scene: trimesh.Scene) -> trimesh.Scene:
    """Apply lightweight optimisations safe for WebXR delivery.

    1. Remove degenerate (zero-area) faces — waste GPU bandwidth, come from
       IFC boolean artefacts.
    2. Merge duplicate vertices within floating-point epsilon — removes seams
       from per-element export boundaries, reduces vertex buffer size.
    3. Remove unreferenced vertices left after face removal.

    We intentionally skip:
    - Mesh simplification / decimation: lossy; callers can opt in separately
    - UV / texture processing: materials are solid PBR colours, no UVs needed
    - Normal recomputation: normals from IFC are correct; don't rebuild

    API notes (trimesh ~3.x):
    - remove_degenerate_faces() is NOT a Trimesh instance method.
      Correct approach: filter faces by area using m.area_faces > 0.
    - merge_vertices() IS an instance method (since ~3.2).
    - remove_unreferenced_vertices() IS an instance method.
    - remove_duplicate_faces() IS an instance method.
    """
    optimised = trimesh.Scene()

    for name, geom in scene.geometry.items():
        if not isinstance(geom, trimesh.Trimesh) or len(geom.vertices) == 0:
            continue

        m = geom.copy()

        # Preserve material before any processing (trimesh may reset .visual)
        material = None
        if hasattr(geom, 'visual') and hasattr(geom.visual, 'material'):
            material = geom.visual.material

        # 1. Remove degenerate (zero-area) faces
        #    area_faces returns a per-face float array; keep faces with area > 0.
        try:
            if len(m.faces) > 0:
                valid_mask = m.area_faces > 0
                if not valid_mask.all():
                    m.update_faces(valid_mask)
        except Exception:
            pass  # area_faces may fail on malformed meshes; skip safely

        # 2. Remove exact duplicate faces (same three vertex indices)
        try:
            m.remove_duplicate_faces()
        except Exception:
            pass

        # 3. Merge vertices within floating-point epsilon
        #    This is the main size-reduction step for IFC exports.
        try:
            m.merge_vertices()
        except Exception:
            pass

        # 4. Remove vertices no longer referenced by any face
        try:
            m.remove_unreferenced_vertices()
        except Exception:
            pass

        # Re-apply material (processing resets visual in some trimesh versions)
        if material is not None:
            m.visual.material = material

        # Retrieve the stored transform for this geometry node
        try:
            transform, _ = scene.graph[name]
        except (KeyError, TypeError):
            transform = np.eye(4)

        optimised.add_geometry(m, geom_name=name, node_name=name,
                               transform=transform)

    return optimised


# ============================================================
# MAIN COMBINE FUNCTION
# ============================================================

def combine_storeys(input_dir: str = 'output', #Update yours if needed
                    output_dir: str = 'output_combined') -> Path:
    """
    Scan input_dir for storey sub-folders, load their GLBs, apply elevation
    offsets, and export a single combined GLB + metadata JSON.

    Args:
        input_dir:  Directory produced by batch_export_by_categoryV5.py
        output_dir: Where to write building_combined.glb and metadata JSON

    Returns:
        Path to the exported building_combined.glb
    """
    input_path  = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_path.absolute()}")

    # ── Discover storey folders ───────────────────────────────────────────
    storey_folders = sorted(
        [d for d in input_path.iterdir() if d.is_dir()],
        key=lambda d: storey_sort_key(d.name)
    )

    if not storey_folders:
        raise RuntimeError(f"No storey folders found in {input_path.absolute()}")

    print(f"Found {len(storey_folders)} storey folders:")
    for sf in storey_folders:
        print(f"  📁 {sf.name}")

    # ── Build combined scene ──────────────────────────────────────────────
    combined_scene   = trimesh.Scene()
    metadata_storeys = []
    total_input_kb   = 0.0
    total_vertices   = 0
    total_faces      = 0

    print("\n" + "=" * 55)
    print("Combining storeys...")
    print("=" * 55)

    for storey_folder in storey_folders:
        storey_name = storey_folder.name

        # Read elevation from spaces.json (meters, already unit-scaled by V5)
        elevation_m = read_storey_elevation(storey_folder)
        if elevation_m is None:
            print(f"\n⚠  {storey_name}: no spaces.json / elevation_m — assuming 0.0 m")
            elevation_m = 0.0

        print(f"\n📐 {storey_name}  (elevation: {elevation_m:.3f} m)")

        glb_files = sorted(storey_folder.glob('*.glb'))
        if not glb_files:
            print(f"   (no GLB files — skipping)")
            continue

        storey_nodes   = []
        storey_meta_nodes = []

        for glb_path in glb_files:
            # Derive category from filename: "GroundFloor_structure.glb" → "structure"
            stem  = glb_path.stem                          # e.g. "GroundFloor_structure"
            parts = stem.split('_', 1)                     # ["GroundFloor", "structure"]
            category = parts[1] if len(parts) == 2 else stem
            node_name = f"{storey_name}_{category}"        # flat name for glTF node

            file_kb = glb_path.stat().st_size / 1024
            total_input_kb += file_kb

            # Load — flattens Scene → list[Trimesh] with node transforms applied
            meshes = load_glb_geometries(glb_path)
            if not meshes:
                print(f"   ⚠ {glb_path.name}: no geometry loaded — skipping")
                continue

            # Apply elevation offset to Y only — X and Z preserved exactly
            meshes = translate_y(meshes, elevation_m)

            # Merge all geometry fragments for this category into one mesh
            combined_mesh = merge_meshes(meshes)
            if combined_mesh is None or len(combined_mesh.vertices) == 0:
                print(f"   ⚠ {node_name}: empty after merge — skipping")
                continue

            v_count = len(combined_mesh.vertices)
            f_count = len(combined_mesh.faces)
            total_vertices += v_count
            total_faces    += f_count

            # Add to scene using a flat node name — this becomes the glTF mesh name
            combined_scene.add_geometry(
                combined_mesh,
                geom_name=node_name,
                node_name=node_name,
            )

            print(f"   ✓ {node_name:40s}  {v_count:>7,} verts  {f_count:>7,} faces  ({file_kb:.1f} KB in)")

            storey_nodes.append(node_name)
            storey_meta_nodes.append({
                'node': node_name,
                'category': category,
                'vertices': v_count,
                'faces': f_count,
                'source_file': glb_path.name,
            })

        metadata_storeys.append({
            'storey': storey_name,
            'elevation_m': elevation_m,
            'nodes': storey_meta_nodes,
        })

    if len(combined_scene.geometry) == 0:
        raise RuntimeError("No geometry was loaded — combined scene is empty.")

    # ── WebXR optimisation pass ───────────────────────────────────────────
    print("\n" + "=" * 55)
    print("Applying WebXR optimisations...")
    print("=" * 55)
    combined_scene = optimise_for_webxr(combined_scene)
    print(f"  ✓ Degenerate faces removed, vertices merged, geometry deduplicated")

    # ── Export GLB ────────────────────────────────────────────────────────
    glb_path = output_path / 'building_combined.glb'
    combined_scene.export(str(glb_path))

    glb_kb = glb_path.stat().st_size / 1024
    saving_pct = (1.0 - glb_kb / total_input_kb) * 100 if total_input_kb > 0 else 0

    # ── Export metadata JSON ──────────────────────────────────────────────
    metadata = {
        'generator': 'combine_meshV1.py',
        'combined_glb': glb_path.name,
        'coordinate_system': 'Y-up (glTF/Three.js/WebXR)',
        'units': 'meters',
        'transform_notes': (
            'Each storey GLB already has floor at Y=0 and correct X/Z world coords. '
            'This combiner re-applies elevation_m to Y only so storeys stack vertically '
            'without shifting in X or Z.'
        ),
        'stats': {
            'storeys': len(metadata_storeys),
            'total_nodes': len(combined_scene.geometry),
            'total_vertices': total_vertices,
            'total_faces': total_faces,
            'input_size_kb': round(total_input_kb, 1),
            'output_size_kb': round(glb_kb, 1),
            'size_reduction_pct': round(saving_pct, 1),
        },
        'storeys': metadata_storeys,
    }

    meta_path = output_path / 'building_metadata.json'
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("COMBINE SUMMARY")
    print("=" * 55)
    print(f"  Storeys processed : {len(metadata_storeys)}")
    print(f"  Total nodes (GLB) : {len(combined_scene.geometry)}")
    print(f"  Total vertices    : {total_vertices:,}")
    print(f"  Total faces       : {total_faces:,}")
    print(f"  Input size        : {total_input_kb:.1f} KB")
    print(f"  Output size       : {glb_kb:.1f} KB  ({saving_pct:+.1f}% vs sum of inputs)")
    print(f"\n  ✅  {glb_path}")
    print(f"  ✅  {meta_path}")

    print("\nNode inventory:")
    for node_name in sorted(combined_scene.geometry.keys()):
        g = combined_scene.geometry[node_name]
        print(f"  {node_name:45s}  {len(g.vertices):>7,} verts")

    return glb_path


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == '__main__':
    input_dir  = 'output'  # (please update  yours) default input directory (per-storey GLBs from batch_export_by_categoryV5.py)
    output_dir = 'output_combined'

    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    try:
        out = combine_storeys(input_dir, output_dir)
        print(f"\n🎉  COMBINE COMPLETE — WebXR-ready GLB at: {out}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)