# -*- coding: utf-8 -*-
"""
Unified Engineering Holes & PCD Patterns for Build123d.

Provides:
  - PCDLocations: High-level Pitch Circle Diameter (bolt circle) location generator
  - EngineeringHole: Unified manufacturing hole primitive supporting:
      * Blind & through holes
      * Standard 118° drill point tip cones
      * Dual chamfers (entry rim & exit rim in a single call)
      * Counterbores & countersinks
      * Subtractive by default in BuildPart contexts
"""

from __future__ import annotations

import math
from typing import Optional, Tuple, Union

from build123d import (
    Align,
    Axis,
    Cone,
    Cylinder,
    Location,
    Mode,
    Part,
    PolarLocations,
    RotationLike,
    Solid,
    Vector,
)
from build123d.objects_part import BasePartObject


class PCDLocations(PolarLocations):
    """
    Pitch Circle Diameter (PCD) / Bolt Circle Pattern Locations.

    Standard mechanical pattern generator for fastener circles, flanges,
    and motor mounts.

    Parameters:
        radius: Bolt circle pitch radius (half of PCD).
        diameter: Bolt circle pitch diameter (PCD). If provided, overrides radius.
        count: Number of hole positions along the circle.
        start_angle: Clocking offset in degrees (default 0.0).
        angular_range: Total angular sweep (default 360.0 for full circle).
    """

    def __init__(
        self,
        radius: Optional[float] = None,
        diameter: Optional[float] = None,
        count: int = 4,
        start_angle: float = 0.0,
        angular_range: float = 360.0,
    ):
        if diameter is not None:
            pcd_r = diameter / 2.0
        elif radius is not None:
            pcd_r = radius
        else:
            raise ValueError("Must specify either radius or diameter for PCDLocations")

        super().__init__(
            radius=pcd_r,
            count=count,
            start_angle=start_angle,
            angular_range=angular_range,
        )


class EngineeringHole(BasePartObject):
    """
    Unified Engineering Hole / Fastener Cavity.

    Constructs an exact parametric subtractive tool for manufacturing holes:
    - Dual chamfers on both entry and exit rims (e.g. 8X 1.5x45° TYP)
    - Conical drill point (standard 118° or custom)
    - Counterbores & Countersinks

    Orientation:
        Origin [0, 0, 0] is at the hole entrance face.
        The hole extends into negative Z (-Z direction).

    Parameters:
        radius: Hole nominal bore radius.
        diameter: Hole nominal bore diameter (overrides radius if provided).
        depth: Total bore cylindrical depth. If None, models an extended through cutter.
        tip_angle: Drill tip point angle in degrees (default 118.0° for blind holes;
                   set to 0 or 180 for flat bottom). Ignored if through=True.
        through: If True, treats as a through-hole and omits drill tip.
        chamfer_entry: Entry rim chamfer width (45°).
        chamfer_exit: Exit rim chamfer width (45°) for through-holes.
        cbore_radius: Counterbore radius at entry face.
        cbore_diameter: Counterbore diameter at entry face.
        cbore_depth: Depth of counterbore from entry face.
        csink_radius: Countersink major radius at entry face.
        csink_diameter: Countersink major diameter at entry face.
        csink_angle: Included countersink angle in degrees (default 90.0°).
        mode: Combination mode (defaults to Mode.SUBTRACT).
    """

    def __init__(
        self,
        radius: Optional[float] = None,
        diameter: Optional[float] = None,
        depth: float = 20.0,
        tip_angle: float = 118.0,
        through: bool = False,
        chamfer_entry: Optional[float] = None,
        chamfer_exit: Optional[float] = None,
        cbore_radius: Optional[float] = None,
        cbore_diameter: Optional[float] = None,
        cbore_depth: Optional[float] = None,
        csink_radius: Optional[float] = None,
        csink_diameter: Optional[float] = None,
        csink_angle: float = 90.0,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, Tuple[Align, Align, Align], None] = None,
        mode: Mode = Mode.SUBTRACT,
    ):
        if diameter is not None:
            r_bore = diameter / 2.0
        elif radius is not None:
            r_bore = radius
        else:
            raise ValueError("Must specify either radius or diameter for EngineeringHole")

        # 1. Main Bore Cylinder
        # Extends from +0.05 down to -depth with exact depth alignment
        cutter = Solid.make_cylinder(r_bore, depth + 0.05).moved(Location((0, 0, -depth)))

        # 2. Drill Point Cone (for blind holes)
        if not through and tip_angle > 0 and tip_angle < 180:
            tip_half_angle = math.radians(tip_angle / 2.0)
            cone_height = r_bore / math.tan(tip_half_angle)
            tip_cone = Solid.make_cone(0.0, r_bore, cone_height).moved(
                Location((0, 0, -depth - cone_height))
            )
            cutter = cutter + tip_cone

        # 3. Entry Chamfer
        if chamfer_entry and chamfer_entry > 0:
            c_cone = Solid.make_cone(
                r_bore, r_bore + chamfer_entry, chamfer_entry + 0.05
            ).moved(Location((0, 0, -chamfer_entry)))
            cutter = cutter + c_cone

        # 4. Exit Chamfer (for through holes)
        if chamfer_exit and chamfer_exit > 0:
            exit_cone = Solid.make_cone(
                r_bore + chamfer_exit, r_bore, chamfer_exit + 0.05
            ).moved(Location((0, 0, -depth)))
            cutter = cutter + exit_cone

        # 5. Counterbore
        cb_r = cbore_diameter / 2.0 if cbore_diameter is not None else cbore_radius
        if cb_r is not None and cbore_depth is not None and cbore_depth > 0:
            cb_cyl = Solid.make_cylinder(cb_r, cbore_depth + 0.05).moved(
                Location((0, 0, -cbore_depth))
            )
            cutter = cutter + cb_cyl

        # 6. Countersink
        cs_r = csink_diameter / 2.0 if csink_diameter is not None else csink_radius
        if cs_r is not None and cs_r > r_bore:
            cs_half_angle = math.radians(csink_angle / 2.0)
            cs_height = (cs_r - r_bore) / math.tan(cs_half_angle)
            cs_cone = Solid.make_cone(
                r_bore, cs_r, cs_height + 0.05
            ).moved(Location((0, 0, -cs_height)))
            cutter = cutter + cs_cone

        super().__init__(part=cutter, rotation=rotation, align=align, mode=mode)
