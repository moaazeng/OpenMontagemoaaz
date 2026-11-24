"""Noor Mic Recorder tool — real 48 kHz WASAPI microphone capture.

Delegates capture to lib/noor/recorder.py (NoorRecorder: sounddevice WASAPI
callback, float32 mono, profiles NEUMANN/HARAM/DEEP_BASS/RAW) and exposes it
as an OpenMontage BaseTool. Records mono float32 at 48000 Hz, blocksize 512
(~10.67 ms monitor latency target), commits a WAV on stop. Warns if the
default input is Bluetooth Hands-Free (16 kHz mono, high latency) which
violates the 48 kHz monitor contract.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

from lib.noor.recorder import DEFAULT_SAMPLE_RATE, DEFAULT_BLOCKSIZE, NoorRecorder
from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)


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
            "sample_rate": {"type": "integer", "default": DEFAULT_SAMPLE_RATE, "minimum": 8000},
            "blocksize": {"type": "integer", "default": DEFAULT_BLOCKSIZE},
            "profile": {
                "type": "string",
                "enum": ["NEUMANN", "HARAM", "DEEP_BASS", "RAW"],
                "default": "RAW",
                "description": "Mic profile coloration applied on commit",
            },
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
            "profile": {"type": "string"},
            "bluetooth_handsfree_warning": {"type": "string"},
        },
    }
    idempotency_key_fields = []

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        output_path = Path(inputs["output_path"])
        device = inputs.get("device")
        sample_rate = int(inputs.get("sample_rate", DEFAULT_SAMPLE_RATE))
        blocksize = int(inputs.get("blocksize", DEFAULT_BLOCKSIZE))
        profile = str(inputs.get("profile", "RAW"))
        duration_seconds = inputs.get("duration_seconds")

        recorder = NoorRecorder()

        # Validate device supports the requested sample rate; warn on BT HF.
        warning = None
        try:
            dev_info = (
                recorder.default_device() if device is None
                else _device_by_index(recorder, device)
            )
            dev_name = dev_info.get("name", "unknown")
            dev_sr = float(dev_info.get("default_samplerate", sample_rate))
            if recorder.is_bluetooth_handsfree(dev_name):
                warning = (
                    f"Bluetooth Hands-Free device '{dev_name}' detected "
                    f"(~16 kHz, high latency); 48 kHz monitor contract not met"
                )
            if abs(dev_sr - sample_rate) > 1 and device is None:
                warning = (warning or "") + (
                    f" default device rate {dev_sr} Hz != requested {sample_rate} Hz"
                )
        except Exception as exc:  # pragma: no cover - hardware dependent
            warning = f"could not query device info: {exc}"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        stopped = threading.Event()

        def on_audio(indata):
            # Auto-stop after duration_seconds.
            if duration_seconds is not None and recorder._start_time is not None:
                if time.time() - recorder._start_time >= duration_seconds:
                    stopped.set()

        recorder.start(
            device=device,
            profile=profile,
            sample_rate=sample_rate,
            blocksize=blocksize,
            on_audio=on_audio,
        )

        # Poll until recorder stops itself (duration) — but duration is
        # advisory here; callers typically stop via a separate stop() call.
        # For the BaseTool single-call contract we capture for duration or
        # until a short timeout. Hardware capture is bounded by duration_seconds
        # when provided; otherwise capture a short buffer and stop.
        max_wait = duration_seconds if duration_seconds is not None else 2.0
        deadline = time.time() + max_wait
        while time.time() < deadline and recorder.recording and not stopped.is_set():
            time.sleep(0.05)

        wav_path = recorder.stop()
        if wav_path is None:
            return ToolResult(
                success=False,
                error="no audio captured",
                duration_seconds=round(time.perf_counter() - start, 4),
            )

        # Move committed temp WAV to the requested output path.
        import shutil

        shutil.move(str(wav_path), str(output_path))

        try:
            import soundfile as sf

            info = sf.info(str(output_path))
            duration = info.frames / info.samplerate
            channels = info.channels
        except Exception:  # pragma: no cover
            duration = 0.0
            channels = 1

        dev_name = (
            recorder.default_device().get("name", "unknown") if device is None else str(device)
        )

        return ToolResult(
            success=True,
            data={
                "output": str(output_path),
                "sample_rate": sample_rate,
                "duration_seconds": round(duration, 4),
                "channels": channels,
                "device_name": dev_name,
                "profile": profile,
                "bluetooth_handsfree_warning": warning,
            },
            artifacts=[str(output_path)],
            cost_usd=0.0,
            duration_seconds=round(time.perf_counter() - start, 4),
        )


def _device_by_index(recorder: NoorRecorder, device) -> dict:
    import sounddevice as sd

    dev = sd.query_devices(device)
    return {
        "name": str(dev.get("name", "unknown")),
        "default_samplerate": float(dev.get("default_samplerate", 0)),
        "max_input_channels": int(dev.get("max_input_channels", 0)),
    }


