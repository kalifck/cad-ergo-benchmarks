# -*- coding: utf-8 -*-
"""
Native B-Rep Diagnostics & Watertightness Verification for Build123d.

Provides in-engine geometric health evaluation:
  - is_watertight: Validates closed 2-manifold B-Rep topology
  - diagnostics: Extracts Euler characteristic, bounding box, volume, and solid counts
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from build123d import Compound, Part, Shape, Solid
from OCP.BRep import BRep_Tool
from OCP.BRepCheck import BRepCheck_Analyzer


def is_watertight(shape: Union[Solid, Part, Compound]) -> bool:
    """
    Checks if a shape is a closed, watertight 2-manifold solid.

    Verifies:
      1. OpenCASCADE topological validity via BRepCheck_Analyzer.
      2. 2-manifold closure of all boundary shells via BRep_Tool.IsClosed_s.
    """
    analyzer = BRepCheck_Analyzer(shape.wrapped)
    if not analyzer.IsValid():
        return False

    solids = shape.solids() if hasattr(shape, "solids") else [shape]
    if not solids:
        return False

    for s in solids:
        shells = s.shells()
        if not shells:
            return False
        for shell in shells:
            if not BRep_Tool.IsClosed_s(shell.wrapped):
                return False

    return True


def diagnostics(shape: Union[Solid, Part, Compound]) -> Dict[str, Any]:
    """
    Returns a comprehensive diagnostic dictionary of geometric and topological health.
    """
    bbox = shape.bounding_box()
    solids = shape.solids() if hasattr(shape, "solids") else [shape]
    watertight = is_watertight(shape)

    # Compute Euler characteristic if tessellatable
    euler = 0
    try:
        import trimesh
        v, f = shape.tessellate(0.05)
        m = trimesh.Trimesh([[p.X, p.Y, p.Z] for p in v], f)
        euler = int(m.euler_number)
    except Exception:
        pass

    return {
        "is_valid": shape.is_valid,
        "is_watertight": watertight,
        "solid_count": len(solids),
        "volume_mm3": round(shape.volume, 3),
        "surface_area_mm2": round(shape.area, 3),
        "bounding_box": {
            "dx": round(bbox.size.X, 3),
            "dy": round(bbox.size.Y, 3),
            "dz": round(bbox.size.Z, 3),
        },
        "euler_characteristic": euler,
    }


def patch_diagnostics() -> None:
    """Injects .is_watertight property and .diagnostics() directly into Solid and Part."""
    Solid.is_watertight = property(is_watertight)  # type: ignore
    Solid.diagnostics = diagnostics  # type: ignore
    Part.is_watertight = property(is_watertight)  # type: ignore
    Part.diagnostics = diagnostics  # type: ignore
