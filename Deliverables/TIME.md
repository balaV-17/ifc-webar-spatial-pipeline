Project Timeline
Start: 2026-05-27 ~19:00
End: 2026-05-29 ~17:00
Total Duration: ~48 hours (on and off)

Day 1 — Wednesday, May 27
Time	Activity
19:00 - 20:00	Read assignment, wrote SPEC.md, understood scope
20:00 - 21:00	AI session: technical concepts (parser, routing, analysis)
21:00 - 21:30	AI session: tool selection — decided on GPT + Copilot (50/50 split)
22:00 - 23:00	Set up project structure, virtual environment, initial Git
23:00 - 00:00	AI session: basic IFC parsing test — test_ifc.py created
End of Day 1 — 5 hours

Day 2 — Thursday, May 28
Time	Activity
09:00 - 10:00	Geometry extraction debugging — Python 3.11 downgrade, venv recreation
11:00 - 12:00	IFC analysis on provided model — 1,952 elements, 18+ storeys
13:00 - 14:00	Created batch_export_by_category.py — semantic batching
14:00 - 15:00	Fixed storey detection (German names, "Bad" filtering)
15:00 - 16:00	Cloned old WebXR project, adapted UI components
16:00 - 17:00	AR placement debugging — Claude Code hallucinations, manual fix
17:00 - 18:00	UI adaptation continued — storey selector, category toggles
20:00 - 22:00	ARView.tsx fixes — rotation, centering, bottom alignment
22:00 - 00:00	Added spaces overlay, "ALL" storey button, elevation slider
End of Day 2 — 11 hours

Day 3 — Friday, May 29
Time	Activity
10:00 - 11:00	Export pipeline fixes — mm→m, Z-up→Y-up, origin centering
11:00 - 12:00	"All Floors" merged GLB design
12:00 - 13:00	V3 export script — individual GLBs only
14:00 - 15:00	Switched transforms from Python to Three.js (more reliable)
15:00 - 16:00	Added XR PBR materials
16:00 - 17:00	Combined export debugging — KeyError, decided to separate scripts
End of Day 3 — 6 hours

Documentation & Wrap-up — Friday, May 29
Time	Activity
15:00 - 16:00	Revised AI_log.md, DECISIONS.md, TIME.md
16:00 - 17:00	Final testing, README updates, repo cleanup
17:00	Submission preparation
Total Time Breakdown
Phase	Hours
Spec & planning	~2
IFC parsing & geometry extraction	~4
Batch export development	~6
WebXR viewer adaptation	~8
AR placement debugging	~3
Export pipeline fixes (V2, V3)	~4
Documentation	~3
Total	~30 hours
Hour Distribution by Activity Type
AI-assisted coding (prompts, reviewing outputs, integrating): ~12 hours

Manual coding (geometry transforms, AR placement fix, UI adaptation): ~10 hours

Debugging (Python version, KeyError, placement): ~5 hours

Documentation (SPEC, DECISIONS, TIME, README): ~3 hours

What Went Well
IFC parsing and storey detection worked first time after Python fix

Batch export reduced draw calls by 99%

Old project UI adapted cleanly to IFC categories

Manual AR placement fix took 5 minutes after AI hallucinations failed

What Was Challenging
Python 3.14 incompatibility with ifcopenshell — lost 1 hour

Combined export KeyError — abandoned in main pipeline

AR placement logic — AI gave 4 wrong fixes before manual solution

What I Would Do Differently
Start with Python 3.11 from the beginning

Not spend time on combined export in main pipeline — separate script from start

Trust manual AR placement logic over AI-generated matrix operations