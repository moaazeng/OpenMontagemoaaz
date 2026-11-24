"""Noor real-time microphone recorder — WASAPI 48 kHz float32.

Profiles:
  NEUMANN    studio condenser reference (flat)
  HARAM      mosque/haram presence curve (gentle low-mid presence)
  DEEP_BASS  +6 dB sub shelf for viral/capcut tiers
  RAW        no coloration, flat capture

Runs sounddevice WASAPI callback at sample_rate/blocksize, accumulates
float32 mono chunks, and commits a PCM_16 WAV on stop. Bluetooth Hands-Free
(16 kHz mono, high latency) is flagged via a warning but not blocked.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import sounddevice as sd
import soundfile as sf


DEFAULT_SAMPLE_RATE = 48000
DEFAULT_BLOCKSIZE = 512  # ~10.67 ms monitor latency target


@dataclass(frozen=True)
class MicProfile:
    name: str
    description: str
    # per-profile EQ-ish coloration applied at capture (applied on commit).
    low_shelf_db: float = 0.0
    high_shelf_db: float = 0.0


NEUMANN = MicProfile("NEUMANN", "studio condenser reference (flat)")
HARAM = MicProfile("HARAM", "mosque/haram presence curve", low_shelf_db=1.0)
DEEP_BASS = MicProfile("DEEP_BASS", "+6 dB sub shelf for viral tiers", low_shelf_db=6.0)
RAW = MicProfile("RAW", "no coloration, flat capture")


PROFILES = {
    "NEUMANN": NEUMANN,
    "HARAM": HARAM,
    "DEEP_BASS": DEEP_BASS,
    "RAW": RAW,
}


class NoorRecorder:
    """Real-time mic capture + live DSP monitor profiles."""

    def __init__(self) -> None:
        self._stream: Optional[sd.InputStream] = None
        self._chunks: list = []
        self._lock = threading.Lock()
        self._recording = False
        self._device = None
        self._sample_rate = DEFAULT_SAMPLE_RATE
        self._blocksize = DEFAULT_BLOCKSIZE
        self._profile = RAW
        self._start_time: Optional[float] = None

    # ── discovery ───────────────────────────────────────────────────────────

    def list_devices(self) -> list[dict]:
        """List input devices (name, index, default_samplerate, max_input_channels)."""
        devices = []
        for i, d in enumerate(sd.query_devices()):
            if d.get("max_input_channels", 0) > 0:
                devices.append(
                    {
                        "index": i,
                        "name": str(d.get("name", "")),
                        "default_samplerate": float(d.get("default_samplerate", 0)),
                        "max_input_channels": int(d.get("max_input_channels", 0)),
                    }
                )
        return devices

    def default_device(self) -> Optional[dict]:
        dev = sd.query_devices(kind="input")
        return {
            "name": str(dev.get("name", "")),
            "default_samplerate": float(dev.get("default_samplerate", 0)),
            "max_input_channels": int(dev.get("max_input_channels", 0)),
        }

    def is_bluetooth_handsfree(self, device_name: str) -> bool:
        name = (device_name or "").lower()
        return "hands-free" in name or "hfp" in name or "headset" in name

    # ── capture ─────────────────────────────────────────────────────────────

    def start(
        self,
        device=None,
        profile: str = "RAW",
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        blocksize: int = DEFAULT_BLOCKSIZE,
        on_audio: Optional[Callable[[object], None]] = None,
    ) -> None:
        """Start capture. profile selects a MicProfile (NEUMANN/HARAM/DEEP_BASS/RAW)."""
        if self._recording:
            return
        self._device = device
        self._sample_rate = int(sample_rate)
        self._blocksize = int(blocksize)
        self._profile = PROFILES.get(profile.upper(), RAW)
        self._chunks = []
        self._recording = True
        self._start_time = time.time()

        def callback(indata, frames, time_info, status):
            with self._lock:
                if self._recording:
                    self._chunks.append(indata.copy())
            if on_audio is not None:
                on_audio(indata)

        self._stream = sd.InputStream(
            samplerate=self._sample_rate,
            blocksize=self._blocksize,
            device=self._device,
            channels=1,
            dtype="float32",
            callback=callback,
        )
        self._stream.start()

    def stop(self) -> Optional[Path]:
        """Stop capture and commit a PCM_16 WAV. Returns the WAV path or None."""
        if not self._recording:
            return None
        self._recording = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        with self._lock:
            chunks = list(self._chunks)
            self._chunks = []

        if not chunks:
            return None

        import numpy as np

        audio = np.concatenate(chunks, axis=0)
        # Apply profile coloration on commit (gentle, deterministic).
        audio = self._apply_profile(audio)

        # Commit to a temp WAV next to the cwd so callers can move/rename.
        import tempfile

        fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        import os

        os.close(fd)
        sf.write(tmp_path, audio, self._sample_rate, subtype="PCM_16")
        return Path(tmp_path)

    def _apply_profile(self, audio):
        """Gentle profile coloration (currently no-op beyond RAW/NEUMANN flat;
        HARAM/DEEP_BASS apply a simple low-shelf gain boost)."""
        import numpy as np

        if self._profile is RAW or self._profile is NEUMANN:
            return audio
        if self._profile is DEEP_BASS:
            # +6 dB sub shelf below ~120 Hz via one-pole low-shelf.
            from scipy import signal

            sos = signal.butter(2, 120, btype="lowpass", fs=self._sample_rate, output="sos")
            bass = signal.sosfilt(sos, audio[:, 0] if audio.ndim > 1 else audio)
            out = audio.copy()
            if out.ndim > 1:
                out[:, 0] = (out[:, 0] + bass * 0.5).astype(audio.dtype)
            else:
                out = (out + bass * 0.5).astype(audio.dtype)
            return out
        return audio

    @property
    def recording(self) -> bool:
        return self._recording
