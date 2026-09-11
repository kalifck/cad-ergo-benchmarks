# 🎓 Build123d Ergonomic Extensions: Complete Practical Tutorial
**Version**: `0.11.1+ext`  
**Philosophy**: *Mechanical Design Intent over Computational Geometry Math.*

Welcome to the comprehensive guide for Build123d's ergonomic CAD extensions. These features eliminate repetitive high-school trigonometry, remove fragile lambda predicates, and turn 40-line boilerplate features into 1-line declarative statements.

---

## 📌 Quick Answer: How Do Chamfers Work? (Do I Write 0 Degrees?)

In mechanical engineering and Build123d's `EngineeringHole`:
- **Chamfer sizes are specified in millimeters of setback, NOT degrees**:
  - `chamfer_entry=1.5` creates a standard $1.5\text{ mm} \times 45^\circ$ entry deburring chamfer.
  - `chamfer_exit=1.0` creates a $1.0\text{ mm} \times 45^\circ$ exit chamfer on through-holes.
- **If you do NOT want any chamfers**:
  - **Simply omit the parameter** (it defaults to `None`), or explicitly pass `chamfer_entry=0` / `chamfer_entry=None`.
  - It will generate a sharp, crisp, 90° cylindrical edge without any beveling!
- **If you want a flat-bottom hole (milled pocket instead of a drill tip cone)**:
  - Simply set `tip_angle=180` (or `tip_angle=0` or `through=True`).
  - By default, blind holes use `tip_angle=118.0` (the standard industrial twist-drill cone angle).

---

## 1. 🔩 The Unified Hole Masterclass: `EngineeringHole`

In traditional Build123d, creating a blind tapped hole with an entrance countersink and a conical drill point tip required nesting a `Cylinder`, two `Cone` primitives, calculating trigonometric heights, and subtracting them. If you needed chamfers on both ends of a through-hole ("8X 1.5x45° TYP"), you had to write custom edge-filtering loops.

`EngineeringHole` solves this in a single, bulletproof subtractive call.

### A. Plain Through-Hole (Zero Chamfers)
```python
from build123d import *

with BuildPart() as p:
    Box(40, 40, 10)
    # Plain Ø8.0mm through-hole, perfectly square edges:
    EngineeringHole(diameter=8.0, depth=10.0, through=True)
```

### B. Production Through-Hole with Dual Chamfers (e.g. 8X 1.5x45°)
```python
with BuildPart() as p:
    Box(40, 40, 20)
    # Dual chamfer: 1.5mm chamfer at entry (top) AND 1.5mm chamfer at exit (bottom)
    EngineeringHole(
        diameter=10.0,
        depth=20.0,
        through=True,
        chamfer_entry=1.5,
        chamfer_exit=1.5
    )
```

### C. Blind Tapped Hole (118° Drill Tip + Countersink)
```python
with BuildPart() as p:
    Box(40, 40, 25)
    # M10 Tap Drill (Ø8.5mm, 18mm deep, 118° drill point, Ø11mm x 90° countersink)
    EngineeringHole(
        diameter=8.5,
        depth=18.0,
        through=False,
        tip_angle=118.0,        # Standard drill bit cone
        csink_diameter=11.0,     # Entrance countersink
        csink_angle=90.0        # Included angle (default 90°)
    )
```

### D. Socket-Head Cap Screw Counterbore Hole
```python
with BuildPart() as p:
    Box(40, 40, 20)
    # M6 clearance hole (Ø6.6) with socket head counterbore (Ø11.0 x 6.5 deep)
    EngineeringHole(
        diameter=6.6,
        depth=20.0,
        through=True,
        cbore_diameter=11.0,
        cbore_depth=6.5,
        chamfer_exit=0.5
    )
```

---

## 2. 🎯 Pitch Circle Diameters in 1 Line: `PCDLocations`

Instead of writing `for ang in (...)` loops with `math.cos(math.radians(ang))` and `math.sin()`, use `PCDLocations`.

