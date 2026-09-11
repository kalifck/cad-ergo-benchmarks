# -*- coding: utf-8 -*-
"""
Build123d Contrib - Ergonomic CAD Primitives, Fluent Selectors & Diagnostics.

Empirically derived extensions to gumyr/build123d designed to dramatically
reduce LLM token consumption, eliminate manual trigonometry, and simplify
mechanical design with code.
"""

from __future__ import annotations

from .selectors import (
    at_x,
    at_y,
    at_z,
    bottom,
    circular,
    concave,
    concentric_to,
    convex,
    inner_rims,
    outer_rims,
    patch_shapelist,
    top,
)
from .primitives_2d import (
    AsymmetricSlot,
    LobePair,
    TearDrop,
)
from .engineering_hole import (
    EngineeringHole,
    PCDLocations,
)
from .features import (
    FlutePattern,
    Gusset,
    HoseBarb,
)
from .diagnostics import (
    diagnostics,
    is_watertight,
    patch_diagnostics,
)


def patch_all() -> None:
    """Activates all monkeypatches on build123d classes (ShapeList, Solid, Part)."""
    patch_shapelist()
    patch_diagnostics()


# Automatically apply monkeypatches upon import so fluent syntax is immediately available
patch_all()

__all__ = [
    # Selectors
    "at_z",
    "at_x",
    "at_y",
    "circular",
    "concentric_to",
    "concave",
    "convex",
    "inner_rims",
    "outer_rims",
    "top",
    "bottom",
    "patch_shapelist",
    # 2D Primitives
    "AsymmetricSlot",
    "LobePair",
    "TearDrop",
    # Engineering Holes & Locations
    "EngineeringHole",
    "PCDLocations",
    # Mechanical Features
    "Gusset",
    "FlutePattern",
    "HoseBarb",
    # Diagnostics
    "is_watertight",
    "diagnostics",
    "patch_diagnostics",
    "patch_all",
]
