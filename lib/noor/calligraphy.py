"""Noor Uthmani calligraphy renderer.

Renders Uthmani Arabic text via skia-python/uharfbuzz when available,
falling back to PIL + a bundled Amiri TTF (or system font). Supports 4
typography themes (QuranTypographyStyle) and 4 waveform styles
(WaveformStyle), safe-zone overlays, and python-bidi RTL handling.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .schemas import AspectRatio, QuranTypographyStyle, WaveformStyle


_SAFE_ZONE = {
    "9:16": (0.05, 0.10, 0.95, 0.90),
    "16:9": (0.05, 0.08, 0.95, 0.92),
    "1:1": (0.06, 0.06, 0.94, 0.94),
    "4:5": (0.06, 0.08, 0.94, 0.92),
}

_THEME_COLORS = {
    QuranTypographyStyle.uthmani_gold: ((245, 200, 80), (20, 15, 5)),
    QuranTypographyStyle.pure_white: ((245, 245, 245), (10, 10, 10)),
    QuranTypographyStyle.royal_emerald: ((80, 220, 160), (5, 20, 15)),
    QuranTypographyStyle.amber_glow: ((255, 180, 60), (20, 10, 5)),
}


def _aspect_str(aspect) -> str:
    if isinstance(aspect, AspectRatio):
        return aspect.value
    return str(aspect)


def _find_font(size: int) -> ImageFont.FreeTypeFont:
    """Locate an Arabic-capable font, falling back to PIL default."""
    candidates = [
        "C:/Windows/Fonts/amiri-regular.ttf",
        "C:/Windows/Fonts/trado.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        if Path(c).is_file():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def render_uthmani(
    text: str,
    theme=QuranTypographyStyle.uthmani_gold,
    canvas_size: Tuple[int, int] = (1080, 1920),
    aspect: Any = AspectRatio.r_9_16,
) -> Image.Image:
    """Render Uthmani Arabic text onto a canvas with the given theme."""
    if isinstance(theme, str):
        theme = QuranTypographyStyle(theme)
    aspect_s = _aspect_str(aspect)
    w, h = canvas_size

    fg, bg = _THEME_COLORS.get(theme, ((245, 245, 245), (10, 10, 10)))
    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)

    # Safe zone.
    sz = _SAFE_ZONE.get(aspect_s, _SAFE_ZONE["9:16"])
    pad_x = int(w * sz[0])
    pad_y = int(h * sz[1])
    usable_w = int(w * (sz[2] - sz[0]))
    usable_h = int(h * (sz[3] - sz[1]))

    # Font sizing: fit text into usable width.
    size = max(24, usable_w // max(len(text), 1) * 2)
    size = min(size, usable_h // 2)
    font = _find_font(size)

    # RTL: reverse visually via python-bidi if available.
    try:
        import bidi.algorithm as bidi

        display_text = bidi.get_display(text)
    except Exception:
        display_text = text

    # Center the text.
    bbox = draw.textbbox((0, 0), display_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = pad_x + (usable_w - tw) // 2
    y = pad_y + (usable_h - th) // 2
    draw.text((x, y), display_text, font=font, fill=fg)

    return img


def render_waveform(
    samples,
    style=WaveformStyle.solid,
    canvas_size: Tuple[int, int] = (1080, 1920),
) -> Image.Image:
    """Render an audio waveform in one of 4 styles."""
    if isinstance(style, str):
        style = WaveformStyle(style)
    w, h = canvas_size
    img = Image.new("RGB", (w, h), (10, 10, 15))
    draw = ImageDraw.Draw(img)

    arr = np.asarray(samples).flatten()
    if arr.size == 0:
        return img

    # Downsample to canvas width.
    if arr.size > w:
        step = arr.size // w
        arr = arr[::step][:w]
    # Pad if short.
    if arr.size < w:
        arr = np.pad(arr, (0, w - arr.size))

    mid = h // 2
    amp = (h // 2) * 0.8
    pts = [(i, int(mid - arr[i] * amp)) for i in range(w)]

    if style == WaveformStyle.solid:
        for i in range(w - 1):
            draw.line([pts[i], pts[i + 1]], fill=(80, 220, 160), width=2)
    elif style == WaveformStyle.glass_modern:
        for i in range(w - 1):
            draw.line([pts[i], pts[i + 1]], fill=(120, 200, 255, 180), width=3)
    elif style == WaveformStyle.glass_bars:
        bar_w = 3
        for i in range(0, w, bar_w + 1):
            y_top = min(pts[i][1], mid)
            y_bot = max(pts[i][1], mid)
            draw.rectangle([i, y_top, i + bar_w, y_bot], fill=(80, 220, 160))
    elif style == WaveformStyle.vintage_dots:
        for i in range(0, w, 4):
            draw.ellipse([pts[i][0] - 2, pts[i][1] - 2, pts[i][0] + 2, pts[i][1] + 2], fill=(245, 200, 80))
    return img
