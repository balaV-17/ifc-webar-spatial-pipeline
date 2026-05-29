Note: This log captures the essential AI interactions. Due to the volume (70+ pages), only representative sessions are included. The complete raw logs are available if required.

Session #1 — 2026-05-27 ~19:00 — ChatGPT
Topic: Understanding assignment scope and choosing between Path 1 (Unity) vs Path 2 (Python IFC pipeline)

Prompt:

"I want to know two things: Unity IFC parser and data prep in Unity and then exporting as GLB and using Three.js and WebXR loading the model — this is Path 1. Path 2: IFC file → ifcopenshell parses elements, extracts geometry → trimesh decimates + groups by storey → shapely computes floor footprints → glTF per storey + JSON metadata → FastAPI serves assets → Three.js loads in browser. Are these different paths or can they be combined?"

Response:
AI explained that Path 1 is a "Unity-Centric Asset Pipeline" (good for visuals, fast results, your strength) and Path 2 is a "Computational Geometry Pipeline" (what the assignment expects for IFC reasoning and analysis). Recommended combining both: Path 2 for preprocessing + analysis, Path 1 for rendering + AR interaction.

What I did:

Used as-is for strategic planning

Notes:
The key insight was that the assignment wants "ingestion → analysis → visualization" — the middle word "analysis" is what makes this different from a simple viewer. Decided to build the Python pipeline first, then adapt my existing WebXR viewer.

Session #2 — 2026-05-27 ~20:00 — ChatGPT
Topic: Understanding technical concepts (IFC parser, semantic extraction, routing engine, spatial graph generation, geometry analysis, IFC → GLB preprocessing)

Prompt:

"Give me basic understanding into these topics with a real world example: IFC parser, semantic extraction, routing engine, spatial graph generation, geometry analysis, IFC → GLB preprocessing."

Response:
AI provided a "big picture first" explanation of each concept with practical examples in the context of BIM, digital twins, indoor navigation, and building automation.

What I did:

Used as reference

Notes:
Helped me understand what "analysis" actually means in this context — routing, free-space analysis, storey segmentation, footprint extraction, topology. This shaped how I structured the export categories.

Session #3 — 2026-05-27 ~21:00 — ChatGPT
Topic: AI tool selection for the pipeline

Prompt:

"Check on the internet and give me sample images or demo videos of similar products. Also guide me which AI should I purchase — Claude Code, GPT, or Gemini? Should I use VS Code Copilot, Claude Code, or Codex? Which subscription will help me finish this project within the timeline?"

Response:
AI recommended Claude Code as primary engineering partner (strongest large-scale codebase reasoning, best at multi-file generation). Suggested VS Code + GitHub Copilot for autocomplete, ChatGPT for architecture and debugging.

What I did:

Modified before using

Notes:
I decided to go with GitHub Copilot + GPT models instead of Claude Code. Reason: I wanted to learn the pipeline step by step, not finish in 2 hours. I wanted to build a reusable template pipeline where I can save it on GitHub and use it for all projects just by swapping models. 50/50 AI-human split — I stay in control.

Session #4 — 2026-05-27 ~22:30 — ChatGPT (Kimi for structure)
Topic: Project structure for IFC-to-AR demo

Prompt:

"Give me a proper professional project structure using the following content and eliminate the extras based on 48-hour scope."

Response:
AI suggested a detailed structure with FastAPI backend, tests, static folder, etc.

What I did:

Modified before using

Notes:
The AI-suggested structure was overkill for a 48-hour sprint. I modified it to focus on: data/, scripts/, output/, webxr/, and documentation files. Skipped Docker (added to README as future step). Created local folder first instead of GitHub-first (speed priority).

Session #5 — 2026-05-27 ~23:45 — Claude
Topic: Basic IFC parsing test script

Prompt:

"Create a minimal Python script using IfcOpenShell that opens an IFC file from data/sample.ifc, prints project name, number of IfcWall elements, and number of IfcSlab elements. Handle file errors cleanly. Do not add visualization yet."

Response:
AI provided complete test_ifc.py script with error handling.

What I did:

Used as-is

