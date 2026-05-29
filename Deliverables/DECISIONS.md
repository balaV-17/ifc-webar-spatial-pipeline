Decision #1 — 2026-05-27 22:45
Problem: IFC parser choice — ifcopenshell vs web-ifc

AI Said: Use web-ifc for browser-native parsing, skip Python backend

I Did: Chose ifcopenshell Python pipeline

Why: web-ifc too new for "real-world messiness", ifcopenshell is industry standard

Geometry/IFC Related: Yes

Decision #2 — 2026-05-27 23:00
Problem: AI tool selection — Claude Code vs. GitHub Copilot vs. GPT

AI Said: Use Claude Code as primary engineering partner for fastest results

I Did: Chose GitHub Copilot + GPT models, 50/50 AI-human split

Why: I wanted to learn the pipeline properly, not just get it done fast. This gives me a reusable template I can apply to future projects just by swapping models. I stay in control; AI handles repetitive parts.

Geometry/IFC Related: No

Decision #3 — 2026-05-28 00:15
Problem: Python version for IfcOpenShell compatibility

AI Said: Downgrade to Python 3.11

I Did: Uninstalled Python 3.14, installed Python 3.11.9, recreated virtual environment

Why: IfcOpenShell's geometry module simply doesn't work with Python 3.14. The fix worked immediately.

Geometry/IFC Related: Yes — geometry extraction depends on this

Decision #4 — 2026-05-28 01:30
Problem: How to group IFC elements for WebXR performance

AI Said: Group by storey first, then by semantic category (structure, openings, circulation, MEP, spaces)

I Did: Implemented exactly that in batch_export_by_category.py

Why: The model has 1,952 elements. Exporting each individually would mean 1,952 draw calls and terrible mobile performance. Batching reduces that to ~4-5 per storey — a 99% reduction.

Geometry/IFC Related: Yes — core export strategy

Decision #5 — 2026-05-28 02:45
Problem: Storey detection was creating folders for rooms (Bad_1367633) instead of only real storeys

AI Said: Filter to only IfcBuildingStorey elements; map German codes to English names

I Did: Added filtering and clean name mapping (EG → GroundFloor, OG1 → Level_01, etc.)

Why: "Bad" means bathroom in German — the script was treating every spatial container as a storey. The fix keeps only actual building storeys.

Geometry/IFC Related: Yes — storey grouping is fundamental

Decision #6 — 2026-05-28 15:30
Problem: How to build WebXR viewer — from scratch or adapt old project

AI Said: Clone old project and modify

I Did: Cloned old project and stripped down to essentials

Why: Old project already has working Three.js + WebXR setup, UI components, and hit testing. Adapting is 10x faster than rebuilding.

Geometry/IFC Related: Yes — core visualization layer

Decision #7 — 2026-05-28 16:00
Problem: Which features from old project to keep vs. remove

AI Said: Keep navigation, floor toggles, teleport; remove placement, rotation, delete

I Did: Created a feature mapping table. Kept reticle (visual feedback), removed placement logic (commented out for now)

Why: This phase is about IFC visualization, not component placement. Simpler = faster delivery.

Geometry/IFC Related: Yes — viewer capabilities

Decision #8 — 2026-05-28 16:30
Problem: AR placement and anchoring still broken after multiple AI attempts

AI Said: Provided 4 different "fixes", each with new bugs

I Did: Abandoned AI-generated placement logic and implemented manual fix using getWorldPosition() + identity quaternion

Why: AI kept hallucinating matrix operations and ignored the working bounding-box offset that already aligned the model. Manual fix took 5 minutes and worked immediately.

Geometry/IFC Related: Yes — core AR interaction

Decision #9 — 2026-05-28 17:00
Problem: Which AI to use for UI logic going forward

AI Said: Claude Code is strongest for large codebases

I Did: Switched from ChatGPT to Claude Code for UI components

Why: ChatGPT gave good architecture but struggled with React + Three.js edge cases. Claude Code initially faster but hallucinated on placement. Now using hybrid: ChatGPT for planning, Claude Code for boilerplate, manual for critical AR logic.

Geometry/IFC Related: No

Decision #10 — 2026-05-29 10:45
Problem: Models float above ground, wrong scale, tilted orientation, no "All Floors" option

AI Said: Fix at the export level (Python script) rather than viewer level

I Did: Modified batch_export_by_category.py with unit conversion, orientation fix, origin normalization

Why: Fixing at the source ensures all future exports are correct. Viewer-side patches are temporary workarounds.

Geometry/IFC Related: Yes — core export pipeline

Decision #11 — 2026-05-29 11:00
Problem: Need "All Floors" merged GLB for UI toggle

AI Said: Export a merged GLB per category with storeys stacked at correct elevations

I Did: Added export_all_floors() function

Why: Users can toggle between single storey and full building view without loading multiple files

Geometry/IFC Related: Yes — export optimization

Decision #12 — 2026-05-29 11:15
Problem: IFC units (mm) vs Three.js units (meters) mismatch

AI Said: Apply scale factor 0.001 during vertex extraction

