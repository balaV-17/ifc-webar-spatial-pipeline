TIME TRACK


DATE: 2026-05-27 to 2026-05-28
TOTAL HOURS: ~7 hours

HOUR 1 (18:00 - 19:00)
Read the assignment, understood the scope

AI Session #1: Asked about AI tools and project structure

Decision #1: Chose GitHub Copilot + GPT over Claude Code (learning over speed)

Created local folder structure instead of GitHub-first (saves time)

HOUR 2 (19:00 - 19:30)
Set up Python virtual environment

Installed IfcOpenShell, trimesh, numpy

Tested basic IFC parsing with open-source sample model

AI Session #2: Got minimal test_ifc.py script

Created diagnose_ifc.py to verify element types

HOUR 3 (20:00 - 21:00)
Encountered ifcopenshell.geom error with Python 3.14

AI Session #3: Diagnosed the issue

Decision #2: Downgraded to Python 3.11

Recreated virtual environment with Python 3.11

Reinstalled packages — geometry extraction now works

HOUR 4 (22:00 - 23:00)
Ran diagnose_ifc.py on the provided model

Got full element breakdown: 1,952 total elements, 18+ storeys

AI Session #4: Analyzed the data — confirmed it's an architectural model

Decision #3: Planned semantic batching strategy (structure, openings, circulation, MEP, spaces)

HOUR 5 (23:00 - 00:00)
Implemented batch_export_by_category.py

Ran first export — GLB files created, but storey names were raw German codes

AI Session #5: Asked about "Bad_*" folders

Decision #4: Added IfcBuildingStorey filtering + German-to-English name mapping

HOUR 6 (00:30 - 01:30)
Deleted old output folder and re-ran export

Clean structure achieved: GroundFloor, Level_01, Level_02, etc.

Each storey folder contains: structure.glb, openings.glb, circulation.glb, mep.glb, spaces.json

Decision #5: Documented the complete pipeline

Updated GitHub with clean, working code