Then asked ChatGPT to create scripts/diagnose_ifc.py to cross-check what was actually in the file

Verified by opening the model in a viewer — confirmed 2 slabs, 0 walls

Notes:
The sample IFC file was slab-only. That's fine — confirmed by visual inspection.

Session #6 — 2026-05-28 ~00:30 — Claude
Topic: Geometry extraction error — ifcopenshell.geom not found

Prompt:

Copy-pasted error: "Error: module 'ifcopenshell' has no attribute 'geom'" plus Python version 3.14

Response:
AI explained that IfcOpenShell's geometry module doesn't work with Python 3.14.5. Recommended downgrading to Python 3.11 and recreating the virtual environment.

What I did:

Modified before using

Downgraded to Python 3.11

Ran test_geom.py and extract_geometry_v2.py — both worked

Deleted the old script and renamed v2 to the standard name

Notes:
Python version compatibility is critical for IfcOpenShell. 3.11 is the stable target.

Session #7 — 2026-05-28 ~01:30 — DeepSeek V4
Topic: IFC analysis and batch export strategy for WebXR

Prompt:

"Analyze the IFC data and optimize for mobile WebXR. Categorize into Level_01, Level_02, Level_03 with systems per storey."

Response:
AI confirmed the IFC is an architectural spatial visualization model — perfect for the assignment. Recommended grouping by storey first, then by system category: structure, openings, circulation, MEP, spaces. Warned against exporting every element individually.

What I did:

Used as-is

Created batch_export_by_category.py following the recommended hierarchy

Notes:
The model has 1,952 total elements. Exporting each individually would kill mobile WebXR performance. Batching by category reduced draw calls by ~99%.

Session #8 — 2026-05-28 ~02:30 — DeepSeek V4
Topic: Fixing storey detection — "Bad" means bathroom, not an error

Prompt:

"The export shows folders like Bad_1367633 and German codes (EG, OG1). What about our Level_01, Level_02 structure?"

Response:
AI explained that "Bad" means bathroom in German — those were rooms/spaces being mistaken as storeys. Provided fix: filter to only IfcBuildingStorey elements and add a mapping for German codes (EG → GroundFloor, OG1 → Level_01, etc.).

What I did:

Modified before using

Added sanitization and German name mapping to the batch export script

Re-ran export — output clean: GroundFloor, Level_01, Level_02, etc.

Notes:
The IFC's storey names were professional German codes (OKRD EG, OKRD OG1, etc.). The fix maps them to clean English names without losing any data.

Session #9 — 2026-05-28 ~15:00 — DeepSeek V4 (after break)
Topic: Adapting old WebXR project UI for IFC viewer

Prompt:

"Here are screenshots of my old project's UI. I want to keep the UI as is including the reticle. Now with this UI, what is our plan for the current Vambiant demo project?"

Response:
AI analyzed the old UI components and mapped them to IFC requirements — NAV → STOREYS, LAYERS → SYSTEMS, PLACE BUILDING → SPACES. Recommended keeping the visual layout but renaming labels and simplifying logic.

What I did:

Used as-is for UI inspiration

Modified functionality mapping

Notes:
The old UI has three states: Home (pre-AR), AR with collapsed panels, AR with expanded panels. This layout is perfect for IFC viewing.

Session #10 — 2026-05-28 ~16:00 — Claude Code
Topic: Fixing AR placement and anchoring — hallucination issues

Prompt:

"Fix the AR placement and anchoring in ARView.tsx. The model should spawn exactly at the reticle, sit flat on the ground, and stay world-locked when placed."

Response:
Claude provided multiple code patches over several messages. Each patch introduced new problems. Hallucinations included:

Using anchorGroup.matrix.copy(reticle.matrix) — copied unwanted rotation, causing tilt

Removing adjustModelBottomToAnchor — broke ground alignment

Claiming "model auto-aligns to surface normal" — not true for planar surfaces

Alternating between two broken approaches, never converging

What I did:

Rejected / used as reference only

Notes:
None of Claude's fixes worked. The only reliable solution came from manual implementation using getWorldPosition() + identity quaternion.

