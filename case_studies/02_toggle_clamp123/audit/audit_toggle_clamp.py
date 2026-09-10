import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

repo_root = Path('c:/Users/Charif/Documents/ANtigravity/BUILD123D')
sys.path.insert(0, str(repo_root / 'ToggleClamp123'))

from build123d import *
from toggle_clamp import (
    PIN_CLEARANCE, SLIDE_CLEARANCE, SPACER_CLEARANCE,
    BASE_LENGTH, BASE_WIDTH, BASE_THICKNESS, BASE_CORNER_R,
    PIVOT_A_X, PIVOT_A_Z, EAR_THICKNESS, EAR_GAP, EAR_BORE,
    BARREL_CENTER_X, BARREL_AXIS_Z, BARREL_LENGTH, BARREL_OUTER_DIA, BARREL_BORE,
    STOP_PIN_X, STOP_PIN_Z,
    HANDLE_HUB_THICKNESS, HANDLE_LENGTH, HANDLE_WIDTH, HANDLE_THICKNESS,
    LINK_RADIUS, LINK_ANGLE_DEG,
    LINK_DIST, LINK_THICKNESS, LINK_WIDTH,
    PLUNGER_DIA, PLUNGER_LENGTH, CLEVIS_LENGTH, CLEVIS_WIDTH, CLEVIS_SLOT,
    FOOT_DIA, FOOT_THICKNESS,
    make_base_flange as make_base_orig,
    make_handle as make_handle_orig,
    make_connecting_link as make_link_orig,
    make_linear_plunger as make_plunger_orig,
    make_pin as make_pin_orig,
)

# ------------------------------------------------------------------------------
# ERGONOMIC IMPLEMENTATIONS
# ------------------------------------------------------------------------------

def make_base_flange_ergo() -> Compound:
    with BuildPart() as p:
        # 1. Base plate with GridLocations (replaces manual 4-corner coordinate math)
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

        # 3. Pivot Ears (replaces manual duplicate loop with single sketch + mirror)
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

        # 4. Stop Pin (Cylinder across ear span)
        total_ear_span = EAR_GAP + 2 * EAR_THICKNESS
        with BuildSketch(Plane.XZ.offset(total_ear_span / 2)):
            with Locations((STOP_PIN_X, STOP_PIN_Z)):
                Circle(3.0)
        extrude(amount=-total_ear_span)

    return p.part


def make_handle_ergo() -> Compound:
    with BuildPart() as p:
        # 1. Rotary Hub
        with BuildSketch(Plane.XZ):
            Circle(10.0)
            Circle(6.4 / 2, mode=Mode.SUBTRACT)
        extrude(amount=HANDLE_HUB_THICKNESS, both=True)

        # 2. Actuation Lever Arm
        with BuildSketch(Plane.XZ):
            with Locations((0, 4.0)):
                RectangleRounded(HANDLE_WIDTH, HANDLE_LENGTH, 4.0)
        extrude(amount=HANDLE_THICKNESS / 2, both=True)

        # 3. Pivot B Clevis Tongue (Zero manual trig! Uses 2D rotated location)
        with BuildSketch(Plane.XZ):
            with Locations(Location((0, 0), LINK_ANGLE_DEG)):
                with Locations((LINK_RADIUS / 2, 0)):
                    Rectangle(LINK_RADIUS, 12.0)
                with Locations((LINK_RADIUS, 0)):
                    Circle(7.0)
                    Circle(6.4 / 2, mode=Mode.SUBTRACT)
        extrude(amount=8.0 / 2, both=True)

    return p.part


def make_connecting_link_ergo() -> Compound:
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            SlotCenterToCenter(LINK_DIST, 12.0)
            with Locations((-LINK_DIST / 2, 0), (LINK_DIST / 2, 0)):
                Circle(6.4 / 2, mode=Mode.SUBTRACT)
        extrude(amount=LINK_THICKNESS / 2, both=True)
    return p.part


