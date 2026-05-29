"""Quick test to verify exported GLB files"""
from pathlib import Path
import trimesh
import numpy as np

test_file = Path('output/GroundFloor/GroundFloor_structure.glb')

if test_file.exists():
    print(f"Loading: {test_file}")
    scene = trimesh.load(str(test_file))
    
    # GLB is a scene — iterate geometries
    for name, geom in scene.geometry.items():
        print(f"\n  Geometry: {name}")
        print(f"    Type: {type(geom).__name__}")
        
        if hasattr(geom, 'vertices'):
            print(f"    Vertices: {len(geom.vertices)}")
            print(f"    Faces: {len(geom.faces)}")
            print(f"    Bounds: {geom.bounds}")
            
            extents = geom.extents
            x, y, z = extents
            print(f"    X extent: {x:.2f}")
            print(f"    Y extent: {y:.2f}  <-- should be tallest for Y-up")
            print(f"    Z extent: {z:.2f}")
            
            if y > x and y > z:
                print("    ✅ Y-up (standing upright)")
            elif z > x and z > y:
                print("    ⚠️  Z-up (lying flat — NEEDS ROTATION)")
            else:
                print("    ⚠️  Unclear orientation")
            
            # Check if centered at origin
            center = (geom.bounds[0] + geom.bounds[1]) / 2
            print(f"    Center: {center}")
            if np.linalg.norm(center) < 1.0:
                print("    ✅ Centered near origin")
            else:
                print("    ⚠️  Far from origin — needs centering")
        
        # Check material
        if hasattr(geom.visual, 'material') and geom.visual.material:
            print(f"    ✅ Material: {type(geom.visual.material).__name__}")
            if hasattr(geom.visual.material, 'baseColorFactor'):
                print(f"       Color: {geom.visual.material.baseColorFactor}")
        else:
            print(f"    ⚠️  No material")
            
else:
    print(f"File not found: {test_file}")