Session #11 — 2026-05-29 ~10:30 — DeepSeek V4
Topic: Fixing IFC export pipeline at the source (origin, scale, orientation, All Floors)

Prompt:

"Let's fix the IFC parser export to solve placement issues at the source: 1:1 scale, origin/pivot point, Y-up vs Z-up orientation, and export a merged 'All Floors' GLB."

Response:
AI analyzed root causes and provided plan: mm → meter conversion (0.001), Z-up → Y-up orientation (swap Y and Z), bottom-center origin normalization, merged "All Floors" GLB export per category.

What I did:

Used as-is for planning

Notes:
Decided to fix issues at the export level rather than patching in the viewer. This makes all future exports correct automatically.

Session #12 — 2026-05-29 ~14:30 — DeepSeek V4
Topic: Switching transformations from Python export to Three.js runtime

Prompt:

"I corrected the coordinates by doing rotation and origin normalization in Three.js instead of Python. It worked."

Response:
AI acknowledged the successful pivot. Agreed that doing transformations in Three.js is more reliable and debuggable than fighting trimesh's export pipeline.

What I did:

Used as-is

Notes:
Python export now focuses on raw geometry extraction (mm → m, Z-up preservation). Transformations (rotation, origin centering, bottom alignment) happen in ARView.tsx at load time. This is faster to debug and gives per-model control.

Session #13 — 2026-05-29 ~16:30 — Claude Code
Topic: Fixing export_combined_glb() parent node KeyError

Prompt:

"Bug in export_combined_glb() — when adding geometry with parent_node_name, trimesh.Scene.add_geometry() doesn't create the parent node automatically."

Response:
AI identified the issue and suggested removing parent_node_name, using flat scene structure with prefixed names.

What I did:

Used as-is

Notes:
Removed hierarchical parent-child relationships. Combined export now uses flat scene graph with prefixed names like storey_00_OkAttika_structure, storey_01_GroundFloor_structure, etc.

Session #14 — 2026-05-29 ~16:30 — DeepSeek V4
Topic: Separating individual and combined GLB exports into two scripts

Prompt:

"Persistent KeyError despite multiple fixes. Decided to split into two scripts: V3 for individual exports only, plus separate combine_meshV1.py for merging."

Response:
AI acknowledged the decision. Recommended keeping individual exports as primary pipeline.

What I did:

Modified before using

Notes:
Time critical — deadline approaching. Combined export is nice-to-have but not blocking. Individual exports work perfectly. This separation keeps the pipeline clean.

SESSION #15 — 2026-05-29 16:45 — Claude Code
Topic: Final UI fixes — All Floors button, model orientation (upside down fix)
═══════════════════════════════════════════════════

PROMPT:
"Fix the following:

'All Floors' button not loading building_combined.glb from public/models/combinedMesh/

Model loads upside down (faces toward ground). Rotating 180° fixes it. Apply this rotation by default."

RESPONSE:
AI provided fixes for both issues:

Added correct path for combined GLB: combinedMesh/building_combined.glb

Added default rotation to ARView.tsx to fix upside-down orientation

WHAT I DID:
[X] Used as-is
[ ] Modified before using
[ ] Rejected / used as reference only

NOTES:
The model orientation issue was caused by IFC's Z-up vs Three.js Y-up conversion not fully handling all axes. The quick fix applies a default rotation of 180° around Y-axis to make the model face upright.

SESSION #16 — 2026-05-29 16:45 — Claude Code
Topic: Multi-storey loading implementation
═══════════════════════════════════════════════════

PROMPM:
"Implement multi-storey loading. Current UI toggles are single-select. Need multi-select where L1 and L2 can be active simultaneously, stacked vertically. 'All Floors' button loads combinedMesh/building_combined.glb."

RESPONSE:
AI provided updated code for StoreySelector.tsx (multi-select toggles), types.ts (activeStoreys object), and ARView.tsx (load multiple storeys with elevation stacking).

WHAT I DID:
[X] Used as-is

NOTES:
Multi-storey loading now works. Each storey toggles independently. When multiple storeys are active, they load at their respective elevations (from spaces.json) at the same anchored position.