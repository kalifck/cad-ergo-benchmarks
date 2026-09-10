# -*- coding: utf-8 -*-
import math
import sys
from pathlib import Path

repo_root = Path('c:/Users/Charif/Documents/ANtigravity/BUILD123D')
sys.path.insert(0, str(repo_root / 'sharp123' / 'src'))

import ocp_vscode
ocp_vscode.show_clear = lambda: None
ocp_vscode.set_defaults = lambda *args, **kwargs: None
ocp_vscode.set_colormap = lambda *args, **kwargs: None
ocp_vscode.show_all = lambda *args, **kwargs: None

from build123d import *
from sharp123 import create_assembly_config
import sharp123.parts as orig_parts
import sharp123.parts.main_tower_ergonomic as mte
import sharp123.parts.base_plate_ergonomic as bpe
import sharp123.parts.clamp_arm_ergonomic as cae

par = create_assembly_config()

def build_assembly(use_ergo=False):
    TowerCls = mte.Tower if use_ergo else orig_parts.Tower
    BasePlateCls = bpe.BasePlate if use_ergo else orig_parts.BasePlate
    ClampArmCls = cae.ClampArm if use_ergo else orig_parts.ClampArm

    tower = TowerCls(par)
    base_plate = BasePlateCls(par)
    clamp_arm_holder = orig_parts.ClampArmHolder(par)
    clamping_screw = orig_parts.ClampingScrew(par)
    tapered_clamping_nut = orig_parts.TaperedClampingNut(par)
    long_pin_1 = orig_parts.LongPin(par)
    long_pin_2 = orig_parts.LongPin(par)
    clamp_arm = ClampArmCls(par)

    clamp_arm_mirror = clamp_arm.solid()
    clamp_arm_mirror = mirror(clamp_arm_mirror, about=Plane.XZ.offset(0))
    RigidJoint('j1', to_part=clamp_arm_mirror, joint_location=clamp_arm.joints['j1'].location)

    angle_adjustment_screw = orig_parts.AngleAdjustmentScrew(par)
    angle_adjustment_nut = orig_parts.AngleAdjustmentNut(par)
    plate_handle_shaft = orig_parts.PlateHandleShaft(par)
    plate_holder_handle = orig_parts.PlateHolderHandle(par)
    diamond_plate_holder = orig_parts.DiamondPlateHolder(par)
    aa_screw_key = orig_parts.AAScrewKey(par)
    washer = orig_parts.Washer(par)
    knife_example = orig_parts.KnifeExample(par)

    # Connect joints
    base_plate.joints['j1'].connect_to(tower.joints['j1'])
    tower.joints['j2'].connect_to(clamp_arm_holder.joints['j1'])
    tower.joints['j3'].connect_to(angle_adjustment_screw.joints['j1'])
    tower.joints['j4'].connect_to(aa_screw_key.joints['j1'])
    angle_adjustment_screw.joints['j2'].connect_to(angle_adjustment_nut.joints['j1'])
    angle_adjustment_nut.joints['j2'].connect_to(plate_handle_shaft.joints['j1'])
    plate_handle_shaft.joints['j2'].connect_to(plate_holder_handle.joints['j1'])
    plate_holder_handle.joints['j2'].connect_to(diamond_plate_holder.joints['j1'])
    clamp_arm_holder.joints['j2'].connect_to(clamping_screw.joints['j1'])
    clamp_arm_holder.joints['j3'].connect_to(long_pin_1.joints['j1'])
    clamp_arm_holder.joints['j4'].connect_to(long_pin_2.joints['j1'])
    clamp_arm_holder.joints['j5'].connect_to(knife_example.joints['j1'])
    clamping_screw.joints['j2'].connect_to(tapered_clamping_nut.joints['j1'])
    clamping_screw.joints['j3'].connect_to(washer.joints['j1'])
    long_pin_1.joints['j2'].connect_to(clamp_arm.joints['j1'])
    long_pin_2.joints['j2'].connect_to(clamp_arm_mirror.joints['j1'])

    all_parts = [
        tower, base_plate, clamp_arm_holder, clamping_screw,
        tapered_clamping_nut, long_pin_1, long_pin_2, clamp_arm,
        clamp_arm_mirror, angle_adjustment_screw, angle_adjustment_nut,
        plate_handle_shaft, plate_holder_handle, diamond_plate_holder,
        aa_screw_key, washer, knife_example
    ]
    return all_parts