I Did: Added SCALE_FACTOR = 0.001 to convert mm to meters

Why: Ensures 1:1 real-world scale in AR placement

Geometry/IFC Related: Yes — unit conversion

Decision #13 — 2026-05-29 11:30
Problem: IFC uses Z-up, Three.js uses Y-up → models tilt

AI Said: Swap Y and Z axes during vertex transformation

I Did: Added convert_to_y_up() function

Why: Models now stand upright without manual rotation in viewer

Geometry/IFC Related: Yes — coordinate system conversion

Decision #14 — 2026-05-29 11:45
Problem: Model spawns offset from reticle because pivot point is at geometry center, not bottom

AI Said: Normalize origin to bottom-center of bounding box

I Did: Added normalize_origin_to_bottom_center() function

Why: When placed at reticle (ground level), model sits exactly on surface, not floating

Geometry/IFC Related: Yes — pivot point correction

Decision #15 — 2026-05-29 14:45
Problem: Python-side transforms (trimesh) were unreliable — models still tilted or floating

AI Said: Do rotation and origin normalization in Three.js viewer instead

I Did: Moved Z-up → Y-up rotation, centering, and bottom alignment to ARView.tsx

Why: Three.js transforms are immediate, testable, and don't require re-exporting GLBs. Much faster iteration.

Geometry/IFC Related: Yes — coordinate system conversion

Decision #16 — 2026-05-29 15:00
Problem: Models had no materials — looked flat and unprofessional

AI Said: Inject XR PBR materials in Three.js based on category

I Did: Added applyMaterials() function with realistic PBR properties

Why: Visual polish matters for presentation. Materials make the model look like a real product.

Geometry/IFC Related: No — visual enhancement

Decision #17 — 2026-05-29 15:15
Problem: V3 combined export failing with KeyError because parent nodes didn't exist

AI Said: Remove parent_node_name, use flat scene structure with prefixed names

I Did: Refactored export_combined_glb() to use flat node hierarchy

Why: Flat structure is simpler, more reliable, and still allows storey/category filtering via name parsing

Geometry/IFC Related: Yes — export optimization

Decision #18 — 2026-05-29 15:30
Problem: V3 combined export still failing with KeyError despite multiple fixes (V3.2, V3.3)

AI Said: Continue debugging trimesh scene graph hierarchy

I Did: Abandoned combined export in main pipeline; created separate combine_meshV1.py script

Why: Individual exports are working perfectly. Combined export is nice-to-have but not blocking. Deadline is near.

Geometry/IFC Related: Yes — export pipeline separation

Decision #19 — 2026-05-29 16:00
Problem: "Failed to extract mesh: Representation is NULL" warnings spam console

AI Said: Ignore — these are IFC elements with no 3D geometry

I Did: Kept as warnings (not errors) — they don't affect successful geometry extraction

Why: These are normal in IFC files. Many elements (IfcSpace, IfcOpeningElement) have no mesh representation by default.

Geometry/IFC Related: Yes — IFC parsing reality

DECISION #20 — 2026-05-29 16:15
Problem: Model loads upside down (facing ground)
AI Said: Apply default rotation in ARView.tsx
I Did: Added modelGroup.rotation.y = Math.PI (180°) as default
Why: The IFC orientation conversion missed one axis. Quick fix is better than re-exporting all GLBs.
Geometry/IFC Related: Yes — orientation fix

═══════════════════════════════════════════════════
DECISION #21 — 2026-05-29 16:30
Problem: "All Floors" button not loading combined GLB
AI Said: Check path and ensure combinedMesh folder exists
I Did: Verified path public/models/combinedMesh/building_combined.glb and updated loading logic
Why: Combined GLB was exported but not being loaded due to wrong path in viewer
Geometry/IFC Related: No — asset loading

═══════════════════════════════════════════════════
DECISION #22 — 2026-05-29 16:45
Problem: UI toggles were single-select, not multi-select
AI Said: Change from selectedStorey: string to activeStoreys: object
I Did: Implemented multi-select toggle buttons for storeys
Why: Users need to see multiple floors stacked (e.g., GroundFloor + Level_01 together) for spatial understanding
Geometry/IFC Related: Yes — core UI interaction

═══════════════════════════════════════════════════
DECISION #23 — 2026-05-29 17:00
Problem: Storey elevation stacking not working
AI Said: Apply Y-offset based on elevation from spaces.json
I Did: Added getStoreyElevation() function and applied position.y offset when loading each storey
Why: Without elevation offset, all storeys overlap at Y=0
Geometry/IFC Related: Yes — spatial stacking

| Hallucination                                                                           | Impact                |
| --------------------------------------------------------------------------------------- | --------------------- |
| Matrix copy misuse — `anchorGroup.matrix.copy(reticle.matrix)` copied unwanted rotation | Model tilted 90°      |
| Removing `adjustModelBottomToAnchor` — broke ground alignment                           | Model floating        |
| Claiming “model auto-aligns to surface normal” — not true for planar surfaces           | Wasted 1 hour         |
| Circular fixes — alternating between two broken approaches, never converging            | Delayed placement fix |


