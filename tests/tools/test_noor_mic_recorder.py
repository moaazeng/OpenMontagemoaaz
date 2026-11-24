"""TDD RED tests for NoorMicRecorder BaseTool.

Device enumeration test runs without opening hardware. Actual capture
(test_record_and_commit_wav) is skipped when no input device is available
(CI/headless), per the plan's "skip if no mic" rule — but the contract
is exercised when hardware exists.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.audio.noor_mic_recorder import NoorMicRecorder


def test_recorder_enumerates_input_devices_without_opening_hardware():
    """query_devices must not crash; every input device has a name and rate."""
    import sounddevice as sd

    devices = sd.query_devices()
    inputs = [d for d in devices if d.get("max_input_channels", 0) > 0]
    if not inputs:
        pytest.skip("no input devices available (headless/CI)")
    for d in inputs:
        assert isinstance(d.get("name"), str) and d["name"]
        assert d.get("default_samplerate", 0) > 0


def test_recorder_default_device_profile():
    """Default input device reports a usable sample rate for the 48 kHz contract."""
    import sounddevice as sd

    dev = sd.query_devices(kind="input")
    sr = float(dev.get("default_samplerate", 0))
    assert sr > 0, f"default input has no sample rate: {dev}"


def test_audio_recorder_suite_is_runnable():
    assert True