```python
with BuildPart() as p:
    Cylinder(radius=35.0, height=15.0)
    
    # 6 holes on a 50mm Pitch Circle Diameter, starting at 30°
    with Locations((0, 0, 15.0)), PCDLocations(diameter=50.0, count=6, start_angle=30.0):
        EngineeringHole(diameter=4.5, depth=15.0, through=True, cbore_diameter=8.0, cbore_depth=4.0)
```

### Parameters:
- `diameter`: Pitch Circle Diameter (PCD) in mm (or use `radius`).
- `count`: Number of hole locations.
- `start_angle`: Clocking angle offset in degrees (default `0.0`).
- `angular_range`: Total sweep angle (default `360.0` for full circle, or `180.0` for semicircles).

---

## 3. 📐 Zero-Trig 2D Envelopes: `AsymmetricSlot` & `LobePair`

Connecting two circular hubs with outer tangent lines or concave waist fillets is one of the most common tasks in mechanical design (rocker arms, linkages, bellcranks, motor mounts, Figure-8 bosses).

### A. `AsymmetricSlot`: The Tapered Linkage / Arm Primitive
Connects two circles of different radii ($R_1$ and $R_2$) separated by `distance` with exact analytical bitangent lines:

```python
with BuildSketch() as sk:
    # Large hub R=18mm, small hub R=10mm, 60mm apart, angled at 45 degrees:
    AsymmetricSlot(r1=18.0, r2=10.0, distance=60.0, angle=45.0)
```
*Zero vector rotations. Zero `math.asin`. 100% exact C1 tangency.*

### B. `LobePair`: Figure-8 Bosses & Waist Blends
Connects two circular lobes blended by concave tangent circular arcs (cam lobes, pulleys, dual-bore bosses):

```python
with BuildSketch() as sk:
    # Right lobe R=41mm, Left lobe R=30mm, 62mm apart, blended by R=10mm concave waist arcs:
    LobePair(r1=41.0, r2=30.0, distance=62.0, waist_radius=10.0)
```

### C. `TearDrop`: Self-Supporting 3D Print Bores
Horizontal round holes tend to sag at the top bridge during 3D printing. `TearDrop` replaces the top half with self-supporting draft angles:

```python
with BuildSketch(Plane.XZ) as sk:
    # 10mm bore with 45° self-supporting overhang peak:
    TearDrop(radius=5.0, angle=45.0)
```

---

## 4. 🦾 Structural & Mechanical Features

### A. `Gusset`: Reinforced Triangular Stiffening Ribs
Adds a reinforcing rib between two perpendicular or angled plates with an optional stress-relief corner chamfer:

```python
with BuildPart() as p:
    # Base plate + vertical wall
    Box(50, 50, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((0, -22.0, 6)):
        Box(50, 6, 35, align=(Align.CENTER, Align.MIN, Align.MIN))
    
    # 1-Line Gusset: length=25mm along X, height=30mm along Z, 4mm thick, 5mm chamfer:
    with Locations((0, -19.0, 6)):
        Gusset(length=25.0, height=30.0, thickness=4.0, chamfer=5.0)
```

### B. `FlutePattern`: Tactile Ergonomic Grips
Generates a circular polar array of longitudinal cylindrical cutter grooves around any cylinder (for flashlight bodies, knobs, dials, hose ports):

```python
with BuildPart() as p:
    Cylinder(radius=15.0, height=30.0)
    # Cut 12 longitudinal flutes (radius 1.2mm, 0.8mm deep)
    FlutePattern(outer_radius=15.0, length=30.0, count=12, flute_radius=1.2, depth=0.8)
```

### C. `HoseBarb`: Conical Fluid Tube Grippers
Constructs high-retention hose barbs with reverse-rake shoulders:

```python
# 3 consecutive barbs: Crest Ø14mm, Root Ø11.5mm, 6mm length per barb, 8mm through-airway:
barb = HoseBarb(crest_diameter=14.0, root_diameter=11.5, length=6.0, count=3, bore_diameter=8.0)
```

---

## 5. 🔍 Fluent Selectors: Goodbye Lambda Predicates!

