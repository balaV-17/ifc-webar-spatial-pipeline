AI CHAT LOG


Session #1 — 2026-05-27 — Project Setup & Tool Selection 
Topic: Choosing the right AI tools and project structure for a 48-hour IFC-to-WebXR pipeline

Prompt:

"Could you check on the internet or youtube and give me sample images or demo videos, so that i can have an idea of the process and final similar product. also guide me which ai should i go and purchase for : claude code or gpt or gemnin to create this pipeline, should I use vscode copilot or claude code or codex ? which subscription will help me to finish this project within the timeline."

Response:

Recommended Claude Code as the primary engineering partner due to strong large-scale codebase reasoning and multi-file generation. Suggested VS Code + GitHub Copilot for autocomplete, with ChatGPT for architecture and debugging. Advised against Gemini as primary due to weaker geometry reasoning.

What I Did:

Modified before using

Decided to go with GitHub Copilot + GPT models instead of Claude Code

Reasoning: I want to learn step by step, not finish in 2 hours. Building a reusable template pipeline matters more than speed.

Notes:
AI pushed for Claude Code as the fastest path. I chose a 50/50 approach — AI assists, I stay in control. This gives me a clean, documented pipeline I can reuse for future projects just by swapping models.

Session #2 — 2026-05-27 — IFC Parsing Test
Topic: Testing basic IFC file parsing with an open-source model

Prompt:

"Create a minimal Python script using IfcOpenShell that opens an IFC file from data/sample.ifc, prints project name, number of IfcWall elements, and number of IfcSlab elements. Handle file errors cleanly. Do not add visualization yet."

Response:

Provided complete test_ifc.py script with error handling. Test output showed: Project Name: Undefined, IfcWall: 0, IfcSlab: 2.

What I Did:

Used as-is

Then asked ChatGPT to create scripts/diagnose_ifc.py to verify what was actually in the file

Cross-checked by opening the model in a viewer — confirmed the file has 2 slabs, 0 walls

Notes:
The sample IFC file was slab-only. No walls. That's fine — confirmed by visual inspection.

Session #3 — 2026-05-28 — Geometry Extraction Error
Topic: ifcopenshell.geom module not found

Prompt:

Copy-pasted error: "Error: module 'ifcopenshell' has no attribute 'geom'" plus Python version 3.14

Response:

Explained that IfcOpenShell's geometry module doesn't work with Python 3.14.5. Recommended downgrading to Python 3.11 and recreating the virtual environment.

What I Did:

Modified before using

Downgraded to Python 3.11 per recommendation

Ran test_geom.py and extract_geometry_v2.py — both worked

Deleted the old script and renamed v2 to the standard name

Notes:
Python version compatibility is critical for IfcOpenShell. 3.11 is the stable target.

Session #4 — 2026-05-28 — IFC Analysis & Batch Export Strategy
Topic: Analyzing the provided IFC model and planning semantic batching for WebXR

Prompt:

"Analyze the IFC data present and optimize for mobile WebXR. Categorize into Level_01, Level_02, Level_03 with systems per storey and asked to further categorize systems as: structure, openings, circulation, MEP, spaces"

Response:

Confirmed the IFC is an architectural spatial visualization model — perfect for the assignment. Said better with the recomend method than exporting every element individually.

What I Did:

Used as-is

Created batch_export_by_category.py following the recommended hierarchy

Ran the script — successfully exported GLB files grouped by storey and category
Found error with the export structures and files which I adressed in the next session.

Notes:
The model has 1,952 total elements. Exporting each individually would kill mobile WebXR performance. 

Session #5 — 2026-05-28 — German Storey Names Fix
Topic: Fixing storey detection — "Bad" means bathroom, not an error

Prompt:

"The export is working but shows folders like Bad_1367633 and German codes (EG, OG1). What about our Level_01, Level_02 structure?"

Response:

Explained that "Bad" means bathroom in German — those were rooms/spaces being mistaken as storeys. Provided fix: filter to only IfcBuildingStorey elements and add a mapping for German codes (EG → GroundFloor, OG1 → Level_01, etc.).

What I Did:

Modified before using

Added the sanitization and German name mapping to the batch export script

Re-ran export — output now clean: GroundFloor, Level_01, Level_02, etc.

Notes:
The IFC's storey names were professional German codes (OKRD EG, OKRD OG1, etc.). The fix maps them to clean English names without losing any data. Batching by category reduced draw calls by ~99%.

