"""Noor face tracking + skin mask + depth map.

MediaPipe 478-point face mesh when available; otherwise a deterministic
center-face fallback so the module runs headless/CI without a webcam.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np


class FaceDepthAI:
    """Face tracking, skin masking, and depth-map estimation."""

    def __init__(self) -> None:
        self._mp = None
        try:
            import mediapipe as mp

            self._mp = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
            )
        except Exception:
            self._mp = None
        # EMA state for track_face.
        self._ema_x: Optional[float] = None
        self._ema_y: Optional[float] = None
        self._ema_r: Optional[float] = None
        self._alpha = 0.3

    def track_face(self, frame: np.ndarray) -> Tuple[float, float, float]:
        """Return (x, y, radius) of the detected face center (EMA smoothed)."""
        h, w = frame.shape[:2]
        cx, cy, r = w / 2.0, h / 2.0, min(w, h) / 4.0

        if self._mp is not None:
            try:
                rgb = frame[:, :, ::-1] if frame.shape[2] == 3 else frame
                res = self._mp.process(rgb)
                if res.multi_face_landmarks:
                    lm = res.multi_face_landmarks[0].landmark
                    xs = [p.x * w for p in lm]
                    ys = [p.y * h for p in lm]
                    cx = float(np.mean(xs))
                    cy = float(np.mean(ys))
                    r = float((max(xs) - min(xs) + max(ys) - min(ys)) / 4.0)
            except Exception:
                pass

        # EMA smoothing.
        if self._ema_x is None:
            self._ema_x, self._ema_y, self._ema_r = cx, cy, r
        else:
            self._ema_x = self._alpha * cx + (1 - self._alpha) * self._ema_x
            self._ema_y = self._alpha * cy + (1 - self._alpha) * self._ema_y
            self._ema_r = self._alpha * r + (1 - self._alpha) * self._ema_r

        return float(self._ema_x), float(self._ema_y), float(self._ema_r)

    def skin_mask(self, frame: np.ndarray) -> np.ndarray:
        """Return a (H,W) uint8 skin mask (0/255)."""
        h, w = frame.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        # YCrCb skin detection (robust, no ML).
        try:
            import cv2

            ycrcb = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
            lower = np.array([0, 133, 77], dtype=np.uint8)
            upper = np.array([255, 173, 127], dtype=np.uint8)
            m = cv2.inRange(ycrcb, lower, upper)
            mask = m.astype(np.uint8)
        except Exception:
            # Fallback: central ellipse.
            yy, xx = np.mgrid[0:h, 0:w]
            cx, cy = w / 2, h / 2
            rx, ry = w / 4, h / 3
            mask = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1).astype(np.uint8) * 255
        return mask

    def depth_map(self, frame: np.ndarray) -> np.ndarray:
        """Return a (H,W) float32 depth/alpha map in [0,1]."""
        h, w = frame.shape[:2]
        # Gradient-based pseudo-depth (fallback when Depth-Anything unavailable).
        gray = frame.mean(axis=2).astype(np.float32)
        # Normalize to [0,1].
        mn, mx = float(gray.min()), float(gray.max())
        if mx - mn < 1e-6:
            return np.zeros((h, w), dtype=np.float32)
        depth = (gray - mn) / (mx - mn)
        # Invert so foreground (brighter) is closer → higher alpha.
        depth = 1.0 - depth
        return depth.astype(np.float32)
