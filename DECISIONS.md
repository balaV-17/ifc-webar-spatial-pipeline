DECISIONS
Decision #1 — 2026-05-27 23:00
Problem: Which AI tool to use for the pipeline — Claude Code vs. GitHub Copilot vs. GPT

AI Said: Use Claude Code as primary engineering partner for fastest results

I Did: Chose GitHub Copilot + GPT models, 50/50 AI-human split

Why: I want to learn the pipeline properly, not just get it done fast. This gives me a reusable template I can apply to future projects just by swapping models. I stay in control; AI handles the repetitive parts.

Geometry/IFC Related: No

Decision #2 — 2026-05-28 00:15
Problem: Python version for IfcOpenShell compatibility

AI Said: Downgrade to Python 3.11

I Did: Uninstalled Python 3.14, installed Python 3.11.9, recreated virtual environment

Why: IfcOpenShell's geometry module simply doesn't work with Python 3.14. The error was clear, and the fix worked immediately.

Geometry/IFC Related: Yes — geometry extraction depends on this

Decision #3 — 2026-05-28 01:30
Problem: How to group IFC elements for WebXR performance

AI Said: Group by storey first, then by semantic category (structure, openings, circulation, MEP, spaces)

I Did: Implemented exactly that in batch_export_by_category.py

Why: The model has 1,952 elements. Exporting each individually would mean 1,952 draw calls and terrible mobile performance. Batching reduces that to ~4-5 per storey — a 99% reduction.

Geometry/IFC Related: Yes — core export strategy

Decision #4 — 2026-05-28 02:45
Problem: Storey detection was creating folders for rooms (Bad_1367633) instead of only real storeys

AI Said: Filter to only IfcBuildingStorey elements; map German codes to English names

I Did: Added filtering and a clean name mapping (EG → GroundFloor, OG1 → Level_01, etc.)

Why: "Bad" means bathroom in German — the script was treating every spatial container as a storey. The fix keeps only actual building storeys and produces clean, English folder names.

Geometry/IFC Related: Yes — storey grouping is fundamental to the export hierarchy

Decision #5 — 2026-05-28 03:15
Problem: Script was appending exports on re-runs, creating duplicates

AI Said: Delete the output folder before re-running

I Did: rmdir /s output then re-ran the export — clean single set of files

Why: The script doesn't overwrite existing files. Deleting the folder ensures a clean slate every time.

Geometry/IFC Related: No — housekeeping