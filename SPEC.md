<div align="center">

# Vambiant AR / Spatial Computing Assignment

## Track E — IFC → WebXR Field Intelligence Layer

**Spatial Computing Prototype | BIM-to-AR Pipeline | 48-Hour Assignment**

</div>

<p align="center">
  <a href="#context"><strong>Context</strong></a> ·
  <a href="#project-goal"><strong>Goal</strong></a> ·
  <a href="#pipeline"><strong>Pipeline</strong></a> ·
  <a href="#scope"><strong>Scope</strong></a> ·
  <a href="#technical-direction"><strong>Tech</strong></a> ·
  <a href="#success-criteria"><strong>Criteria</strong></a>
</p>

---

## Overview

| | |
|:---|:---|
| **Author** | [Balaji Velu] |
| **Role Target** | AR / Spatial Computing Developer |
| **Duration** | 48 Hours |
| **Status** | Specification written before implementation |

---

## 1. Context

> Most BIM workflows stop at geometry inspection.

A model is exported, reviewed on a desktop monitor, and disconnected from the physical environment where the building is actually constructed. Yet the stated goal of Vambiant's platform is fundamentally spatial: allowing field workers and engineers to visualize building intelligence directly inside real environments.

This project is designed around that gap.

Rather than treating IFC as a static BIM artifact, this assignment treats IFC as a **spatial data source for real-time augmented reality workflows**.

The objective is therefore not only to parse geometry correctly, but to establish a complete pipeline:

```
IFC → Geometry Processing → Semantic Structuring → WebXR Visualization
```

The result is a lightweight, field-facing WebXR prototype capable of loading IFC-derived geometry into an augmented reality environment directly from the browser — with no native application installation required.

---

## 2. Project Goal

Build a spatial computing pipeline that:

- [x] Parses a real IFC building model
- [x] Extracts structural and MEP geometry
- [x] Converts BIM geometry into optimized runtime assets
- [x] Organizes assets semantically by storey and system type
- [x] Visualizes the result in an interactive WebXR experience
- [x] Allows spatial inspection, semantic filtering, and contextual overlays in AR

The final deliverable demonstrates how BIM information can transition from a desktop coordination artifact into a **field-usable spatial interface**.

---

## 3. Why This Track

The provided assignment examples primarily focus on:

- Routing algorithms
- Floor plan generation
- Geometry analysis
- Voxel processing

Those are valuable BIM engineering exercises. However, the target role for this submission is **AR / Spatial Computing Developer**.

This project therefore intentionally shifts focus toward:

| Domain | Focus |
|:---|:---|
| **Spatial Visualization** | Real-world AR rendering of BIM data |
| **Real-World Alignment** | Surface detection and model placement |
| **Browser-Based XR Delivery** | WebXR, no native app required |
| **Semantic Interaction** | Layer toggles, storey isolation, element selection |
| **Runtime Geometry Optimization** | Lightweight mobile-first performance |

The goal is not to compete on the complexity of BIM tooling alone, but to demonstrate understanding of the **final spatial product layer** that construction teams ultimately interact with.

---

## 4. Concept Overview

The proposed system acts as a lightweight **"Field Intelligence Layer"** for BIM data.

A user opens a WebXR session on a mobile device and places a building model onto a detected real-world surface. Structural and MEP systems can then be explored spatially using semantic filters, storey isolation, and contextual overlays.

### Core Principles

| Principle | Description |
|:---|:---|
| **Spatial Clarity** | Only the information relevant to the current task should be visible |
| **Semantic Navigation** | The building is explored through systems, storeys, and element categories rather than raw mesh complexity |
| **Runtime Simplicity** | Heavy BIM processing occurs before runtime so that the WebXR layer remains lightweight and performant on mobile hardware |

---

## 5. Existing Foundation

This project builds upon a previously developed WebXR prototype focused on AR-based MEP component placement. That prototype already demonstrated:

- WebXR session management
- Hit-testing and surface detection
- Reticle-based placement
- Anchor persistence
- GLB loading via Three.js
- Mobile-first AR interaction
- Runtime model placement workflows

### Extension

| From | To |
|:---|:---|
| Manually placed static GLB assets | Dynamically processed IFC-derived building geometry |

The existing prototype serves as the **interaction layer**, while this assignment introduces:

- IFC ingestion
- Geometry preprocessing
- Semantic extraction
- BIM-aware visualization

---

## 6. High-Level Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  INGESTION                                                      │
│  IFC File → IfcOpenShell parsing → Element + storey extraction  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PROCESSING                                                     │
│  Geometry conversion → Mesh cleanup + optimization              │
│  → Storey grouping → Semantic metadata extraction               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  EXPORT                                                         │
│  Optimized GLB assets + JSON metadata manifests                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  VISUALIZATION                                                  │
│  Three.js runtime → WebXR scene                                 │
│  → Spatial overlays + interaction                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Technical Direction

### 7.1 IFC Processing

The preprocessing pipeline will:

- Extract structural shell geometry
- Extract MEP systems
- Normalize coordinates
- Organize assets by storey
- Export lightweight runtime meshes

