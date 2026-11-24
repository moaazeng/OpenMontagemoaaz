"""Noor Video FX tool — wraps GLRenderer + FaceDepthAI + VideoDecoder.

Exposes the Golden Order video FX chain (LUT3D, split wipe, rays, bloom,
grain, vignette, face-tracked split) as an OpenMontage BaseTool.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from lib.noor.gl_renderer import GLRenderer
from lib.noor.video_decoder import VideoDecoder

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)


class NoorVideoFX(BaseTool):
    name = "noor_video_fx"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "video_processing"
    provider = "noor"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = [
        "python:av",
        "python:moderngl",
        "python:numpy",
        "cmd:ffmpeg",
    ]
    install_instructions = (
        "pip install -r requirements-noor.txt (av, moderngl, numpy); "
        "ffmpeg must be on PATH."
    )
    input_schema = {
        "type": "object",
        "required": ["input_path", "output_path"],
        "properties": {
            "input_path": {"type": "string"},
            "output_path": {"type": "string"},
            "split": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.5},
            "split_mode": {
                "type": "string",
                "enum": ["split", "filtered", "original", "side-by-side"],
                "default": "split",
            },
            "lut_style": {"type": "string", "default": "kadyrov_gold"},
            "warmth": {"type": "number", "default": 1.0},
            "contrast": {"type": "number", "default": 1.0},
            "exposure": {"type": "number", "default": 1.0},
            "saturation": {"type": "number", "default": 1.0},
            "grain": {"type": "number", "default": 0.0},
            "vignette": {"type": "number", "default": 0.3},
        },
        "additionalProperties": False,
    }
    output_schema = {
        "type": "object",
        "required": ["output", "frames_processed"],
        "properties": {
            "output": {"type": "string"},
            "frames_processed": {"type": "integer"},
        },
    }
    idempotency_key_fields = ["input_path", "output_path", "lut_style"]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        src = inputs["input_path"]
        dst = Path(inputs["output_path"])
        dst.parent.mkdir(parents=True, exist_ok=True)

        renderer = GLRenderer()
        decoder = VideoDecoder(src)
        frames = list(decoder.decode())
        if not frames:
            return ToolResult(
                success=False,
                error="no frames decoded",
                duration_seconds=round(time.perf_counter() - start, 4),
            )

        split = float(inputs.get("split", 0.5))
        split_mode = inputs.get("split_mode", "split")
        lut_style = inputs.get("lut_style", "kadyrov_gold")
        warmth = float(inputs.get("warmth", 1.0))
        contrast = float(inputs.get("contrast", 1.0))
        exposure = float(inputs.get("exposure", 1.0))
        saturation = float(inputs.get("saturation", 1.0))
        grain = float(inputs.get("grain", 0.0))
        vignette = float(inputs.get("vignette", 0.3))

        rendered = []
        for f in frames:
            out = renderer.render_frame(
                f,
                split=split,
                split_mode=split_mode,
                lut_style=lut_style,
                warmth=warmth,
                contrast=contrast,
                exposure=exposure,
                saturation=saturation,
                grain=grain,
                vignette=vignette,
            )
            rendered.append(out)

        # Write a representative frame as a PNG artifact (single-frame summary).
        try:
            from PIL import Image

            Image.fromarray(rendered[0]).save(dst.with_suffix(".png"))
        except Exception:
            pass

        # Commit a stitched MP4 if ffmpeg is available.
        import shutil
        import subprocess

        if shutil.which("ffmpeg"):
            # Write frames to a temp dir then encode.
            tmp = dst.parent / "_noor_frames"
            tmp.mkdir(exist_ok=True)
            for i, fr in enumerate(rendered):
                from PIL import Image

                Image.fromarray(fr).save(tmp / f"frame_{i:05d}.png")
            subprocess.run(
                [
                    "ffmpeg", "-v", "error", "-y",
                    "-framerate", "24",
                    "-i", str(tmp / "frame_%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    str(dst),
                ],
                capture_output=True, timeout=120,
            )
            # cleanup
            for p in tmp.glob("*.png"):
                p.unlink(missing_ok=True)
            try:
                tmp.rmdir()
            except Exception:
                pass

        return ToolResult(
            success=True,
            data={
                "output": str(dst),
                "frames_processed": len(rendered),
            },
            artifacts=[str(dst)],
            cost_usd=0.0,
            duration_seconds=round(time.perf_counter() - start, 4),
        )
