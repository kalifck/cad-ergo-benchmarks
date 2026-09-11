# -*- coding: utf-8 -*-
"""
Fluent Topological Selectors for Build123d ShapeList.

Provides semantic, high-level filter methods that replace verbose, fragile lambda
predicates across edges, faces, and wires:
  - .at_z(), .at_x(), .at_y()
  - .circular(), .cylindrical()
  - .convex(), .concave() (analytical B-Rep dihedral angle classification)
  - .inner_rims(), .outer_rims()
  - .top(), .bottom(), .lateral()
"""

from __future__ import annotations

import math
from typing import Callable, Iterable, List, Optional, TypeVar, Union

from build123d import (
    Axis,
    Edge,
    Face,
    GeomType,
    Plane,
    Shape,
    ShapeList,
    Solid,
    Vector,
    VectorLike,
    Wire,
)

T = TypeVar("T", bound=Shape)


def at_z(
    shapes: ShapeList[T],
    z: float,
    tolerance: float = 1e-3,
    span: bool = False,
) -> ShapeList[T]:
    """
    Filters shapes located at coordinate Z.

    Parameters:
        shapes: ShapeList to filter.
        z: Target Z coordinate.
        tolerance: Coordinate tolerance.
        span: If True, requires the entire bounding box [min.Z, max.Z] to lie
              within z ± tolerance (useful for strictly planar edges or faces).
              If False, checks the shape's center().Z.
    """
    if span:
        return shapes.filter_by(
            lambda s: abs(s.bounding_box().min.Z - z) <= tolerance
            and abs(s.bounding_box().max.Z - z) <= tolerance
        )
    return shapes.filter_by(lambda s: abs(s.center().Z - z) <= tolerance)


def at_x(
    shapes: ShapeList[T],
    x: float,
    tolerance: float = 1e-3,
    span: bool = False,
) -> ShapeList[T]:
    """Filters shapes located at coordinate X."""
    if span:
        return shapes.filter_by(
            lambda s: abs(s.bounding_box().min.X - x) <= tolerance
            and abs(s.bounding_box().max.X - x) <= tolerance
        )
    return shapes.filter_by(lambda s: abs(s.center().X - x) <= tolerance)


def at_y(
    shapes: ShapeList[T],
    y: float,
    tolerance: float = 1e-3,
    span: bool = False,
) -> ShapeList[T]:
    """Filters shapes located at coordinate Y."""
    if span:
        return shapes.filter_by(
            lambda s: abs(s.bounding_box().min.Y - y) <= tolerance
            and abs(s.bounding_box().max.Y - y) <= tolerance
        )
    return shapes.filter_by(lambda s: abs(s.center().Y - y) <= tolerance)


def circular(
    shapes: ShapeList[T],
    radius: Optional[float] = None,
    diameter: Optional[float] = None,
    tolerance: float = 1e-3,
) -> ShapeList[T]:
    """
    Filters circular edges (or cylindrical faces).

    Parameters:
        shapes: ShapeList of Edges or Faces.
        radius: Target radius.
        diameter: Target diameter (overrides radius if provided).
        tolerance: Radius tolerance.
    """
    target_r = diameter / 2.0 if diameter is not None else radius

    def pred(s: Shape) -> bool:
        if s.geom_type in (GeomType.CIRCLE, GeomType.CYLINDER):
            if target_r is None:
                return True
            actual_r = getattr(s, "radius", None)
            if actual_r is not None:
                return abs(actual_r - target_r) <= tolerance
        return False

    return shapes.filter_by(pred)


def concentric_to(
    shapes: ShapeList[T],
    target: Union[VectorLike, Axis, Shape],
    tolerance: float = 1e-3,
    plane: Axis = Axis.Z,
) -> ShapeList[T]:
    """
    Filters shapes whose center is concentric to a target point, axis, or shape
    projected along the given axis plane.
    """
    if isinstance(target, Axis):
        target_pt = target.position
    elif isinstance(target, Shape):
        target_pt = target.center()
    else:
        target_pt = Vector(target)

    def pred(s: Shape) -> bool:
        c = s.center()
        if plane == Axis.Z:
            return math.hypot(c.X - target_pt.X, c.Y - target_pt.Y) <= tolerance
        elif plane == Axis.Y:
            return math.hypot(c.X - target_pt.X, c.Z - target_pt.Z) <= tolerance
        else:
            return math.hypot(c.Y - target_pt.Y, c.Z - target_pt.Z) <= tolerance

    return shapes.filter_by(pred)