| Technology | Purpose |
|:---|:---|
| **IfcOpenShell** | IFC parsing and geometry extraction |
| **trimesh** | Mesh processing and optimization |
| **shapely** | 2D geometry operations |
| **Python 3.11** | Pipeline orchestration |

### 7.2 Runtime Visualization

The frontend runtime will:

- Load optimized GLB assets
- Visualize semantic layers
- Support WebXR placement
- Provide fallback desktop viewing
- Enable spatial interaction

| Technology | Purpose |
|:---|:---|
| **Three.js** | 3D rendering engine |
| **WebXR Device API** | Immersive AR session management |
| **GLTFLoader** | Runtime GLB asset loading |
| **Vite** | Build tooling and dev server |

---

## 8. Scope

### 8.1 Included

#### IFC Extraction

- [x] Walls
- [x] Slabs
- [x] Columns
- [x] Beams
- [x] Pipe systems
- [x] Duct systems
- [x] Cable systems
- [x] Storey hierarchy
- [x] IFC property metadata

#### Geometry Processing

- [x] Mesh extraction
- [x] Coordinate normalization
- [x] Storey grouping
- [x] Runtime optimization
- [x] GLB export

#### WebXR Runtime

- [x] Surface placement
- [x] Storey visibility
- [x] Semantic toggles
- [x] Element interaction
- [x] Layer isolation
- [x] Spatial overlays

#### Documentation

- [x] `SPEC.md`
- [x] `DECISIONS.md`
- [x] `TIME.md`
- [x] `README.md`

### 8.2 Explicitly Out of Scope

| Excluded | Reason |
|:---|:---|
| Persistent SLAM anchoring | Outside realistic 48-hour scope |
| Multi-user networking | Requires separate synchronization infrastructure |
| Full BIM editing | Read-only visualization is correct scope |
| Native mobile apps | Browser delivery aligns better with assignment |
| Full routing algorithms | Focus remains spatial visualization |
| Furniture / interior assets | Low spatial value for this prototype |

> These exclusions are intentional and reflect prioritization discipline rather than missing functionality.

---

## 9. Architectural Philosophy

The project intentionally separates **heavy BIM computation** from **lightweight XR rendering**.

| Approach | Rationale |
|:---|:---|
| **Offline preprocessing → lightweight runtime visualization** | IFC geometry is computationally expensive; mobile XR performance is constrained; runtime stability is critical; preprocessing enables semantic optimization |

This decision was made because:

- IFC geometry is computationally expensive
- Mobile XR performance is constrained
- Runtime stability is critical
- Preprocessing enables semantic optimization

---

## 10. Runtime User Experience

### 10.1 AR Flow

```
┌─────────────────┐
│ Open WebXR app  │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Detect surfaces │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Place model     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Structural shell│
│ appears         │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Toggle MEP      │
│ systems         │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Navigate by     │
│ storey          │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Select element  │
│ → metadata      │
└─────────────────┘
```

### 10.2 Desktop Fallback

If immersive AR is unavailable, the same scene loads in a **desktop orbit viewer**, preserving semantic interaction and visualization logic. This ensures the project remains fully reviewable regardless of hardware availability.

---

## 11. Success Criteria

The project is considered successful if:

| # | Criterion | Status |
|:---|:---|:---:|
| 1 | IFC geometry parses successfully | ⬜ |
| 2 | Storeys are extracted correctly | ⬜ |
| 3 | Runtime GLBs load in browser | ⬜ |
| 4 | WebXR session initializes on mobile | ⬜ |
| 5 | Semantic layer toggles function | ⬜ |
| 6 | Storey isolation functions | ⬜ |
| 7 | Element interaction works | ⬜ |
| 8 | Runtime performance remains stable on mobile hardware | ⬜ |

---

## 12. Risk Areas

| Risk | Mitigation |
|:---|:---|
| IFC coordinate inconsistencies | Coordinate normalization pipeline |
| Large geometry payloads | Mesh decimation + storey segmentation |
| WebXR browser inconsistencies | Fallback 3D viewer |
| Missing MEP geometry | Graceful layer degradation |
| Mobile rendering performance | Runtime optimization and mesh reduction |

---

## 13. AI Usage Strategy

AI tools will be used selectively for:

- Boilerplate generation
- Repetitive scaffolding
- API lookup acceleration
- Frontend iteration

**Manually controlled areas:**

- Coordinate transformation logic
- IFC parsing decisions
- Geometry normalization
- WebXR spatial behavior
- Architectural decisions

> This is intentional because spatial and geometry workflows are precisely where AI-generated implementations are most likely to hallucinate or introduce subtle runtime errors.

---

## 14. Intended Outcome

The objective of this project is not merely to produce another BIM viewer.

The objective is to demonstrate a believable future workflow where **BIM intelligence**, **spatial computing**, and **field interaction** exist inside the same runtime experience.

The submission is therefore positioned as a **spatial computing prototype**, not a generalized BIM platform.

---

## 15. Final Note

This specification was intentionally written **before implementation begins**.

The purpose is to establish:

- Scope
- Architecture
- Technical direction
- Engineering priorities

...before any code generation occurs.

---

<div align="center">

**Built for the spatial computing layer of construction workflows.**

</div>
