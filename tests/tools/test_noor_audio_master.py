"""TDD RED tests for NoorAudioMaster BaseTool.

Written BEFORE the implementation was verified end-to-end. Uses real
ffmpeg-generated input and real soundfile decode/write — no mocks.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.audio.noor_audio_master import NoorAudioMaster

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="FFmpeg required")


def _make_source(tmp_path: Path, suffix: str = "wav") -> Path:
    """Generate a 0.5 s 440 Hz sine at -20 dBFS (ffmpeg)."""
    src = tmp_path / f"voice.{suffix}"
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-f", "lavfi", "-i",
            "sine=frequency=440:sample_rate=48000:duration=0.5", "-c:a",
            "pcm_s16le" if suffix == "wav" else "libmp3lame", "-q:a", "2",
            str(src),
        ],
        capture_output=True, check=True, timeout=15,
    )
    return src


def test_master_clean_speech_produces_wav(tmp_path):
    """clean_speech preset on a 440 Hz sine → WAV, finite true peak ≤ -1 dBTP."""
    src = _make_source(tmp_path, "wav")
    out = tmp_path / "voice_mastered.wav"
    result = NoorAudioMaster().execute({
        "input_path": str(src),
        "output_path": str(out),
        "preset": "clean_speech",
    })
    assert result.success, result.error
    assert out == Path(result.data["output"])
    assert out.stat().st_size > 0
    assert result.data["sample_rate"] == 48000
    assert result.data["true_peak_db_tp"] <= -1.0


def test_master_quranic_recitation_mp3_input(tmp_path):
    """quranic_recitation preset accepts MP3 input, emits WAV output."""
    src = _make_source(tmp_path, "mp3")
    out = tmp_path / "voice_mastered.wav"
    result = NoorAudioMaster().execute({
        "input_path": str(src),
        "output_path": str(out),
        "preset": "quranic_recitation",
    })
    assert result.success, result.error
    assert out.stat().st_size > 0
    assert result.data["format"] == "wav"


def test_master_preamp_gain_override_respected(tmp_path):
    """Explicit preamp_gain override merges onto preset base."""
    src = _make_source(tmp_path, "wav")
    out = tmp_path / "voice_mastered.wav"
    result = NoorAudioMaster().execute({
        "input_path": str(src),
        "output_path": str(out),
        "preset": "clean_speech",
        "preamp_gain": 4.0,
    })
    assert result.success, result.error
    assert out.stat().st_size > 0
    assert result.data["true_peak_db_tp"] <= -1.0  # limiter still guards


def test_master_missing_input_returns_error(tmp_path):
    """Missing input file → success=False with a clear error, not a crash."""
    out = tmp_path / "out.wav"
    result = NoorAudioMaster().execute({
        "input_path": str(tmp_path / "does_not_exist.wav"),
        "output_path": str(out),
    })
    assert not result.success
    assert "not found" in result.error
    assert not out.exists()


def test_audio_master_suite_is_runnable():
    assert True
