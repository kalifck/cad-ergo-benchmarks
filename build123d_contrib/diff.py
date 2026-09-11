# -*- coding: utf-8 -*-
"""
1-Call Optical & Volumetric B-Rep Diff Engine for Build123d.

Provides mathematically exact OpenCASCADE volumetric difference, Jaccard similarity,
and optical CAD inspection between two shapes or STEP files with zero-token execution
and compact, token-efficient telemetry reporting.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from build123d import (
    Color,
    Compound,
    Location,
    Part,
    Shape,
    Solid,
    Vector,
    export_step,
    export_stl,
    import_step,
)


def _normalize_shape(obj: Any) -> Union[Solid, Compound]:
    """Converts Part, Solid, Compound, file path, or list into a unified B-Rep Shape."""
    if isinstance(obj, (str, Path)):
        p = Path(obj)
        if not p.exists():
            raise FileNotFoundError(f"CAD file not found: {p}")
        if p.suffix.lower() in (".step", ".stp", ".brep"):
            return import_step(str(p))
        raise ValueError(f"Unsupported CAD file extension: {p.suffix}")

    if hasattr(obj, "part") and obj.part is not None:
        obj = obj.part

    if hasattr(obj, "solids"):
        solids = obj.solids()
        if len(solids) == 1:
            return solids[0]
        elif len(solids) > 1:
            return Compound(solids)
        raise ValueError("Provided CAD object contains zero solids.")

    if isinstance(obj, (Solid, Compound)):
        return obj

    if isinstance(obj, (list, tuple)):
        all_solids: List[Solid] = []
        for item in obj:
            if hasattr(item, "solids"):
                all_solids.extend(item.solids())
            elif isinstance(item, Solid):
                all_solids.append(item)
        if all_solids:
            return Compound(all_solids)

    raise TypeError(f"Cannot normalize object of type {type(obj)} to B-Rep Solid/Compound.")


class BrepDiffResult:
    """Encapsulates the mathematical metrics and optical 3D geometry of a CAD diff."""

    def __init__(
        self,
        match: bool,
        jaccard_pct: float,
        dice_pct: float,
        target_volume: float,
        candidate_volume: float,
        missing_volume: float,
        extra_volume: float,
        common_volume: float,
        com_shift_mm: float,
        bbox_delta: Dict[str, float],
        missing_shape: Optional[Shape],
        extra_shape: Optional[Shape],
        common_shape: Optional[Shape],
    ):
        self.match = match
        self.jaccard_pct = round(jaccard_pct, 4)
        self.dice_pct = round(dice_pct, 4)
        self.target_volume = round(target_volume, 4)
        self.candidate_volume = round(candidate_volume, 4)
        self.missing_volume = round(missing_volume, 4)
        self.extra_volume = round(extra_volume, 4)
        self.common_volume = round(common_volume, 4)
        self.com_shift_mm = round(com_shift_mm, 4)
        self.bbox_delta = {k: round(v, 4) for k, v in bbox_delta.items()}

        self.missing = missing_shape
        self.extra = extra_shape
        self.common = common_shape

        # Build colored optical composite solid
        colored_elements: List[Shape] = []
        if self.common is not None and len(self.common.solids()) > 0:
            c = self.common
            c.color = Color(0.7, 0.7, 0.7, 0.3)  # Translucent clay
            colored_elements.append(c)
        if self.missing is not None and len(self.missing.solids()) > 0:
            m = self.missing
            m.color = Color(0.9, 0.1, 0.1, 0.8)  # Red: material removed
            colored_elements.append(m)
        if self.extra is not None and len(self.extra.solids()) > 0:
            e = self.extra
            e.color = Color(0.1, 0.85, 0.2, 0.8)  # Green: material added
            colored_elements.append(e)

        self.composite = Compound(colored_elements) if colored_elements else None

    def to_dict(self, compact: bool = True) -> Dict[str, Any]:
        """Returns a token-disciplined dictionary summary."""
        res: Dict[str, Any] = {
            "match": self.match,
            "jaccard_pct": self.jaccard_pct,
            "v_target": self.target_volume,
            "v_candidate": self.candidate_volume,
            "v_missing": self.missing_volume,
            "v_extra": self.extra_volume,
            "com_shift_mm": self.com_shift_mm,
        }
        if not compact:
            res["dice_pct"] = self.dice_pct
            res["v_common"] = self.common_volume
            res["bbox_delta"] = self.bbox_delta
        return res

    def summary(self, compact: bool = True) -> str:
        """Returns a concise, token-efficient string representation."""
        status = "MATCH" if self.match else "MISMATCH"
        if compact:
            return (
                f"[BREP DIFF] {status} ({self.jaccard_pct:.2f}% Jaccard) | "
                f"Missing: {self.missing_volume:.4f} mm³ | "
                f"Extra: {self.extra_volume:.4f} mm³ | "
                f"COM Shift: {self.com_shift_mm:.4f} mm"
            )
        return (
            f"============================================================\n"
            f"OPEN CASCADE B-REP VOLUMETRIC DIFF SUMMARY\n"
            f"============================================================\n"
            f"  Verdict:            {status} ({self.jaccard_pct:.4f}% Jaccard Similarity)\n"
            f"  Target Volume (A):  {self.target_volume:.4f} mm³\n"
            f"  Candidate Vol (B):  {self.candidate_volume:.4f} mm³\n"
            f"  Missing (A \\ B):    {self.missing_volume:.4f} mm³ (Red)\n"
            f"  Extra   (B \\ A):    {self.extra_volume:.4f} mm³ (Green)\n"
            f"  Common  (A ∩ B):    {self.common_volume:.4f} mm³ (Clay)\n"
            f"  Center of Mass Δ:   {self.com_shift_mm:.4f} mm\n"
            f"  BBox Delta (X,Y,Z): ({self.bbox_delta['dx']:.3f}, {self.bbox_delta['dy']:.3f}, {self.bbox_delta['dz']:.3f}) mm\n"
            f"============================================================"
        )

    def export_step(self, file_path: Union[str, Path]) -> Optional[Path]:
        """Exports the optical color-coded diff compound to STEP format."""
        if self.composite is None:
            return None
        out = Path(file_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        export_step(self.composite, str(out))
        return out

    def export_stl(self, out_dir: Union[str, Path], prefix: str = "diff") -> Dict[str, Path]:
        """Exports individual optical component STLs (common, missing, extra)."""
        d = Path(out_dir)
        d.mkdir(parents=True, exist_ok=True)
        paths: Dict[str, Path] = {}
        if self.common is not None and len(self.common.solids()) > 0:
            p_com = d / f"{prefix}_common.stl"
            export_stl(self.common, str(p_com))
            paths["common"] = p_com
        if self.missing is not None and len(self.missing.solids()) > 0:
            p_mis = d / f"{prefix}_missing.stl"
            export_stl(self.missing, str(p_mis))
            paths["missing"] = p_mis
        if self.extra is not None and len(self.extra.solids()) > 0:
            p_ext = d / f"{prefix}_extra.stl"
            export_stl(self.extra, str(p_ext))
            paths["extra"] = p_ext
        return paths

    def __repr__(self) -> str:
        return self.summary(compact=True)

    def __str__(self) -> str:
        return self.summary(compact=True)


def brep_diff(
    target: Union[Solid, Part, Compound, str, Path, Any],
    candidate: Union[Solid, Part, Compound, str, Path, Any],
    tolerance: float = 1e-4,
    export_dir: Optional[Union[str, Path]] = None,
) -> BrepDiffResult:
    """
    Executes a 1-call OpenCASCADE optical and volumetric diff between two CAD models.

    Parameters:
        target: Reference / baseline CAD solid, Part, Compound, or .step file path.
        candidate: Modified / candidate CAD solid, Part, Compound, or .step file path.
        tolerance: Numerical volume tolerance in mm³ to qualify as zero-delta match.
        export_dir: Optional output directory to automatically save colored diff assets.

    Returns:
        BrepDiffResult: Mathematically rigorous volumetric metrics and 3D diff solids.
    """
    s_a = _normalize_shape(target)
    s_b = _normalize_shape(candidate)

    va = float(s_a.volume)
    vb = float(s_b.volume)

    # 1. Missing Volume: A \ B (Material present in target but deleted in candidate)
    cut_ab = s_a - s_b
    solids_missing = cut_ab.solids() if hasattr(cut_ab, "solids") else []
    v_missing = float(cut_ab.volume) if len(solids_missing) > 0 else 0.0
    if v_missing < tolerance:
        v_missing = 0.0
        shape_missing = None
    else:
        shape_missing = cut_ab

    # 2. Extra Volume: B \ A (Material present in candidate that wasn't in target)
    cut_ba = s_b - s_a
    solids_extra = cut_ba.solids() if hasattr(cut_ba, "solids") else []
    v_extra = float(cut_ba.volume) if len(solids_extra) > 0 else 0.0
    if v_extra < tolerance:
        v_extra = 0.0
        shape_extra = None
    else:
        shape_extra = cut_ba

    # 3. Common Core: A ∩ B
    inter = s_a & s_b
    solids_common = inter.solids() if hasattr(inter, "solids") else []
    v_common = float(inter.volume) if len(solids_common) > 0 else 0.0
    shape_common = inter if len(solids_common) > 0 else None

    # 4. Similarity Metrics
    v_union = va + vb - v_common
    jaccard = (v_common / v_union * 100.0) if v_union > 0 else 0.0
    dice = (2.0 * v_common / (va + vb) * 100.0) if (va + vb) > 0 else 0.0

    # 5. Spatial Shifts
    ca = s_a.center()
    cb = s_b.center()
    com_shift = math.hypot(cb.X - ca.X, cb.Y - ca.Y, cb.Z - ca.Z)

    bba = s_a.bounding_box()
    bbb = s_b.bounding_box()
    bbox_delta = {
        "dx": abs(bbb.size.X - bba.size.X),
        "dy": abs(bbb.size.Y - bba.size.Y),
        "dz": abs(bbb.size.Z - bba.size.Z),
    }

    match = (
        v_missing == 0.0
        and v_extra == 0.0
        and com_shift < tolerance
        and bbox_delta["dx"] < tolerance
        and bbox_delta["dy"] < tolerance
        and bbox_delta["dz"] < tolerance
    )

    result = BrepDiffResult(
        match=match,
        jaccard_pct=jaccard,
        dice_pct=dice,
        target_volume=va,
        candidate_volume=vb,
        missing_volume=v_missing,
        extra_volume=v_extra,
        common_volume=v_common,
        com_shift_mm=com_shift,
        bbox_delta=bbox_delta,
        missing_shape=shape_missing,
        extra_shape=shape_extra,
        common_shape=shape_common,
    )

    if export_dir is not None:
        out_p = Path(export_dir)
        result.export_step(out_p / "brep_diff_composite.step")
        result.export_stl(out_p)

    return result


def patch_diff() -> None:
    """Monkey-patches .diff() directly onto Build123d Shape, Solid, Part, and Compound."""

    def diff_method(self: Any, other: Any, tolerance: float = 1e-4) -> BrepDiffResult:
        return brep_diff(target=self, candidate=other, tolerance=tolerance)

    Shape.diff = diff_method  # type: ignore[attr-defined]
    Part.diff = diff_method  # type: ignore[attr-defined]
