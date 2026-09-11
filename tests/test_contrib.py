# -*- coding: utf-8 -*-
"""
Unit tests for Build123d Contrib extensions:
- Fluent Selectors (ShapeList)
- 2D Primitives (AsymmetricSlot, LobePair, TearDrop)
- Engineering Holes & PCD Patterns
- Mechanical Features (Gusset, FlutePattern, HoseBarb)
- B-Rep Diagnostics
"""

import math
import pytest
import build123d as bd
from build123d_contrib import (
    AsymmetricSlot,
    EngineeringHole,
    FlutePattern,
    Gusset,
    HoseBarb,
    LobePair,
    PCDLocations,
    TearDrop,
    brep_diff,
    is_watertight,
    patch_all,
)

# Ensure patches are active
patch_all()


def test_fluent_selectors_planar_and_circular():
    """Tests at_z, circular, top, and bottom selectors."""
    with bd.BuildPart() as p:
        b1 = bd.Box(30, 30, 10, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        with bd.Locations((0, 0, 10)):
            b2 = bd.Cylinder(radius=5, height=15, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        # Hole
        with bd.Locations((0, 0, 0)):
            bd.Cylinder(radius=2, height=25, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN), mode=bd.Mode.SUBTRACT)

    solid = p.part.solids()[0]

    # Test top face
    top_face = solid.faces().top()
    assert abs(top_face.center().Z - 25.0) < 1e-3

    # Test bottom face
    bottom_face = solid.faces().bottom()
    assert abs(bottom_face.center().Z - 0.0) < 1e-3

    # Test at_z on edges
    deck_edges = solid.edges().at_z(10.0)
    assert len(deck_edges) > 0

    # Test circular edges
    cyl_edges = solid.edges().circular(radius=5.0)
    assert len(cyl_edges) >= 1

    hole_edges = solid.edges().circular(radius=2.0)
    assert len(hole_edges) >= 2


def test_convex_concave_edge_selectors():
    """Tests dihedral angle convex and concave edge filtering."""
    # L-bracket with 1 internal re-entrant corner and multiple exterior convex corners
    part = bd.Box(20, 20, 10) - bd.Pos(10, 10, 0) * bd.Box(20, 20, 10)
    solid = part.solids()[0]

    concave_edges = solid.edges().concave(solid)
    convex_edges = solid.edges().convex(solid)

    assert len(concave_edges) == 1
    assert abs(concave_edges[0].center().X) < 1e-2
    assert abs(concave_edges[0].center().Y) < 1e-2
    assert len(convex_edges) > 10


def test_asymmetric_slot():
    """Tests AsymmetricSlot 2D primitive in both builder and algebra modes."""
    # Algebra mode
    slot_algebra = AsymmetricSlot(r1=12.0, r2=6.0, distance=35.0, angle=30.0)
    assert slot_algebra.is_valid
    assert slot_algebra.area > 0

    # Builder mode
    with bd.BuildSketch() as sk:
        AsymmetricSlot(r1=10.0, r2=5.0, distance=25.0)
    assert sk.face().is_valid
    assert sk.face().area > 0


def test_lobe_pair():
    """Tests LobePair (Figure-8) with concave waist arcs."""
    lobe = LobePair(r1=41.0, r2=30.0, distance=61.8, waist_radius=10.0)
    assert lobe.is_valid
    assert lobe.area > 1000.0


def test_teardrop():
    """Tests TearDrop 3D printing profile."""
    td = TearDrop(radius=5.0, angle=45.0)
    assert td.is_valid
    assert td.area > math.pi * 25.0 / 2.0  # Must be larger than half-circle


def test_pcd_and_engineering_hole():
    """Tests PCDLocations with EngineeringHole (dual chamfer, drill tip, counterbore)."""
    with bd.BuildPart() as p:
        bd.Box(80, 80, 20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        # 4x through holes with dual chamfer on PCD 50
        with PCDLocations(diameter=50.0, count=4):
            EngineeringHole(
                diameter=8.0,
                depth=20.0,
                through=True,
                chamfer_entry=1.0,
                chamfer_exit=1.0,
            )
        # 1x central blind hole with 118 drill tip and countersink
        EngineeringHole(
            diameter=12.0,
            depth=12.0,
            through=False,
            tip_angle=118.0,
            csink_diameter=16.0,
            csink_angle=90.0,
        )

    solid = p.part.solids()[0]
    assert len(p.part.solids()) == 1
    assert solid.is_valid
    assert solid.is_watertight


def test_gusset_stiffener():
    """Tests Gusset triangular rib addition."""
    with bd.BuildPart() as p:
        bd.Box(40, 40, 5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        with bd.Locations((0, -17.5, 5)):
            bd.Box(40, 5, 30, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN))
        with bd.Locations((0, -15, 5)):
            Gusset(length=20, height=25, thickness=4, chamfer=5)

    assert len(p.part.solids()) == 1
    assert p.part.solids()[0].is_watertight


def test_flute_pattern():
    """Tests tactile fluting around cylinder."""
    with bd.BuildPart() as p:
        bd.Cylinder(radius=15, height=30)
        FlutePattern(outer_radius=15, length=30, count=8, flute_radius=1.5, depth=1.0)

    assert len(p.part.solids()) == 1
    assert p.part.solids()[0].is_watertight


def test_hose_barb():
    """Tests HoseBarb fluid fitting generator."""
    barb = HoseBarb(crest_diameter=14.0, root_diameter=11.5, length=6.0, count=3, bore_diameter=8.0)
    assert len(barb.solids()) == 1
    assert barb.solids()[0].is_watertight


def test_diagnostics_and_watertightness():
    """Tests native B-Rep diagnostics."""
    box = bd.Box(10, 10, 10)
    diag = box.diagnostics()
    assert diag["is_watertight"] is True
    assert diag["solid_count"] == 1
    assert abs(diag["volume_mm3"] - 1000.0) < 1e-1
    assert box.is_watertight is True


def test_brep_diff_identical():
    """Tests that identical shapes produce 100% Jaccard match with zero missing/extra volume."""
    b1 = bd.Box(10, 10, 10)
    b2 = bd.Box(10, 10, 10)
    diff = brep_diff(b1, b2)
    assert diff.match is True
    assert diff.jaccard_pct == 100.0
    assert diff.missing_volume == 0.0
    assert diff.extra_volume == 0.0
    assert diff.com_shift_mm == 0.0
    assert "MATCH" in str(diff)


def test_brep_diff_modified():
    """Tests that a drilled hole produces missing volume and reduced Jaccard similarity."""
    b_solid = bd.Box(10, 10, 10)
    b_drilled = bd.Box(10, 10, 10) - bd.Cylinder(radius=2, height=10)
    diff = brep_diff(b_solid, b_drilled)
    assert diff.match is False
    assert diff.jaccard_pct < 100.0
    assert diff.missing_volume > 0.0
    assert diff.extra_volume == 0.0
    assert diff.missing is not None
    assert "MISMATCH" in str(diff)


def test_brep_diff_monkeypatch():
    """Tests that .diff() is available directly on Part and Solid objects."""
    b1 = bd.Box(20, 20, 10)
    b2 = bd.Box(20, 20, 10)
    diff = b1.diff(b2)
    assert diff.match is True
    assert diff.jaccard_pct == 100.0