print('Building original assembly...')
parts_orig = build_assembly(use_ergo=False)
print('Building ergonomic candidate assembly...')
parts_cand = build_assembly(use_ergo=True)

part_names = [
    'Tower', 'BasePlate', 'ClampArmHolder', 'ClampingScrew',
    'TaperedClampingNut', 'LongPin1', 'LongPin2', 'ClampArm',
    'ClampArmMirror', 'AngleAdjustmentScrew', 'AngleAdjustmentNut',
    'PlateHandleShaft', 'PlateHolderHandle', 'DiamondPlateHolder',
    'AAScrewKey', 'Washer', 'KnifeExample'
]

print('================================================================================')
print('FULL 17-PART ASSEMBLED SUPERIMPOSED AUDIT')
print('================================================================================')

total_vol_orig = 0.0
total_vol_cand = 0.0
all_match = True

for name, p_o, p_c in zip(part_names, parts_orig, parts_cand):
    solids_o = p_o.solids() if hasattr(p_o, 'solids') else ([p_o] if isinstance(p_o, Solid) else list(p_o))
    solids_c = p_c.solids() if hasattr(p_c, 'solids') else ([p_c] if isinstance(p_c, Solid) else list(p_c))
    
    comp_o = Compound(solids_o)
    comp_c = Compound(solids_c)
    
    vo = comp_o.volume
    vc = comp_c.volume
    total_vol_orig += vo
    total_vol_cand += vc
    
    bb_o = comp_o.bounding_box()
    bb_c = comp_c.bounding_box()
    dx = abs((bb_c.max.X - bb_c.min.X) - (bb_o.max.X - bb_o.min.X))
    dy = abs((bb_c.max.Y - bb_c.min.Y) - (bb_o.max.Y - bb_o.min.Y))
    dz = abs((bb_c.max.Z - bb_c.min.Z) - (bb_o.max.Z - bb_o.min.Z))
    
    c_o = comp_o.center()
    c_c = comp_c.center()
    dc = math.hypot(c_c.X - c_o.X, c_c.Y - c_o.Y, c_c.Z - c_o.Z)
    
    d_vol = abs(vc - vo)
    match = (d_vol < 0.01 and dx < 0.01 and dy < 0.01 and dz < 0.01 and dc < 0.01)
    if not match: all_match = False
    
    status = 'MATCH' if match else 'MISMATCH'
    print(f'  {name:22s}: [{status}] Vol={vo:10.2f} mm3 | DeltaV={d_vol:.4f} | WorldCenterDelta={dc:.4f} mm | BBoxDelta=({dx:.3f},{dy:.3f},{dz:.3f})')

print('--------------------------------------------------------------------------------')
print('TOTAL ASSEMBLED VOLUME:')
print(f'  - Original Assembly:    {total_vol_orig:.2f} mm3')
print(f'  - Candidate Assembly:   {total_vol_cand:.2f} mm3')
print(f'  - Total Volume Delta:   {abs(total_vol_cand - total_vol_orig):.4f} mm3')
verdict = '100% PERFECT MATCH PASS' if all_match else 'FAIL'
print(f'  - Overall Assembly:     {verdict}')
print('================================================================================')

# Export full assembled compound STLs
out_dir = repo_root / "output" / "sharp123"
out_dir.mkdir(parents=True, exist_ok=True)

all_orig_solids = []
for p in parts_orig:
    solids = p.solids() if hasattr(p, 'solids') else ([p] if isinstance(p, Solid) else list(p))
    all_orig_solids.extend(solids)

all_cand_solids = []
for p in parts_cand:
    solids = p.solids() if hasattr(p, 'solids') else ([p] if isinstance(p, Solid) else list(p))
    all_cand_solids.extend(solids)

comp_asm_orig = Compound(all_orig_solids)
comp_asm_cand = Compound(all_cand_solids)

# Center for Three.js viewer
ctr = comp_asm_orig.center()
comp_asm_orig_ctr = comp_asm_orig.moved(Location((-ctr.X, -ctr.Y, -ctr.Z)))
comp_asm_cand_ctr = comp_asm_cand.moved(Location((-ctr.X, -ctr.Y, -ctr.Z)))

export_stl(comp_asm_orig_ctr, str(out_dir / "assembly_orig.stl"))
export_stl(comp_asm_cand_ctr, str(out_dir / "assembly_ergo.stl"))
export_stl(comp_asm_cand_ctr, str(out_dir / "sharp123_assembly.stl"))
print(f'Successfully exported assembly STLs to {out_dir}!')