def make_linear_plunger_ergo() -> Compound:
    with BuildPart() as p:
        # Shaft
        with BuildSketch(Plane.YZ):
            Circle(PLUNGER_DIA / 2)
        extrude(amount=PLUNGER_LENGTH, both=True)

        # Clevis
        shaft_half = PLUNGER_LENGTH / 2
        with BuildSketch(Plane.XY.offset(-7.0)):
            with Locations((-shaft_half - CLEVIS_LENGTH / 2, 0)):
                Rectangle(CLEVIS_LENGTH, CLEVIS_WIDTH)
        extrude(amount=14.0)

        # Slot in clevis
        with BuildSketch(Plane.XY.offset(-CLEVIS_SLOT / 2)):
            with Locations((-shaft_half - CLEVIS_LENGTH / 2, 0)):
                Rectangle(CLEVIS_LENGTH + 2.0, CLEVIS_SLOT)
        extrude(amount=CLEVIS_SLOT, mode=Mode.SUBTRACT)

        # Pin hole
        pivot_c_x = -(shaft_half + CLEVIS_LENGTH - 7.0)
        with BuildSketch(Plane.XZ):
            with Locations((pivot_c_x, 0)):
                Circle(6.4 / 2)
        extrude(amount=CLEVIS_WIDTH / 2, both=True, mode=Mode.SUBTRACT)

        # Foot
        with BuildSketch(Plane.YZ.offset(shaft_half)):
            Circle(FOOT_DIA / 2)
        extrude(amount=FOOT_THICKNESS)

    return p.part


def make_pin_ergo(length: float) -> Compound:
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            Circle(3.0)
        extrude(amount=length / 2, both=True)
        chamfer(p.part.edges().circular(), 0.5)
    return p.part


# Run comparison audit
def run_diff_audit(name, orig, ergo):
    vo = orig.volume
    ve = ergo.volume
    d_vol = abs(ve - vo)
    
    missing = (orig - ergo).volume
    extra = (ergo - orig).volume
    intersection = (orig & ergo).volume
    union = (orig + ergo).volume
    jaccard = (intersection / union) * 100.0 if union > 0 else 100.0

    print(f"=== {name} ===")
    print(f"  Orig Vol: {vo:.4f} mm³ | Ergo Vol: {ve:.4f} mm³ | Δ: {d_vol:.4f} mm³")
    print(f"  Missing: {missing:.4f} mm³ | Extra: {extra:.4f} mm³ | Jaccard: {jaccard:.2f}%")
    status = "PASS" if d_vol < 1e-3 and missing < 1e-3 and extra < 1e-3 else "FAIL"
    print(f"  Verdict: {status}\n")
    return status == "PASS"

if __name__ == "__main__":
    print("Testing ToggleClamp123 Ergonomic Rewrite Parity...\n")
    all_pass = True
    all_pass &= run_diff_audit("Handle", make_handle_orig(), make_handle_ergo())
    all_pass &= run_diff_audit("Connecting Link", make_link_orig(), make_connecting_link_ergo())
    all_pass &= run_diff_audit("Pin A (30mm)", make_pin_orig(30.0), make_pin_ergo(30.0))
    all_pass &= run_diff_audit("Pin B (20mm)", make_pin_orig(20.0), make_pin_ergo(20.0))
    all_pass &= run_diff_audit("Pin C (18mm)", make_pin_orig(18.0), make_pin_ergo(18.0))
    all_pass &= run_diff_audit("Base Flange", make_base_orig(), make_base_flange_ergo())
    all_pass &= run_diff_audit("Plunger", make_plunger_orig(), make_linear_plunger_ergo())
    
    if all_pass:
        print("🎉 ALL COMPONENTS ACHIEVED 100.00% VOLUMETRIC PARITY!")
    else:
        print("❌ SOME COMPONENTS NEED REFINEMENT.")
