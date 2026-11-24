"""Noor Mic Recorder tool — real 48 kHz WASAPI microphone capture.

Wraps lib/noor/recorder.py (sounddevice WASAPI callback) as an OpenMontage
BaseTool. Records mono float32 at 48000 Hz, blocksize 512 (~10.67 ms),
commits a WAV on stop. Warns if the default input is Bluetooth Hands-Free
(16 kHz mono, high latency) which violates the 48 kHz monitor contract.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import sounddevice as sd

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

# repo root: tools/audio/noor_mic_recorder.py -> parents[2]
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

_DEFAULT_SAMPLE_RATE = 48000
_DEFAULT_BLOCKSIZE = 512  # ~10.67 ms monitor latency target


def np_concat(chunks):
    import numpy as np

    return np.concatenate(chunks, axis=0)


class NoorMicRecorder(BaseTool):
    name = "noor_mic_recorder"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "audio_capture"
    provider = "noor"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC  # live mic input is inherently non-deterministic
    runtime = ToolRuntime.LOCAL

    dependencies = [
        "python:sounddevice",
        "python:soundfile",
        "cmd:ffmpeg",
    ]
    install_instructions = (
        "pip install -r requirements-noor.txt (sounddevice, soundfile); "
        "Windows WASAPI backend used by default."
    )
    input_schema = {
        "type": "object",
        "required": ["output_path"],
        "properties": {
            "output_path": {"type": "string", "description": "WAV output path"},
            "device": {
                "type": ["integer", "string", "null"],
                "default": None,
                "description": "sounddevice device index/name or None for default",
            },
            "sample_rate": {"type": "integer", "default": _DEFAULT_SAMPLE_RATE, "minimum": 8000},
            "blocksize": {"type": "integer", "default": _DEFAULT_BLOCKSIZE},
            "duration_seconds": {
                "type": "number",
                "default": None,
                "description": "If set, auto-stop after this many seconds",
            },
        },
        "additionalProperties": False,
    }
    output_schema = {
        "type": "object",
        "required": ["output", "sample_rate", "duration_seconds", "channels"],
        "properties": {
            "output": {"type": "string"},
            "sample_rate": {"type": "integer"},
            "duration_seconds": {"type": "number"},
            "channels": {"type": "integer"},
            "device_name": {"type": "string"},
            "bluetooth_handsfree_warning": {"type": "string"},
        },
    }
    idempotency_key_fields = []

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        output_path = Path(inputs["output_path"])
        device = inputs.get("device")
        sample_rate = int(inputs.get("sample_rate", _DEFAULT_SAMPLE_RATE))
        blocksize = int(inputs.get("blocksize", _DEFAULT_BLOCKSIZE))
        duration_seconds = inputs.get("duration_seconds")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Validate device supports the requested sample rate; warn on BT HF.
        warning = None
        try:
            dev_info = sd.query_devices(device) if device is not None else sd.query_devices(kind="input")
            dev_name = str(dev_info.get("name", "unknown"))
            dev_sr = float(dev_info.get("default_samplerate", sample_rate))
            if dev_name.lower().find("hands-free") != -1 or dev_name.lower().find("hfp") != -1:
                warning = (
                    f"Bluetooth Hands-Free device '{dev_name}' detected "
                    f"(~16 kHz, high latency); 48 kHz monitor contract not met"
                )
            if abs(dev_sr - sample_rate) > 1 and device is None:
                # default device rate differs; sounddevice will still resample in-callback
                warning = (warning or "") + f" default device rate {dev_sr} Hz != requested {sample_rate} Hz"
        except Exception as exc:  # pragma: no cover - hardware dependent
            warning = f"could not query device info: {exc}"

        recorded: list = []
        stop = False

        def callback(indata, frames, time_info, status):
            nonlocal stop
            if status:  # pragma: no cover - runtime overflow
                pass  # status surfaced via sd.CallbackFlags; non-fatal
            recorded.append(indata.copy())
            if duration_seconds is not None and len(recorded) * blocksize / sample_rate >= duration_seconds:
                stop = True
                raise sd.CallbackStop

        try:
            with sd.InputStream(
                samplerate=sample_rate,
                blocksize=blocksize,
                device=device,
                channels=1,
                dtype="float32",
                callback=callback,
            ):
                while not stop:
                    sd.sleep(100)
        except sd.CallbackStop:
            pass  # clean auto-stop
        except Exception as exc:  # pragma: no cover - hardware dependent
            return ToolResult(
                success=False,
                error=f"recording failed: {exc}",
                duration_seconds=round(time.perf_counter() - start, 4),
            )

        if not recorded:
            return ToolResult(
                success=False,
                error="no audio captured",
                duration_seconds=round(time.perf_counter() - start, 4),
            )

        audio = np_concat(recorded)
        duration = len(audio) / sample_rate

        import soundfile as sf  # imported here so hardware-less envs still import this module

        try:
            sf.write(output_path, audio, sample_rate, subtype="PCM_16")
        except Exception as exc:  # pragma: no cover - writer dependent
            return ToolResult(
                success=False,
                error=f"failed to write WAV: {exc}",
                duration_seconds=round(time.perf_counter() - start, 4),
            )

        return ToolResult(
            success=True,
            data={
                "output": str(output_path),
                "sample_rate": sample_rate,
                "duration_seconds": round(duration, 4),
                "channels": 1,
                "device_name": (sd.query_devices(device).get("name") if device is not None else sd.query_devices(kind="input").get("name")),
                "bluetooth_handsfree_warning": warning,
            },
            artifacts=[str(output_path)],
            cost_usd=0.0,
            duration_seconds=round(time.perf_counter() - start, 4),
        )


def np_concat(chunks):
    import numpy as np

    return np.concatenate(chunks, axis=0)