def is_edge_concave(edge: Edge, solid: Solid, tolerance: float = 1e-3) -> Optional[bool]:
    """
    Analytically determines if an edge is concave (re-entrant), convex (exterior),
    or smooth (tangent) with respect to a solid body using B-Rep dihedral angle.

    Returns:
        True if concave (internal corner/fillet seam),
        False if convex (external corner/round),
        None if edge is non-manifold, boundary, or tangent.
    """
    adj_faces = [f for f in solid.faces() if any(fe.is_same(edge) for fe in f.edges())]
    if len(adj_faces) != 2:
        return None

    p = edge.position_at(0.5)
    t = edge.tangent_at(0.5)
    f0, f1 = adj_faces[0], adj_faces[1]
    n0 = f0.normal_at(p)
    n1 = f1.normal_at(p)

    # Co-tangent outward vector along face 0
    b0 = n0.cross(t)
    p_test = p + b0 * 0.001
    dist = f0.distance_to(p_test)
    if dist > 0.0005:
        b0 = -b0

    dot = n1.dot(b0)
    if dot > 0.01:
        return True  # Concave
    elif dot < -0.01:
        return False  # Convex
    return None  # Smooth tangent


def concave(shapes: ShapeList[Edge], solid: Solid) -> ShapeList[Edge]:
    """Filters only re-entrant / concave edges (internal corners) of a solid."""
    return shapes.filter_by(lambda e: is_edge_concave(e, solid) is True)


def convex(shapes: ShapeList[Edge], solid: Solid) -> ShapeList[Edge]:
    """Filters only exterior / convex edges (external corners) of a solid."""
    return shapes.filter_by(lambda e: is_edge_concave(e, solid) is False)


def inner_rims(shapes: ShapeList[Edge], face: Face) -> ShapeList[Edge]:
    """Filters edges belonging to internal holes / cutouts of a face."""
    outer_wire = face.outer_wire()
    outer_edges = outer_wire.edges()
    return shapes.filter_by(lambda e: not any(oe.is_same(e) for oe in outer_edges))


def outer_rims(shapes: ShapeList[Edge], face: Face) -> ShapeList[Edge]:
    """Filters edges belonging strictly to the outer boundary of a face."""
    outer_wire = face.outer_wire()
    outer_edges = outer_wire.edges()
    return shapes.filter_by(lambda e: any(oe.is_same(e) for oe in outer_edges))


def top(faces: ShapeList[Face], axis: Axis = Axis.Z) -> Face:
    """Returns the single top-most face along the specified axis."""
    return faces.sort_by(axis).last


def bottom(faces: ShapeList[Face], axis: Axis = Axis.Z) -> Face:
    """Returns the single bottom-most face along the specified axis."""
    return faces.sort_by(axis).first


def patch_shapelist() -> None:
    """Injects fluent selector methods directly into build123d.ShapeList."""
    ShapeList.at_z = lambda self, z, tol=1e-3, span=False: at_z(self, z, tol, span)  # type: ignore
    ShapeList.at_x = lambda self, x, tol=1e-3, span=False: at_x(self, x, tol, span)  # type: ignore
    ShapeList.at_y = lambda self, y, tol=1e-3, span=False: at_y(self, y, tol, span)  # type: ignore
    ShapeList.circular = (  # type: ignore
        lambda self, radius=None, diameter=None, tolerance=1e-3: circular(
            self, radius=radius, diameter=diameter, tolerance=tolerance
        )
    )
    ShapeList.concentric_to = lambda self, target, tol=1e-3, plane=Axis.Z: concentric_to(self, target, tol, plane)  # type: ignore
    ShapeList.concave = lambda self, solid: concave(self, solid)  # type: ignore
    ShapeList.convex = lambda self, solid: convex(self, solid)  # type: ignore
    ShapeList.inner_rims = lambda self, face: inner_rims(self, face)  # type: ignore
    ShapeList.outer_rims = lambda self, face: outer_rims(self, face)  # type: ignore
    ShapeList.top = lambda self, axis=Axis.Z: top(self, axis)  # type: ignore
    ShapeList.bottom = lambda self, axis=Axis.Z: bottom(self, axis)  # type: ignore
