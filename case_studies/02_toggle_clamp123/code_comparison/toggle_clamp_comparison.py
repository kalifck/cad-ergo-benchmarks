# -*- coding: utf-8 -*-
"""
Case Study 02: ToggleClamp123 — Full Component Suite Comparison
===============================================================

Original Mechanism & CAD Architecture: @kalifck (https://github.com/kalifck/ToggleClamp123)
Engineered with: Google Antigravity & Gemini 3.8 Flash
Ergonomic Port & Benchmark: cad-ergo-benchmarks

Complete side-by-side comparison of the push-action toggle clamp mechanism:
- Base mounting chassis with 85mm clear travel bay and guide barrel
- Actuation handle with 83° rotational sweep and Pivot B tongue
- Twin dogleg connecting links
- Linear plunger with clevis slot and pressure foot
- Precision dowel pins
"""

import math
from build123d import *

# ==============================================================================
# PARAMETERS & TOLERANCES
# ==============================================================================
PIN_CLEARANCE = 0.4
SLIDE_CLEARANCE = 0.4
SPACER_CLEARANCE = 0.6

BASE_LENGTH = 175.0
BASE_WIDTH = 56.0
BASE_THICKNESS = 6.0
BASE_CORNER_R = 6.0
PIVOT_A_X = -45.0
PIVOT_A_Z = 32.0
EAR_THICKNESS = 6.0
EAR_GAP = 14.0
EAR_BORE = 6.0 + PIN_CLEARANCE
BARREL_CENTER_X = 65.0
BARREL_AXIS_Z = 16.0
BARREL_LENGTH = 40.0
BARREL_OUTER_DIA = 24.0
BARREL_BORE = 14.0
STOP_PIN_X = -60.0
STOP_PIN_Z = 18.0

HANDLE_HUB_THICKNESS = EAR_GAP - SPACER_CLEARANCE
HANDLE_LENGTH = 100.0
HANDLE_WIDTH = 14.0
HANDLE_THICKNESS = 8.0
LINK_RADIUS = 28.0
LINK_ANGLE_DEG = 35.0

LINK_DIST = 48.0
LINK_THICKNESS = 3.5
LINK_WIDTH = 12.0

PLUNGER_DIA = BARREL_BORE - SLIDE_CLEARANCE
PLUNGER_LENGTH = 95.0
CLEVIS_LENGTH = 18.0
CLEVIS_WIDTH = 14.0
CLEVIS_SLOT = LINK_THICKNESS * 2 + 1.0
FOOT_DIA = 22.0
FOOT_THICKNESS = 8.0


# ==============================================================================
# 1. ORIGINAL IMPLEMENTATION (ToggleClamp123)
# ==============================================================================

def make_base_flange_orig() -> Compound:
    with BuildPart() as p:
        with BuildSketch() as s_base:
            RectangleRounded(BASE_LENGTH, BASE_WIDTH, BASE_CORNER_R)
            x_slot = BASE_LENGTH / 2 - 15.0
            y_slot = BASE_WIDTH / 2 - 7.5
            with Locations((-x_slot, y_slot), (-x_slot, -y_slot), (x_slot, y_slot), (x_slot, -y_slot)):
                SlotOverall(12.0, 6.5, mode=Mode.SUBTRACT)
        extrude(amount=BASE_THICKNESS)

        barrel_start_x = BARREL_CENTER_X - BARREL_LENGTH / 2
        with BuildSketch(Plane.YZ.offset(barrel_start_x)) as s_b:
            with Locations((0, BARREL_AXIS_Z)):
                Circle(BARREL_OUTER_DIA / 2)
            with Locations((0, BARREL_AXIS_Z / 2)):
                Rectangle(BARREL_OUTER_DIA, BARREL_AXIS_Z)
            with Locations((0, BARREL_AXIS_Z)):
                Circle(BARREL_BORE / 2, mode=Mode.SUBTRACT)
        extrude(amount=BARREL_LENGTH)

        ear_r = 10.0
        ear_inner_y = EAR_GAP / 2
        for y_off, ext in [(-ear_inner_y, -EAR_THICKNESS), (ear_inner_y, EAR_THICKNESS)]:
            with BuildSketch(Plane.XZ.offset(y_off)):
                with BuildLine():
                    Line((PIVOT_A_X - ear_r - 6.0, 0), (PIVOT_A_X - ear_r, PIVOT_A_Z))
                    RadiusArc((PIVOT_A_X - ear_r, PIVOT_A_Z), (PIVOT_A_X + ear_r, PIVOT_A_Z), ear_r)
                    Line((PIVOT_A_X + ear_r, PIVOT_A_Z), (PIVOT_A_X + ear_r + 8.0, 0))
                    Line((PIVOT_A_X + ear_r + 8.0, 0), (PIVOT_A_X - ear_r - 6.0, 0))
                make_face()
                with Locations((PIVOT_A_X, PIVOT_A_Z)):
                    Circle(EAR_BORE / 2, mode=Mode.SUBTRACT)
            extrude(amount=ext)

        total_ear_span = EAR_GAP + 2 * EAR_THICKNESS
        with BuildSketch(Plane.XZ.offset(total_ear_span / 2)):
            with Locations((STOP_PIN_X, STOP_PIN_Z)):
                Circle(3.0)
        extrude(amount=-total_ear_span)

    return p.part