Stop writing 4-line lambda predicates with bounding-box floating point tolerances (`abs(e.bounding_box().min.Z - 30) < 1e-2`). Use fluent selectors directly:

| Old / Fragile Build123d Syntax | New Fluent Contrib Syntax | What it Does |
| :--- | :--- | :--- |
| `edges.filter_by(lambda e: abs(e.center().Z - 30) < 1e-3)` | `edges.at_z(30.0)` | Selects edges at $Z = 30\text{ mm}$ |
| `edges.filter_by(GeomType.CIRCLE).filter_by(lambda e: abs(e.radius - 5) < 1e-3)` | `edges.circular(radius=5.0)` | Selects circular edges of radius 5mm |
| `faces.sort_by(Axis.Z)[-1]` | `faces.top()` | Selects top-most face along $Z$ |
| `faces.sort_by(Axis.Z)[0]` | `faces.bottom()` | Selects bottom-most face along $Z$ |
| *(Impossible without complex OCC code)* | `edges.convex(solid)` | Selects only exterior edges (for rounds) |
| *(Impossible without complex OCC code)* | `edges.concave(solid)` | Selects only interior re-entrant edges (for fillets) |

### Example: Filleting Only Inside Corners
```python
part = Box(30, 30, 10) - Pos(15, 15, 0) * Box(30, 30, 10)
solid = part.solids()[0]

# Fillet ONLY the interior re-entrant fillet seam:
solid = fillet(solid.edges().concave(solid), radius=3.0)
```

---

## 6. 🩺 Native B-Rep Diagnostics

Verify your CAD models directly in Python without installing external mesh tools:

```python
# Check closed 2-manifold watertightness directly on any Solid or Part:
if solid.is_watertight:
    print("Geometry is 100% production ready!")

# Query full topological report:
report = solid.diagnostics()
print("Volume:", report["volume_mm3"], "mm³")
print("Bounding Box:", report["bounding_box"])
print("Solid Count:", report["solid_count"])
```

---

## 7. 🚀 Full Real-World Example: Motor Mounting Bracket (Under 30 Lines)

Here is a complete, production-ready motor bracket combining `AsymmetricSlot`, `PCDLocations`, `EngineeringHole`, `Gusset`, and fluent selectors:

```python
from build123d import *

with BuildPart() as p:
    # 1. Base Foot Plate with mounting slots
    with BuildSketch(Plane.XY):
        Rectangle(80.0, 50.0)
    extrude(amount=8.0)
    
    # 2. Mounting Bores with Dual Chamfers (4X 1.0x45°)
    with Locations((-28.0, 0), (28.0, 0)):
        EngineeringHole(diameter=6.5, depth=8.0, through=True, chamfer_entry=1.0, chamfer_exit=1.0)
    
    # 3. Vertical Motor Flange (Tapered Arm using AsymmetricSlot)
    with BuildSketch(Plane.XZ.offset(25.0)):
        with Locations((0, 8.0)):
            AsymmetricSlot(r1=22.0, r2=15.0, distance=40.0, angle=90.0)
    extrude(amount=-10.0)
    
    # 4. Motor Center Bore & 4-Bolt PCD Pattern
    with Locations((0, 25.0, 48.0)):
        # Central shaft pilot hole
        EngineeringHole(diameter=16.0, depth=10.0, through=True)
        # NEMA 17 / Stepper 4x M3 PCD Bolt Circle with Counterbores
        with PCDLocations(diameter=31.0, count=4, start_angle=45.0):
            EngineeringHole(diameter=3.4, depth=10.0, through=True, cbore_diameter=6.0, cbore_depth=3.0)
    
    # 5. Reinforcing Gusset Rib on backside
    with Locations((0, 15.0, 8.0)):
        Gusset(length=20.0, height=25.0, thickness=5.0, chamfer=4.0)

bracket = p.part.solids()[0]
assert bracket.is_watertight

print(f"Bracket built successfully! Volume: {bracket.volume:.1f} mm³")
```
*Zero manual trigonometry. Zero boolean cutter nesting. 100% watertight on the first compile!*
