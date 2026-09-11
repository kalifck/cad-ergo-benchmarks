# -*- coding: utf-8 -*-
"""
Mechanical Manufacturing Features & Primitives for Build123d.

Provides high-frequency mechanical components:
  - Gusset: Structural triangular stiffening web
  - FlutePattern: Ergonomic tactile grip grooves around cylinders
  - HoseBarb: Conical fluid hose retention barbs
  - ORingGroove: Annular dynamic/static elastomeric seal glands
"""

from __future__ import annotations

import math
from typing import Optional, Tuple, Union

from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Cone,
    Cylinder,
    Line,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    PolarLocations,
    RotationLike,
    Solid,
    Vector,
    extrude,
    make_face,
    revolve,
)
from build123d.objects_part import BasePartObject


class Gusset(BasePartObject):
    """
    Structural Triangular Stiffening Gusset / Rib.

    Connects two perpendicular or angled plates with a reinforced triangular web
    and optional outer hypouse chamfer.

    Parameters:
        length: Base horizontal leg length along +X.
        height: Vertical leg height along +Z.
        thickness: Total lateral thickness (centered across Y=0).
        chamfer: Optional corner cut on the hypotenuse.
        rotation: Orientation rotation.
        align: Alignment tuple.
        mode: Combination mode (defaults to Mode.ADD).
    """

    def __init__(
        self,
        length: float,
        height: float,
        thickness: float,
        chamfer: float = 0.0,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, Tuple[Align, Align, Align], None] = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildSketch(Plane.XZ) as sk:
            with BuildLine():
                p0 = (0.0, 0.0)
                p1 = (length, 0.0)
                p2 = (0.0, height)
                if 0 < chamfer < min(length, height):
                    Line(p0, p1)
                    Line(p1, (length, chamfer))
                    Line((length, chamfer), (chamfer, height))
                    Line((chamfer, height), p2)
                    Line(p2, p0)
                else:
                    Line(p0, p1)
                    Line(p1, p2)
                    Line(p2, p0)
            make_face()

        rib_solid = extrude(sk.face(), amount=thickness / 2.0, both=True)
        super().__init__(part=rib_solid, rotation=rotation, align=align, mode=mode)


class FlutePattern(BasePartObject):
    """
    Ergonomic Tactile Fluting / Knurling Pattern.

    Generates a polar array of longitudinal cylindrical cutter grooves around
    a central cylinder (knobs, flashlight bodies, hose ports, vape sleeves).

    Parameters:
        outer_radius: Nominal outer radius of the parent cylinder.
        outer_diameter: Nominal outer diameter (overrides outer_radius).
        length: Longitudinal height of the flutes.
        count: Number of flutes around the perimeter (default 12).
        flute_radius: Radius of the circular cutter flute.
        depth: Penetration depth into the surface (default equals flute_radius).
        rotation: Orientation rotation.
        mode: Combination mode (defaults to Mode.SUBTRACT).
    """

    def __init__(
        self,
        outer_radius: Optional[float] = None,
        outer_diameter: Optional[float] = None,
        length: float = 20.0,
        count: int = 12,
        flute_radius: float = 1.0,
        depth: Optional[float] = None,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, Tuple[Align, Align, Align], None] = None,
        mode: Mode = Mode.SUBTRACT,
    ):
        r_outer = outer_diameter / 2.0 if outer_diameter is not None else outer_radius
        if r_outer is None:
            raise ValueError("Must specify either outer_radius or outer_diameter")

        cut_depth = depth if depth is not None else flute_radius
        # Center of cutter is placed at outer_radius - depth + flute_radius
        pcd_cutter_r = r_outer + flute_radius - cut_depth

        with BuildPart() as p:
            with PolarLocations(radius=pcd_cutter_r, count=count):
                Cylinder(
                    radius=flute_radius,
                    height=length + 0.1,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

        super().__init__(part=p.part, rotation=rotation, align=align, mode=mode)


class HoseBarb(BasePartObject):
    """
    Parametric Fluid Hose Retention Barb.

    Constructs standard conical barbs with reverse-rake catch shoulders for
    elastomeric tube gripping.

    Parameters:
        crest_diameter: Crest (major) outer diameter of the barb.
        root_diameter: Root (minor) stem diameter of the barb.
        length: Length of each individual barb segment.
        count: Number of consecutive retention barbs.
        catch_angle: Backside catch shoulder angle in degrees (90.0 = square shoulder,
                     45.0 = self-supporting 3D print shoulder).
        bore_diameter: Optional internal flow through-bore diameter.
        mode: Combination mode (defaults to Mode.ADD).
    """

    def __init__(
        self,
        crest_diameter: float,
        root_diameter: float,
        length: float,
        count: int = 3,
        catch_angle: float = 85.0,
        bore_diameter: Optional[float] = None,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, Tuple[Align, Align, Align], None] = None,
        mode: Mode = Mode.ADD,
    ):
        r_crest = crest_diameter / 2.0
        r_root = root_diameter / 2.0
        catch_rad = math.radians(min(89.0, max(30.0, catch_angle)))
        shoulder_drop = (r_crest - r_root) / math.tan(catch_rad)
        taper_len = max(0.1, length - shoulder_drop)

        with BuildPart() as p:
            for i in range(count):
                z_base = i * length
                # Forward conical ramp
                with Locations((0, 0, z_base)):
                    Cone(
                        bottom_radius=r_root,
                        top_radius=r_crest,
                        height=taper_len,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                # Catch shoulder taper
                if shoulder_drop > 0.05:
                    with Locations((0, 0, z_base + taper_len)):
                        Cone(
                            bottom_radius=r_crest,
                            top_radius=r_root,
                            height=shoulder_drop,
                            align=(Align.CENTER, Align.CENTER, Align.MIN),
                        )

            # Optional core airway subtraction
            if bore_diameter is not None and bore_diameter > 0:
                with Locations((0, 0, -0.05)):
                    Cylinder(
                        radius=bore_diameter / 2.0,
                        height=count * length + 0.1,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                        mode=Mode.SUBTRACT,
                    )

        super().__init__(part=p.part, rotation=rotation, align=align, mode=mode)