def make_handle_orig() -> Compound:
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            Circle(10.0)
            Circle(6.4 / 2, mode=Mode.SUBTRACT)
        extrude(amount=HANDLE_HUB_THICKNESS, both=True)

        with BuildSketch(Plane.XZ):
            with Locations((0, 4.0)):
                RectangleRounded(HANDLE_WIDTH, HANDLE_LENGTH, 4.0)
        extrude(amount=HANDLE_THICKNESS / 2, both=True)

        alpha = math.radians(LINK_ANGLE_DEG)
        bx = LINK_RADIUS * math.cos(alpha)
        bz = LINK_RADIUS * math.sin(alpha)
        with BuildSketch(Plane.XZ):
            with Locations((bx / 2, bz / 2)):
                Rectangle(LINK_RADIUS, 12.0, rotation=LINK_ANGLE_DEG)
            with Locations((bx, bz)):
                Circle(7.0)
                Circle(6.4 / 2, mode=Mode.SUBTRACT)
        extrude(amount=8.0 / 2, both=True)

    return p.part


def make_pin_orig(length: float) -> Compound:
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            Circle(3.0)
        extrude(amount=length / 2, both=True)
        edges = p.part.edges().filter_by(GeomType.CIRCLE)
        if edges:
            chamfer(edges, 0.5)
    return p.part


# ==============================================================================
# 2. ERGONOMIC REWRITE (cad-ergo-benchmarks)
# ==============================================================================

def make_base_flange_ergo() -> Compound:
    with BuildPart() as p:
        # 1. Base plate with declarative GridLocations (eliminates manual 4-corner math)
        with BuildSketch():
            RectangleRounded(BASE_LENGTH, BASE_WIDTH, BASE_CORNER_R)
            with GridLocations(BASE_LENGTH - 30.0, BASE_WIDTH - 15.0, 2, 2):
                SlotOverall(12.0, 6.5, mode=Mode.SUBTRACT)
        extrude(amount=BASE_THICKNESS)

        # 2. Guide Barrel
        barrel_start_x = BARREL_CENTER_X - BARREL_LENGTH / 2
        with BuildSketch(Plane.YZ.offset(barrel_start_x)):
            with Locations((0, BARREL_AXIS_Z)):
                Circle(BARREL_OUTER_DIA / 2)
            with Locations((0, BARREL_AXIS_Z / 2)):
                Rectangle(BARREL_OUTER_DIA, BARREL_AXIS_Z)
            with Locations((0, BARREL_AXIS_Z)):
                Circle(BARREL_BORE / 2, mode=Mode.SUBTRACT)
        extrude(amount=BARREL_LENGTH)

        # 3. Pivot Ears (Modeled once and mirrored across Plane.XZ)
        ear_r = 10.0
        ear_inner_y = EAR_GAP / 2
        with BuildPart():
            with BuildSketch(Plane.XZ.offset(ear_inner_y)):
                with BuildLine():
                    Line((PIVOT_A_X - ear_r - 6.0, 0), (PIVOT_A_X - ear_r, PIVOT_A_Z))
                    RadiusArc((PIVOT_A_X - ear_r, PIVOT_A_Z), (PIVOT_A_X + ear_r, PIVOT_A_Z), ear_r)
                    Line((PIVOT_A_X + ear_r, PIVOT_A_Z), (PIVOT_A_X + ear_r + 8.0, 0))
                    Line((PIVOT_A_X + ear_r + 8.0, 0), (PIVOT_A_X - ear_r - 6.0, 0))
                make_face()
                with Locations((PIVOT_A_X, PIVOT_A_Z)):
                    Circle(EAR_BORE / 2, mode=Mode.SUBTRACT)
            extrude(amount=EAR_THICKNESS)
            mirror(about=Plane.XZ)

        # 4. Stop Pin
        total_ear_span = EAR_GAP + 2 * EAR_THICKNESS
        with BuildSketch(Plane.XZ.offset(total_ear_span / 2)):
            with Locations((STOP_PIN_X, STOP_PIN_Z)):
                Circle(3.0)
        extrude(amount=-total_ear_span)

    return p.part


def make_handle_ergo() -> Compound:
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            Circle(10.0)
            Circle(6.4 / 2, mode=Mode.SUBTRACT)
        extrude(amount=HANDLE_HUB_THICKNESS, both=True)

        with BuildSketch(Plane.XZ):
            with Locations((0, 4.0)):
                RectangleRounded(HANDLE_WIDTH, HANDLE_LENGTH, 4.0)
        extrude(amount=HANDLE_THICKNESS / 2, both=True)

        # Pivot B clevis tongue: Zero manual trigonometry!
        with BuildSketch(Plane.XZ):
            with Locations(Location((0, 0), LINK_ANGLE_DEG)):
                with Locations((LINK_RADIUS / 2, 0)):
                    Rectangle(LINK_RADIUS, 12.0)
                with Locations((LINK_RADIUS, 0)):
                    Circle(7.0)
                    Circle(6.4 / 2, mode=Mode.SUBTRACT)
        extrude(amount=8.0 / 2, both=True)

    return p.part


def make_pin_ergo(length: float) -> Compound:
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            Circle(3.0)
        extrude(amount=length / 2, both=True)
        chamfer(p.part.edges().circular(), 0.5)
    return p.part
