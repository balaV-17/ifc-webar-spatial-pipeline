# IFC to GLB Export Pipeline

## Overview

This pipeline converts any IFC (Industry Foundation Classes) BIM model into optimized GLB files ready for AR/WebXR visualization.
[Watch Demo](https://youtu.be/GlctptoFtcw)

**What it does:**
- Parses IFC files using ifcopenshell
- Extracts storeys (floors) and translates German naming conventions
- Categorizes elements: structure, openings, circulation, MEP, spaces
- Applies XR-ready PBR materials
- Normalizes units (mm → meters) and orientation (Z-up → Y-up)
- Preserves world coordinates (X, Z) while normalizing storey ground to Y=0
- Exports individual GLB files per storey and category
- Optionally combines all storeys into a single stacked GLB

---

## Requirements

### System Requirements
- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** Version 3.11 (3.12+ may cause compatibility issues with ifcopenshell)
- **RAM:** 8GB minimum (16GB recommended for large IFC files)
- **Storage:** 2GB free space for temporary files

---
## Quick Start

### Step 1: Clone or Download the Repository

```bash
git clone https://github.com/your-repo/ifc-webar-spatial-pipeline.git
cd ifc-webar-spatial-pipeline
```

### Step 2: Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt

**Note:** If `ifcopenshell` installation fails on Windows, download the pre-compiled wheel from [IfcOpenShell Releases](https://github.com/IfcOpenShell/IfcOpenShell/releases). Look for a file matching `ifcopenshell-*.whl` for Python 3.11 and Windows.

### Step 4: Verify Installation

```bash
python -c "import ifcopenshell; print('IfcOpenShell OK')"
python -c "import trimesh; print('Trimesh OK')"
python -c "import numpy; print('NumPy OK')"
```

Expected output:
```
IfcOpenShell OK
Trimesh OK
NumPy OK
```

---

## Usage

### Step 1: Prepare Your IFC File

Place your IFC file in the `data/` folder:

```
data/
└── sample.ifc
```

### Step 2: Export Individual Storey GLBs

```bash
python scripts/batch_export_by_category.py data/sample.ifc output
```

**What this does:**
- Parses the IFC file
- Exports one GLB per storey per category
- Creates `spaces.json` with room metadata for each storey

### Step 3: (Optional) Combine All Storeys into One GLB

```bash
python scripts/combine_mesh.py output output_combinedMesh
```

**What this does:**
- Reads all exported GLB files from the `output/` folder
- Stacks storeys at their correct elevations (from `spaces.json`)
- Creates a single `building_combined.glb` with named mesh groups


## Command Reference

| Command | Description |
|---------|-------------|
| `python scripts/batch_export_by_category.py <ifc_path> <output_dir>` | Export individual storey GLBs |
| `python scripts/combine_meshV1.py <input_dir> <output_dir>` | Combine all storeys into one GLB |

### Arguments

**batch_export_by_category.py**
| Argument | Description | Default |
|----------|-------------|---------|
| `ifc_path` | Path to input IFC file | `data/sample.ifc` |
| `output_dir` | Output directory for GLB files | `output` |

**combine_meshV1.py**
| Argument | Description | Default |
|----------|-------------|---------|
| `input_dir` | Directory containing storey folders | `output` |
| `output_dir` | Output directory for combined GLB | `output_combinedMesh` |

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'ifcopenshell'` | Run `pip install ifcopenshell` |
| `ImportError: IfcOpenShell not built for 'python3.11'` | Download the correct wheel from GitHub releases |
| `Warning: Failed to extract mesh: Representation is NULL` | Safe to ignore — some IFC elements have no geometry |
| `KeyError: 'storey_01_GroundFloor'` | Run individual export first, then combined script |
| Model appears flat in AR | Ensure you're using the combined GLB for "All Floors" view |



## Project Structure

```
ifc-webar-spatial-pipeline/
├── .venv/                          # Virtual env (gitignored)
├── data/
│   └── sample.ifc                  # Your IFC file
├── scripts/
│   ├── batch_export_by_categoryV3.py
│   └── combine_meshV1.py
├── output/                         # Auto-generated (gitignored)
├── output_combinedMesh/            # Auto-generated (gitignored)
├── AI_log.md
├── DECISIONS.md
├── TIME.md
├── README.md                       # Updated with clean docs
├── requirements.txt
├── .gitignore                      # Updated
└── SPEC.md                         # Project original spec ( Updated on the first day)

---
Note
Important: The output/ and output_combinedMesh/ folders are created automatically when you run the scripts. They are ignored by git to keep the repository clean.

Next Steps
After running the pipeline, you will have GLB files ready for WebXR visualization.

👉 Proceed to Phase 2: Use the [webar-construction-validation-tool](https://github.com/balaV-17/WebAR_Construction_Validation_Tool) to view the GLB in AR.

License
This project is for demonstration purposes as part of the BIM-AR Validation Tool assignment.

Created by Balaji Velu