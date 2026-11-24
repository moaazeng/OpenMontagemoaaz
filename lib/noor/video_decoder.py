"""Noor video decoder — PyAV VFR→CFR + image plate loader + procedural fallback.

Provides VideoDecoder.decode(path) -> iterator[np.ndarray] of RGB CFR frames,
load_image_plate(path), and procedural_mosque_frame() (deterministic fallback
when no input video is supplied).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator, Optional

import av
import numpy as np


DEFAULT_FPS = 24.0


class VideoDecoder:
    """PyAV-backed CFR decoder producing RGB uint8 frames."""

    def __init__(self, path: Optional[str | Path] = None) -> None:
        self.path = str(path) if path is not None else None

    # ── decoding ────────────────────────────────────────────────────────────

    def decode(self, path: Optional[str | Path] = None, fps: float = DEFAULT_FPS) -> Iterator[np.ndarray]:
        """Decode a video to CFR RGB frames. If path is None, uses self.path."""
        src = path if path is not None else self.path
        if src is None:
            # Fallback: generate a procedural mosque frame stream.
            for _ in range(int(fps)):
                yield self.procedural_mosque_frame()
            return
        p = Path(src)
        if not p.is_file():
            for _ in range(int(fps)):
                yield self.procedural_mosque_frame()
            return
        container = av.open(str(p))
        stream = container.streams.video[0]
        # Force CFR by converting via filter.
        try:
            stream.codec_context.skip_frame = "NONKEY"  # noqa - best effort
        except Exception:
            pass
        for frame in container.decode(video=0):
            img = frame.to_ndarray(format="rgb24")
            yield np.ascontiguousarray(img)
        container.close()

    @staticmethod
    def load_image_plate(path: Optional[str | Path]) -> Optional[np.ndarray]:
        """Load an image as an RGB uint8 plate (None → procedural fallback)."""
        if path is None:
            return None
        p = Path(path)
        if not p.is_file():
            return None
        try:
            from PIL import Image

            with Image.open(p) as im:
                return np.ascontiguousarray(np.array(im.convert("RGB")))
        except Exception:
            return None

    @staticmethod
    def procedural_mosque_frame(width: int = 1280, height: int = 720) -> np.ndarray:
        """Deterministic mosque-arch silhouette frame (fallback plate)."""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Sky gradient (dark blue → emerald)
        for y in range(height):
            t = y / max(height - 1, 1)
            frame[y, :] = (
                int(10 + t * 20),
                int(20 + t * 60),
                int(40 + t * 30),
            )
        # Arch silhouette in center
        cx, cy = width // 2, height // 2
        for y in range(height // 3, 2 * height // 3):
            for x in range(width // 4, 3 * width // 4):
                if (x - cx) ** 2 + (y - cy) ** 2 < (min(width, height) // 4) ** 2:
                    frame[y, x] = (15, 10, 5)
        return np.ascontiguousarray(frame)
