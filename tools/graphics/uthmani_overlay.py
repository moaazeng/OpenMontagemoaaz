"""Uthmani Overlay tool — renders Uthmani calligraphy + waveform onto a frame.

Wraps lib/noor/calligraphy.py as an OpenMontage BaseTool.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from lib.noor.calligraphy import render_uthmani, render_waveform

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)


class UthmaniOverlay(BaseTool):
    name = "uthmani_overlay"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "graphics"
    provider = "noor"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = [
        "python:PIL",
        "python:numpy",
    ]
    install_instructions = "pip install -r requirements-noor.txt (Pillow, numpy)"
    input_schema = {
        "type": "object",
        "required": ["output_path"],
        "properties": {
            "output_path": {"type": "string"},
            "text": {"type": "string", "default": "بِسْمِ ٱللَّٰهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ"},
            "theme": {
                "type": "string",
                "enum": ["uthmani_gold", "pure_white", "royal_emerald", "amber_glow"],
                "default": "uthmani_gold",
            },
            "waveform_style": {
                "type": "string",
                "enum": ["solid", "glass_modern", "glass_bars", "vintage_dots"],
                "default": "solid",
            },
            "aspect": {
                "type": "string",
                "enum": ["9:16", "16:9", "1:1", "4:5"],
                "default": "9:16",
            },
            "canvas_size": {
                "type": "array",
                "items": {"type": "integer"},
                "default": [1080, 1920],
            },
        },
        "additionalProperties": False,
    }
    output_schema = {
        "type": "object",
        "required": ["output"],
        "properties": {"output": {"type": "string"}},
    }
    idempotency_key_fields = ["output_path", "text", "theme"]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        out = Path(inputs["output_path"])
        out.parent.mkdir(parents=True, exist_ok=True)

        text = inputs.get("text", "بِسْمِ ٱللَّٰهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ")
        theme = inputs.get("theme", "uthmani_gold")
        wf_style = inputs.get("waveform_style", "solid")
        aspect = inputs.get("aspect", "9:16")
        canvas = tuple(inputs.get("canvas_size", [1080, 1920]))

        img = render_uthmani(text, theme=theme, canvas_size=canvas, aspect=aspect)

        # Optional waveform overlay (bottom band).
        try:
            import numpy as np

            samples = np.sin(2 * np.pi * 440 * np.arange(48000) / 48000).astype("float32")
            wf = render_waveform(samples, style=wf_style, canvas_size=canvas)
            # Composite waveform onto bottom 15% of the calligraphy canvas.
            from PIL import Image

            img = Image.alpha_composite if False else img
            # Simple paste of waveform into bottom band.
            wf_crop = wf.crop((0, int(canvas[1] * 0.85), canvas[0], canvas[1]))
            img.paste(wf_crop, (0, int(canvas[1] * 0.85)))
        except Exception:
            pass

        img.save(out)
        return ToolResult(
            success=True,
            data={"output": str(out)},
            artifacts=[str(out)],
            cost_usd=0.0,
            duration_seconds=round(time.perf_counter() - start, 4),
        )
