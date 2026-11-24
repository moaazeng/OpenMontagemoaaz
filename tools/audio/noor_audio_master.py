"""Noor Audio Master tool — wraps the Golden Order DSP engine.

Exposes lib/noor/audio_dsp.py as an OpenMontage BaseTool so the agentic
pipeline (and the noor_studio /dsp route) can master audio deterministically:
pre-amp → denoise → gate → de-esser → mic cal → deep bass → 6-band EQ →
compressor → harmonics → echo → mosque reverb → EQ → -1.0 dBTP brickwall
limiter. Output is always finite, same-shaped float32 PCM, never exceeding
-1.0 dBTP.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import soundfile as sf

from lib.noor.audio_dsp import GoldenOrderDSP, SAMPLE_RATE
from lib.noor.schemas import DSPConfig

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)

# repo root: tools/audio/noor_audio_master.py -> parents[2]
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class NoorAudioMaster(BaseTool):
    name = "noor_audio_master"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "audio_processing"
    provider = "noor"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = [
        "python:pedalboard",
        "python:soundfile",
        "python:scipy",
        "python:pyloudnorm",
        "python:numpy",
        "cmd:ffmpeg",
    ]
    install_instructions = (
        "pip install -r requirements-noor.txt (installs pedalboard, soundfile, "
        "scipy, pyloudnorm, numpy); ffmpeg must be on PATH for container "
        "conversion if requested."
    )
    input_schema = {
        "type": "object",
        "required": ["input_path", "output_path"],
        "properties": {
            "input_path": {"type": "string", "description": "Source audio file (WAV/MP3/FLAC/OGG/M4A)"},
            "output_path": {"type": "string", "description": "Mastered output path (WAV/MP3/FLAC)"},
            "preset": {
                "type": "string",
                "enum": ["clean_speech", "quranic_recitation", "viral_capcut", "podcast"],
                "default": "quranic_recitation",
                "description": "Named DSP preset (see styles/noor/official_presets.yaml)",
            },
            # DSPConfig overrides (all optional, bounded in the model).
            "preamp_gain": {"type": "number", "minimum": 0.5, "maximum": 4.0},
            "eq_band_1_gain_db": {"type": "number", "minimum": -12.0, "maximum": 12.0},
            "eq_band_2_gain_db": {"type": "number", "minimum": -12.0, "maximum": 12.0},
            "eq_band_3_gain_db": {"type": "number", "minimum": -12.0, "maximum": 12.0},
            "eq_band_4_gain_db": {"type": "number", "minimum": -12.0, "maximum": 12.0},
            "eq_band_5_gain_db": {"type": "number", "minimum": -12.0, "maximum": 12.0},
            "eq_band_6_gain_db": {"type": "number", "minimum": -12.0, "maximum": 12.0},
            "lut_intensity": {"type": "integer", "minimum": 0, "maximum": 100},
            "deep_bass_mix": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "capcut_noise_mode": {
                "type": "string",
                "enum": ["off", "standard", "pro_clean", "extreme"],
            },
            "capcut_deep_bass_mode": {
                "type": "string",
                "enum": ["off", "warm", "capcut_pro", "kadyrov_elite"],
            },
            "mobile_mic_calibration": {
                "type": "string",
                "enum": ["studio_neumann", "broadcast_shure", "smooth_warm", "raw_calibrated"],
            },
            "mosque_acoustic_space": {
                "type": "string",
                "enum": ["haram_makkah", "prophet_madina", "alaqsa", "pro_studio", "dome_hall"],
            },
            "lut_style": {
                "type": "string",
                "enum": [
                    "kadyrov_gold", "royal_dark", "makkah_sunrise", "madina_emerald",
                    "dawn_spiritual", "vintage_film", "pure_mushaf", "dramatic_monochrome",
                ],
            },
        },
        "additionalProperties": False,
    }
    output_schema = {
        "type": "object",
        "required": ["output", "sample_rate", "duration_seconds", "true_peak_db_tp"],
        "properties": {
            "output": {"type": "string"},
            "sample_rate": {"type": "integer"},
            "duration_seconds": {"type": "number"},
            "true_peak_db_tp": {"type": "number"},
            "lufs_integrated": {"type": "number"},
            "format": {"type": "string"},
        },
    }
    artifact_schema = {"$ref": "openmontage/artifacts/noor_dsp_config"}
    supports = {
        "formats_in": ["wav", "mp3", "flac", "ogg", "m4a"],
        "formats_out": ["wav", "flac", "mp3"],
        "sample_rate_hz": SAMPLE_RATE,
        "max_duration_seconds": None,
    }
    idempotency_key_fields = ["input_path", "output_path", "preset"]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        input_path = inputs["input_path"]
        output_path = inputs["output_path"]

        src = Path(input_path)
        if not src.is_file():
            return ToolResult(
                success=False,
                error=f"input audio not found: {input_path}",
                duration_seconds=time.perf_counter() - start,
            )

        try:
            data, sr = sf.read(src, always_2d=False, dtype="float32")
        except Exception as exc:  # pragma: no cover - decoder dependent
            return ToolResult(
                success=False,
                error=f"failed to decode input: {exc}",
                duration_seconds=time.perf_counter() - start,
            )

        # Build DSP config from preset + overrides.
        config = self._config_from_inputs(inputs)

        dsp = GoldenOrderDSP(sample_rate=SAMPLE_RATE)
        mastered = dsp.process(data, config)
        analysis = dsp.analyze(mastered)

        dst = Path(output_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            sf.write(dst, mastered, SAMPLE_RATE, subtype="PCM_16")
        except Exception as exc:  # pragma: no cover - writer dependent
            return ToolResult(
                success=False,
                error=f"failed to write output: {exc}",
                duration_seconds=time.perf_counter() - start,
            )

        duration = len(mastered) / SAMPLE_RATE
        return ToolResult(
            success=True,
            data={
                "output": str(dst),
                "sample_rate": SAMPLE_RATE,
                "duration_seconds": round(duration, 4),
                "true_peak_db_tp": analysis.true_peak_db_tp,
                "lufs_integrated": analysis.lufs_integrated,
                "format": dst.suffix.lstrip("."),
            },
            artifacts=[str(dst)],
            cost_usd=0.0,
            duration_seconds=round(time.perf_counter() - start, 4),
        )

    # ── internals ───────────────────────────────────────────────────────────

    def _config_from_inputs(self, inputs: dict[str, Any]) -> DSPConfig:
        """Map preset name + explicit overrides to a DSPConfig."""
        preset = inputs.get("preset", "quranic_recitation")
        base = _PRESETS.get(preset, _PRESETS["quranic_recitation"])

        # Apply explicit overrides on top of the preset base.
        override_keys = [
            "preamp_gain",
            "eq_band_1_gain_db",
            "eq_band_2_gain_db",
            "eq_band_3_gain_db",
            "eq_band_4_gain_db",
            "eq_band_5_gain_db",
            "eq_band_6_gain_db",
            "lut_intensity",
            "deep_bass_mix",
            "capcut_noise_mode",
            "capcut_deep_bass_mode",
            "mobile_mic_calibration",
            "mosque_acoustic_space",
            "lut_style",
        ]
        merged = dict(base)
        for key in override_keys:
            if key in inputs and inputs[key] is not None:
                merged[key] = inputs[key]
        return DSPConfig(**merged)


_PRESETS: dict[str, dict[str, Any]] = {
    "clean_speech": {
        "preamp_gain": 1.0,
        "eq_band_1_gain_db": 0.0,
        "eq_band_2_gain_db": 0.0,
        "eq_band_3_gain_db": 0.0,
        "eq_band_4_gain_db": 0.0,
        "eq_band_5_gain_db": 0.0,
        "eq_band_6_gain_db": 0.0,
        "lut_intensity": 50,
        "deep_bass_mix": 0.0,
        "capcut_noise_mode": "pro_clean",
        "capcut_deep_bass_mode": "off",
        "mobile_mic_calibration": "broadcast_shure",
        "mosque_acoustic_space": "pro_studio",
        "lut_style": "pure_mushaf",
    },
    "quranic_recitation": {
        "preamp_gain": 1.4,
        "eq_band_1_gain_db": 1.0,
        "eq_band_2_gain_db": 0.0,
        "eq_band_3_gain_db": 2.0,
        "eq_band_4_gain_db": 0.0,
        "eq_band_5_gain_db": -1.0,
        "eq_band_6_gain_db": 0.0,
        "lut_intensity": 75,
        "deep_bass_mix": 0.2,
        "capcut_noise_mode": "standard",
        "capcut_deep_bass_mode": "off",
        "mobile_mic_calibration": "studio_neumann",
        "mosque_acoustic_space": "haram_makkah",
        "lut_style": "makkah_sunrise",
    },
    "viral_capcut": {
        "preamp_gain": 1.6,
        "eq_band_1_gain_db": 3.0,
        "eq_band_2_gain_db": 2.0,
        "eq_band_3_gain_db": 1.0,
        "eq_band_4_gain_db": 0.0,
        "eq_band_5_gain_db": 0.0,
        "eq_band_6_gain_db": 0.0,
        "lut_intensity": 90,
        "deep_bass_mix": 0.7,
        "capcut_noise_mode": "off",
        "capcut_deep_bass_mode": "capcut_pro",
        "mobile_mic_calibration": "broadcast_shure",
        "mosque_acoustic_space": "dome_hall",
        "lut_style": "kadyrov_gold",
    },
    "podcast": {
        "preamp_gain": 1.3,
        "eq_band_1_gain_db": -1.0,
        "eq_band_2_gain_db": 0.0,
        "eq_band_3_gain_db": 1.0,
        "eq_band_4_gain_db": 0.0,
        "eq_band_5_gain_db": -1.0,
        "eq_band_6_gain_db": 0.0,
        "lut_intensity": 60,
        "deep_bass_mix": 0.1,
        "capcut_noise_mode": "standard",
        "capcut_deep_bass_mode": "warm",
        "mobile_mic_calibration": "studio_neumann",
        "mosque_acoustic_space": "pro_studio",
        "lut_style": "pure_mushaf",
    },
}
