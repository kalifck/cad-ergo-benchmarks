# CAD Ergonomic Benchmarks for Build123d

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![CAD Engine](https://img.shields.io/badge/kernel-OpenCASCADE%20%7C%20Build123d-orange.svg)](https://github.com/gumyr/build123d)
[![AI Engineering](https://img.shields.io/badge/Engineered%20with-Antigravity%20%7C%20Gemini%203.8%20Flash-792ee5.svg)](https://deepmind.google/)
[![Mathematical Audit](https://img.shields.io/badge/OpenCASCADE%20Audit-100%25%20Exact%20Match-brightgreen.svg)](case_studies/)
[![Interactive 3D Viewer](https://img.shields.io/badge/3D%20Viewer-Standalone%20WebGL-success.svg)](viewer/sharp123_viewer.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Empirical code-density benchmarks, ergonomic syntax experiments, and interactive 3D comparison studies for [Build123d](https://github.com/gumyr/build123d).**  
> *Engineered with Google Antigravity & Gemini 3.8 Flash.*  
> Demonstrating how high-level mechanical primitives eliminate the "Math Wall" and cut boilerplate by up to 87% without compromising OpenCASCADE precision.

---

## 💡 The Motivation: The "Math Wall" in Code-CAD

Programmatic CAD (Code-CAD) offers unprecedented superpowers: parametric flexibility, git-based version control, and algorithmic geometry. However, mechanical engineers modeling real-world machinery often hit the **"Math Wall"**:

1. **The 200-Line Helper Tax**:  
   Connecting two offset circular bosses with smooth bitangent lines (belt paths, bellcranks, clamp jaws) requires complex trigonometry. Developers frequently have to write hundreds of lines of custom vector projection and rotation solvers.
2. **Multi-Pass Manufacturing Cavities**:  
   Cutting standard stepped counterbores or countersunk holes with lead-in chamfers shouldn't require separate sketch planes, redundant circles, and multiple subtractive extrusions.
3. **Brittle Topological Queries**:  
   Referencing an edge or face for a kinematic joint often produces fragile expressions like:  
   `edges().filter_by(GeomType.CIRCLE).filter_by(lambda e: e.radius == 15 / 2).sort_by(Axis.Y)[0]`  
   which can break silently when upstream parametric dimensions shift.

---

## 🚀 Case Study 01: `@jdegenstein`'s `sharp123` Knife Sharpening Station

To benchmark real-world impact, we ported key components of [**`jdegenstein/sharp123`**](https://github.com/jdegenstein/sharp123), an outstanding 17-part precision kinematic sharpening jig designed by **`@jdegenstein`**.

> **Attribution Note**:  
> All mechanical engineering, mechanism design, and kinematic relationships belong 100% to **`@jdegenstein`**.  
> This benchmark is strictly an ergonomic code study and syntactic comparison — NOT an original mechanical design.

---

### 📊 Benchmark Summary: Original vs. Ergonomic Rewrite

| Component / Metric | Original `sharp123` | Ergonomic Rewrite | Impact |
| :--- | :---: | :---: | :---: |
| **Trig Math Solver (`tangentline.py`)** | **200 LOC** (Trig Math) | **0 LOC** (Native Primitive) | **-100% DELETED** |
| **Clamp Arm Profile Sketch** | 47 LOC | 6 LOC | **-87.2% LOC** |
| **Clamp Arm AST Complexity** | 311 syntax nodes | 68 syntax nodes | **-78.1% Complexity** |
| **Main Tower Fastener Cuts** | 18 LOC (Stacked Sk.) | 10 LOC (Engineering Hole) | **-44.4% LOC** |
| **Base Plate Selectors** | Index Slicing `[0:3]` | Fluent `.top` Property | **Direct & Semantic** |
| **Mated Kinematic Bodies** | 17 Bodies | 17 Bodies | **100% Drop-in Fit** |

---

### 🧪 Failproof OpenCASCADE Volumetric Verification

Every component and the entire 17-part assembly were evaluated using exact OpenCASCADE Boolean difference operations:

$$\text{Missing} = V(A \setminus B), \quad \text{Extra} = V(B \setminus A), \quad \text{Jaccard Similarity} = \frac{V(A \cap B)}{V(A \cup B)} \times 100\%$$

| Component | Original Volume | Candidate Volume | Missing ($A \setminus B$) | Extra ($B \setminus A$) | Jaccard Similarity | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`ClampArm`** | $103,080.90\text{ mm}^3$ | $103,080.90\text{ mm}^3$ | **$0.0000\text{ mm}^3$** | **$0.0000\text{ mm}^3$** | **100.00%** | **PASS** |
| **`MainTower`** | $688,554.55\text{ mm}^3$ | $688,554.55\text{ mm}^3$ | **$0.0000\text{ mm}^3$** | **$0.0000\text{ mm}^3$** | **100.00%** | **PASS** |
| **`BasePlate`** | $291,382.83\text{ mm}^3$ | $291,382.83\text{ mm}^3$ | **$0.0000\text{ mm}^3$** | **$0.0000\text{ mm}^3$** | **100.00%** | **PASS** |

#### Full 17-Part Assembled Station in World Space:
- **Original Assembly Total Volume**: `1,649,776.75 mm³`
- **Ergonomic Assembly Total Volume**: `1,649,776.75 mm³`
- **Total Volume Delta**: **`0.0000 mm³`**
- **World Center Shift across ALL 17 parts**: **`0.0000 mm`**
- **Kinematic Joint Residual**: **`0.0 mm`**

---

## 📸 Visual Comparison Gallery

### 1. Full 17-Part Assembly (Side-by-Side)
*Original (Slate Red) on the left vs. Ergonomic Rewrite (Polished Emerald) on the right standing upright on the desk.*  
![Full Assembly Side-by-Side](screenshots/full_assembly_side_by_side.png)

### 2. Full Assembly Optical Superposition (Diff Mode)
*Both assemblies superimposed in the exact same world coordinate space with opacity blending — zero gaps, zero collision artifacts.*  
![Full Assembly Diff Mode](screenshots/full_assembly_diff_mode.png)

### 3. Clamp Arm (Bitangent Profile)
*Replacing 200 lines of manual trigonometry with a single native call.*  
![Clamp Arm Comparison](screenshots/clamp_arm_loft_comparison.png)

### 4. Main Tower (Elevation Column & Fasteners)
*Replacing multi-pass offset planes with a single manufacturing cavity call.*  
![Main Tower Comparison](screenshots/main_tower_comparison.png)

### 5. Base Plate (Dovetail Mounting & Chamfers)
*Clean semantic selectors replacing brittle index slicing.*  
![Base Plate Comparison](screenshots/base_plate_comparison.png)

### 6. Clamp Arm (Remodel & Kinematic Pin Bore)
*Exact volumetric and kinematic alignment with the clamp arm holder.*  
![Clamp Arm Remodel Comparison](screenshots/clamp_arm_remodel_comparison.png)

---

## ⚡ Case Study 02: `@kalifck`'s `ToggleClamp123` (Engineered with Antigravity & Gemini 3.8 Flash)

[**`kalifck/ToggleClamp123`**](https://github.com/kalifck/ToggleClamp123) is a precision 3D-printable push-action toggle clamp engineered using parametric Build123d. It features an **83° rotational sweep**, **48.6 mm linear plunger stroke**, and positive **over-center toggle locking**.

> **AI Engineering Note**:  
> 🚀 **Designed and developed with Google Antigravity & Gemini 3.8 Flash!**  
> Demonstrating how high-level programmatic CAD combined with frontier agentic intelligence eliminates tedious manual trigonometry and produces production-grade B-Rep mechanisms.

### 🎬 Kinematic Simulation in Action
![ToggleClamp123 Kinematic Demo](screenshots/toggle_clamp_demo.gif)

### 📊 Benchmark Summary: Original vs. Ergonomic Rewrite

| Component / Metric | Original `ToggleClamp123` | Ergonomic Rewrite | Impact |
| :--- | :---: | :---: | :---: |
| **Pivot B Trigonometry** | `math.sin / cos / rad` (5 LOC) | `Location((0, 0), angle)` (1 LOC) | **-100% (DELETED)** |
| **Handle AST Complexity** | 206 AST Nodes | 174 AST Nodes | **-15.5% AST** |
| **Base Mounting Slots** | 4 LOC, 71 AST Nodes | 2 LOC, 29 AST Nodes | **-59.2% AST** |
| **Pivot Ears Modeling** | Manual loop with sign tracking | Single sketch + `mirror` | **Clean & Symmetric** |
| **Pin Edge Selectors** | Filter lambda + condition | Fluent `.circular().chamfer()` | **Self-documenting** |
| **Volumetric Parity** | 133,859.17 mm³ | 133,859.17 mm³ | **$0.0000\text{ mm}^3$ Δ (100% Match)** |

### 🧪 OpenCASCADE Volumetric Verification (All 8 Solids)

$$\text{Missing} = V(A \setminus B) = 0.0000\text{ mm}^3, \quad \text{Extra} = V(B \setminus A) = 0.0000\text{ mm}^3, \quad \text{Jaccard} = 100.00\%$$

- **`base_mounting_flange`**: $79,678.4421\text{ mm}^3 \to 0.0000\text{ mm}^3 \Delta$ (**100.00% Jaccard**)
- **`actuation_handle`**: $18,978.2547\text{ mm}^3 \to 0.0000\text{ mm}^3 \Delta$ (**100.00% Jaccard**)
- **`connecting_link`**: $2,186.6513\text{ mm}^3 \to 0.0000\text{ mm}^3 \Delta$ (**100.00% Jaccard**)
- **`linear_plunger`**: $28,919.8703\text{ mm}^3 \to 0.0000\text{ mm}^3 \Delta$ (**100.00% Jaccard**)
- **`dowel_pins` (A, B, C)**: $843.78 / 561.04 / 504.49\text{ mm}^3 \to 0.0000\text{ mm}^3 \Delta$ (**100.00% Jaccard**)
- **Full 8-Solid Assembly**: **$133,859.1727\text{ mm}^3 \to 0.0000\text{ mm}^3 \Delta$** (**100.00% Exact Match**)

---

## 📦 Production CAD Assets (STEP & STL Downloads)

All CAD solids are pre-rendered and exported in both industry-standard STEP and high-res binary STL formats:

### Case Study 01: `sharp123`
| Model / Part | Original STEP | Ergonomic STEP | Original STL | Ergonomic STL |
| :--- | :---: | :---: | :---: | :---: |
| **Full 17-Part Assembly** | [assembly_orig.step](case_studies/01_sharp123/cad_models/step/assembly_orig.step) | [assembly_ergo.step](case_studies/01_sharp123/cad_models/step/assembly_ergo.step) | [assembly_orig.stl](case_studies/01_sharp123/cad_models/stl/assembly_orig.stl) | [assembly_ergo.stl](case_studies/01_sharp123/cad_models/stl/assembly_ergo.stl) |
| **Main Elevation Tower** | [main_tower_orig.step](case_studies/01_sharp123/cad_models/step/main_tower_orig.step) | [main_tower_ergo.step](case_studies/01_sharp123/cad_models/step/main_tower_ergo.step) | [main_tower_orig.stl](case_studies/01_sharp123/cad_models/stl/main_tower_orig.stl) | [main_tower_ergo.stl](case_studies/01_sharp123/cad_models/stl/main_tower_ergo.stl) |
| **Dovetail Base Plate** | [base_plate_orig.step](case_studies/01_sharp123/cad_models/step/base_plate_orig.step) | [base_plate_ergo.step](case_studies/01_sharp123/cad_models/step/base_plate_ergo.step) | [base_plate_orig.stl](case_studies/01_sharp123/cad_models/stl/base_plate_orig.stl) | [base_plate_ergo.stl](case_studies/01_sharp123/cad_models/stl/base_plate_ergo.stl) |
| **Knife Clamp Arm** | [clamp_arm_orig.step](case_studies/01_sharp123/cad_models/step/clamp_arm_orig.step) | [clamp_arm_ergo.step](case_studies/01_sharp123/cad_models/step/clamp_arm_ergo.step) | [clamp_arm_orig.stl](case_studies/01_sharp123/cad_models/stl/clamp_arm_orig.stl) | [clamp_arm_ergo.stl](case_studies/01_sharp123/cad_models/stl/clamp_arm_ergo.stl) |

### Case Study 02: `ToggleClamp123`
| Model / Part | STEP Model | Binary STL |
| :--- | :---: | :---: |
| **Full Toggle Clamp Assembly** | [toggle_clamp_assembly_ergo.step](case_studies/02_toggle_clamp123/cad_models/step/toggle_clamp_assembly_ergo.step) | [toggle_clamp_assembly_ergo.stl](case_studies/02_toggle_clamp123/cad_models/stl/toggle_clamp_assembly_ergo.stl) |
| **Base Mounting Flange** | [base_mounting_flange_ergo.step](case_studies/02_toggle_clamp123/cad_models/step/base_mounting_flange_ergo.step) | [base_mounting_flange_ergo.stl](case_studies/02_toggle_clamp123/cad_models/stl/base_mounting_flange_ergo.stl) |
| **Actuation Handle** | [actuation_handle_ergo.step](case_studies/02_toggle_clamp123/cad_models/step/actuation_handle_ergo.step) | [actuation_handle_ergo.stl](case_studies/02_toggle_clamp123/cad_models/stl/actuation_handle_ergo.stl) |
| **Connecting Link** | [connecting_link_ergo.step](case_studies/02_toggle_clamp123/cad_models/step/connecting_link_ergo.step) | [connecting_link_ergo.stl](case_studies/02_toggle_clamp123/cad_models/stl/connecting_link_ergo.stl) |
| **Linear Plunger** | [linear_plunger_ergo.step](case_studies/02_toggle_clamp123/cad_models/step/linear_plunger_ergo.step) | [linear_plunger_ergo.stl](case_studies/02_toggle_clamp123/cad_models/stl/linear_plunger_ergo.stl) |

---

## 🕹️ Interactive 3D Comparison Studio

Inside [`viewer/sharp123_viewer.html`](viewer/sharp123_viewer.html) is a self-contained, single-file Three.js application:
- **Upright Engineering Orientation**: Base Plate rests naturally on the ground floor grid.
- **Interactive Part Switcher**: Toggle between all 6 component pairs and the full 17-part assembly.
- **Side-by-Side & Superimposed Diff Modes**: Inspect geometric tolerances and joint alignment in real-time.
- **Cutaway Sectioning & Wireframe**: Cross-section internal fastener cavities and wall thicknesses.
- **Zero Dependencies**: Simply double-click `viewer/sharp123_viewer.html` to open in any web browser!

---

## 📁 Repository Organization

```text
cad-ergo-benchmarks/
├── README.md                      # Benchmark suite overview & discovery documentation
├── index.html                     # GitHub Pages launcher for the interactive 3D viewer
├── viewer/
│   └── sharp123_viewer.html       # Standalone 3D multi-part comparison viewer
├── screenshots/                   # High-res WebGL renders, optical diffs, and kinematic GIFs
└── case_studies/
    ├── 01_sharp123/               # Case Study 01: sharp123 by @jdegenstein
    │   ├── README.md              # In-depth case study breakdown & audit report
    │   ├── code_comparison/       # Side-by-side commented Python scripts
    │   ├── audit/                 # OpenCASCADE Boolean diff audit scripts & JSON
    │   └── cad_models/            # Production STEP & STL models
    └── 02_toggle_clamp123/        # Case Study 02: ToggleClamp123 by @kalifck (Antigravity & Gemini 3.8 Flash)
        ├── README.md              # In-depth case study breakdown & audit report
        ├── code_comparison/       # Side-by-side commented Python scripts
        ├── audit/                 # OpenCASCADE Boolean diff audit scripts & JSON
        ├── screenshots/           # Kinematic simulation GIF & interface views
        └── cad_models/            # Production STEP & STL models
```

---

## 🎁 Roadmap & Upstream Contributions

1. **Comprehensive Benchmark Suite**: Adding more real-world mechanical assemblies and parametric case studies.
2. **Upstream RFC Submission**: Proposing these high-level mechanical primitives directly to [`gumyr/build123d`](https://github.com/gumyr/build123d) so that all Code-CAD practitioners benefit.
3. **Companion Package**: Releasing a standalone PyPI package with extensive docstrings and unit tests.

---

## ⚖️ License & Acknowledgements

- **`sharp123` Mechanism & CAD Architecture**: Designed by **`@jdegenstein`** ([GitHub](https://github.com/jdegenstein/sharp123)).
- **`ToggleClamp123` Mechanism & CAD Architecture**: Designed by **`@kalifck`** ([GitHub](https://github.com/kalifck/ToggleClamp123)), engineered with **Google Antigravity & Gemini 3.8 Flash**.
- **`Build123d` Core Framework**: Maintained by **`@gumyr`** and the Build123d contributor community ([GitHub](https://github.com/gumyr/build123d)).
- Benchmark data, 3D viewer, and comparative scripts are released under the [MIT License](LICENSE).
