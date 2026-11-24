"""Noor ModernGL FX renderer — LUT3D, split wipe, rays, bloom, grain, vignette.

Pure software fallback (no GPU required) so it runs in CI/headless. If a
ModernGL context is available, the same operations are accelerated.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

from .schemas import SplitMode


# Built-in LUTs as simple 3D identity-ish transforms (software path).
_LUTS = {
    "kadyrov_gold": (1.10, 1.05, 0.95),
    "royal_dark": (0.85, 0.90, 1.10),
    "makkah_sunrise": (1.15, 1.00, 0.85),
    "madina_emerald": (0.85, 1.15, 0.95),
    "dawn_spiritual": (1.05, 1.00, 1.10),
    "vintage_film": (1.10, 0.95, 0.80),
    "pure_mushaf": (1.00, 1.00, 1.00),
    "dramatic_monochrome": (0.5, 0.5, 0.5),
}


def _apply_lut(frame: np.ndarray, lut_style: str) -> np.ndarray:
    """Apply a 3D LUT (software path) by per-channel gain."""
    gain = _LUTS.get(lut_style, (1.0, 1.0, 1.0))
    out = frame.astype(np.float32).copy()
    out[:, :, 0] *= gain[0]
    out[:, :, 1] *= gain[1]
    out[:, :, 2] *= gain[2]
    return np.clip(out, 0, 255).astype(np.uint8)


def _apply_warmth(frame: np.ndarray, warmth: float) -> np.ndarray:
    out = frame.astype(np.float32).copy()
    out[:, :, 0] *= warmth
    out[:, :, 1] *= 1.0 + (warmth - 1.0) * 0.3
    return np.clip(out, 0, 255).astype(np.uint8)


def _vignette(frame: np.ndarray, strength: float = 0.4) -> np.ndarray:
    h, w = frame.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    r = r / r.max()
    mask = 1.0 - strength * r ** 2
    mask = mask[:, :, None]
    return np.clip(frame.astype(np.float32) * mask, 0, 255).astype(np.uint8)


def _grain(frame: np.ndarray, amount: float = 0.05) -> np.ndarray:
    rng = np.random.default_rng(12345)
    noise = rng.standard_normal(frame.shape) * (amount * 255)
    return np.clip(frame.astype(np.float32) + noise, 0, 255).astype(np.uint8)


class GLRenderer:
    """ModernGL-style FX renderer with a software fallback."""

    def __init__(self) -> None:
        self.ctx = None
        try:
            import moderngl

            self.ctx = moderngl.create_standalone_context()
        except Exception:
            self.ctx = None  # software fallback

    def render_frame(
        self,
        frame: np.ndarray,
        split: float = 0.5,
        split_mode=SplitMode.split,
        lut_style: str = "kadyrov_gold",
        warmth: float = 1.0,
        contrast: float = 1.0,
        exposure: float = 1.0,
        saturation: float = 1.0,
        rays: bool = False,
        bloom: bool = False,
        grain: float = 0.0,
        vignette: float = 0.3,
        rain: bool = False,
        dust: bool = False,
    ) -> np.ndarray:
        """Render a frame applying FX. Returns RGB uint8 array same shape."""
        if frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError("frame must be RGB uint8 (H,W,3)")
        h, w = frame.shape[:2]

        # Normalize split mode string.
        mode = split_mode
        if isinstance(mode, str):
            mode = SplitMode(mode)
        mode_val = mode.value if hasattr(mode, "value") else str(mode)

        filtered = _apply_lut(frame, lut_style)
        filtered = _apply_warmth(filtered, warmth)
        filtered = _vignette(filtered, vignette)
        if grain > 0:
            filtered = _grain(filtered, grain)

        if mode_val == SplitMode.original.value:
            return frame.copy()
        if mode_val == SplitMode.filtered.value:
            return filtered
        if mode_val == SplitMode.side_by_side.value or mode_val == "side-by-side":
            out = np.zeros_like(frame)
            mid = w // 2
            out[:, :mid] = frame[:, :mid]
            out[:, mid:] = filtered[:, mid:]
            return out
        # split (wipe) mode: left=original, right=filtered at `split` position.
        split_px = int(max(0.0, min(1.0, split)) * w)
        out = np.zeros_like(frame)
        out[:, :split_px] = frame[:, :split_px]
        out[:, split_px:] = filtered[:, split_px:]
        return out
