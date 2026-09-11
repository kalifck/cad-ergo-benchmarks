# -*- coding: utf-8 -*-
"""
Advanced 2D Sketch Primitives & Analytical Envelopes for Build123d.

Provides high-level geometric primitives that eliminate repetitive manual
trigonometry and fragile vertex filleting:
  - AsymmetricSlot: Two circles of different radii connected by outer bitangent lines
  - LobePair: Two circles connected by concave tangent waist arcs (Figure-8)
  - TearDrop: Self-supporting 3D print teardrop profile
  - sketch_hull: Analytical 2D convex envelope of 2D shapes
"""

from __future__ import annotations

import math
from typing import Iterable, List, Optional, Tuple, Union

from build123d import (
    Align,
    Axis,
    BuildLine,
    BuildSketch,
    Compound,
    Edge,
    Face,
    GeomType,
    Line,
    Location,
    Mode,
    RadiusArc,
    Rotation,
    Shape,
    ShapeList,
    Sketch,
    ThreePointArc,
    Vector,
    VectorLike,
    Wire,
    make_face,
)
from build123d.objects_sketch import BaseSketchObject


class AsymmetricSlot(BaseSketchObject):
    """
    2D Asymmetric Slot / Tapered Capsule.

    Connects two circles of radii `r1` and `r2` separated by `distance` with
    exact analytical outer bitangent lines.

    Parameters:
        r1: Radius of the first (origin) circular end.
        r2: Radius of the second circular end.
        distance: Center-to-center distance between the two circular ends.
        angle: Orientation angle in degrees (0 = along +X axis).
        rotation: Additional rotation angle in degrees.
        align: Alignment tuple (Align.CENTER, Align.CENTER).
        mode: Combination mode (Mode.ADD, Mode.SUBTRACT, etc.).
    """

    def __init__(
        self,
        r1: float,
        r2: float,
        distance: float,
        angle: float = 0.0,
        rotation: float = 0.0,
        align: Union[Align, Tuple[Align, Align], None] = None,
        mode: Mode = Mode.ADD,
    ):
        if distance <= abs(r1 - r2):
            raise ValueError(
                f"Distance ({distance}) must be greater than the difference in radii ({abs(r1 - r2)})"
            )

        # Calculate bitangent angle theta
        theta = math.asin((r1 - r2) / distance)

        # Contact points in unrotated frame
        p1_top = Vector(-r1 * math.sin(theta), r1 * math.cos(theta))
        p1_bot = Vector(-r1 * math.sin(theta), -r1 * math.cos(theta))
        p2_top = Vector(distance - r2 * math.sin(theta), r2 * math.cos(theta))
        p2_bot = Vector(distance - r2 * math.sin(theta), -r2 * math.cos(theta))

        with BuildSketch() as sk:
            with BuildLine():
                Line(p1_top, p2_top)
                RadiusArc(p2_top, p2_bot, r2)
                Line(p2_bot, p1_bot)
                RadiusArc(p1_bot, p1_top, r1)
            make_face()

        raw_face = sk.face()
        total_rot = angle + rotation
        if total_rot != 0.0:
            raw_face = raw_face.rotate(Axis.Z, total_rot)

        super().__init__(raw_face, rotation=0.0, align=align, mode=mode)


class LobePair(BaseSketchObject):
    """
    Figure-8 Dual-Lobe / Waist-Blended Profile.

    Connects two circular lobes of radii `r1` and `r2` separated by `distance`
    blended smoothly on both sides by concave circular waist arcs of radius `waist_radius`.

    Parameters:
        r1: Radius of the first (origin) circular lobe.
        r2: Radius of the second circular lobe.
        distance: Center-to-center distance between lobes.
        waist_radius: Radius of the concave tangent blend arcs on both sides.
        angle: Orientation angle in degrees (0 = along +X axis).
        rotation: Additional rotation angle in degrees.
        align: Alignment tuple.
        mode: Combination mode.
    """

    def __init__(
        self,
        r1: float,
        r2: float,
        distance: float,
        waist_radius: float,
        angle: float = 0.0,
        rotation: float = 0.0,
        align: Union[Align, Tuple[Align, Align], None] = None,
        mode: Mode = Mode.ADD,
    ):
        R_a = r1 + waist_radius
        R_b = r2 + waist_radius
        if distance >= R_a + R_b or distance <= abs(R_a - R_b):
            raise ValueError(
                f"Distance ({distance}) is out of bridgeable range for waist radius ({waist_radius})"
            )

        # Intersection of offset circles to find waist arc centers
        x_w = (distance**2 + R_a**2 - R_b**2) / (2.0 * distance)
        y_w = math.sqrt(max(0.0, R_a**2 - x_w**2))

        # Tangent contact points
        p1_top = Vector(x_w * r1 / R_a, y_w * r1 / R_a)
        p2_top = Vector(distance + (x_w - distance) * r2 / R_b, y_w * r2 / R_b)
        p1_bot = Vector(x_w * r1 / R_a, -y_w * r1 / R_a)
        p2_bot = Vector(distance + (x_w - distance) * r2 / R_b, -y_w * r2 / R_b)

        with BuildSketch() as sk:
            with BuildLine():
                RadiusArc(p1_top, p2_top, -waist_radius)
                RadiusArc(p2_top, p2_bot, r2)
                RadiusArc(p2_bot, p1_bot, -waist_radius)
                RadiusArc(p1_bot, p1_top, r1)
            make_face()

        raw_face = sk.face()
        total_rot = angle + rotation
        if total_rot != 0.0:
            raw_face = raw_face.rotate(Axis.Z, total_rot)

        super().__init__(raw_face, rotation=0.0, align=align, mode=mode)


class TearDrop(BaseSketchObject):
    """
    Self-Supporting 3D-Printing Teardrop Hole Profile.

    Replaces the top half of a circular hole with two straight tangent edges
    meeting at a peak angle (typically 45° or 60°), preventing sagging when
    printed horizontally without supports.

    Parameters:
        radius: Base nominal bore radius.
        angle: Overhang draft angle in degrees from vertical (default 45.0°).
        rotation: Orientation rotation angle in degrees.
        align: Alignment tuple.
        mode: Combination mode.
    """

    def __init__(
        self,
        radius: float,
        angle: float = 45.0,
        rotation: float = 0.0,
        align: Union[Align, Tuple[Align, Align], None] = None,
        mode: Mode = Mode.ADD,
    ):
        theta_rad = math.radians(angle)
        # Tangency point on circle: normal vector makes angle theta with horizontal
        x_contact = radius * math.cos(theta_rad)
        y_contact = radius * math.sin(theta_rad)
        # Peak height
        y_peak = radius / math.sin(theta_rad)

        p_left = Vector(-x_contact, y_contact)
        p_right = Vector(x_contact, y_contact)
        p_peak = Vector(0.0, y_peak)

        with BuildSketch() as sk:
            with BuildLine():
                ThreePointArc(p_left, (0.0, -radius), p_right)
                Line(p_right, p_peak)
                Line(p_peak, p_left)
            make_face()

        raw_face = sk.face()
        super().__init__(raw_face, rotation=rotation, align=align, mode=mode)
