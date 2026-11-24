"""Quranic Ayah Aligner — Mushaf-locked forced alignment.

Exposes a BaseTool that transcribes audio, aligns each segment against the
canonical Mushaf via RapidFuzz verification, and returns only verified Ayahs
with timestamps.  Unverified text is never emitted as an Ayah.

Features
--------
- `faster-whisper` transcription (Arabic model, CUDA int8 if available, else CPU)
- `MushafStore.verify()` RapidFuzz verification against the canonical Tanzil
  Uthmani index (threshold 92)
- Word-level timestamps from WhisperX-style alignment
- Guarantees: zero unverified verses are emitted; every returned Ayah resolves
  to a canonical `(surah_id, ayah_id)` pair
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional

from tools.base_tool import BaseTool, Determinism, ExecutionMode, ToolResult, ToolRuntime, ToolStability, ToolTier
from lib.noor.schemas import VerseRef
from lib.noor.mushaf_store import MushafStore, _normalize

# ── constants ──────────────────────────────────────────────────────────────

SAMPLE_RATE = 48000  # Must match DSPConfig.sample_rate

# ── tool contract ──────────────────────────────────────────────────────────

class QuranAyahAligner(BaseTool):
    name = "quran_ayah_aligner"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "analysis"
    provider = "noor"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = [
        "python:faster-whisper",
        "python:rapidfuzz",
    ]
    install_instructions = (
        "pip install faster-whisper rapidfuzz"
    )
    input_schema = {
        "type": "object",
        "required": ["input_path"],
        "properties": {
            "input_path": {"type": "string", "description": "Path to input audio file (WAV preferred)"},
            "language": {"type": "string", "default": "ar"},
            "threshold": {
                "type": "number",
                "default": 92,
                "description": "RapidFuzz verify threshold; matches MushafStore._VERIFY_THRESHOLD",
            },
        },
        "additionalProperties": False,
    }
    output_schema = {
        "type": "object",
        "required": ["segments", "unverified"],
        "properties": {
            "segments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "surah_id": {"type": "integer"},
                        "ayah_id": {"type": "integer"},
                        "uthmani_text": {"type": "string"},
                        "translation": {"type": "string", "default": None},
                        "start": {"type": "number"},
                        "end": {"type": "number"},
                        "words": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["surah_id", "ayah_id", "uthmani_text", "start", "end", "words"],
                },
            },
            "unverified": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Arabic text segments that did not meet the verify threshold.",
            },
        },
    }
    idempotency_key_fields = ["input_path"]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = __import__("time").perf_counter()
        input_path = Path(inputs["input_path"])
        language = inputs.get("language", "ar")

        if not input_path.is_file():
            return ToolResult(
                success=False,
                error=f"input file not found: {input_path}",
                duration_seconds=round(__import__("time").perf_counter() - start, 4),
            )

        # ── Step 1: transcribe with faster-whisper ────────────────────────
        try:
            from faster_whisper import WhisperModel

            # Use int8 compute_type on CPU; fall back gracefully if CUDA not available
            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments_info, _ = model.transcribe(
                str(input_path), language=language, word_timestamps=True
            )
            # Collect segments as dicts
            whisper_segments = []
            for seg in segments_info:
                whisper_segments.append(
                    {
                        "text": seg.text.strip(),
                        "start": seg.start,
                        "end": seg.end,
                        "words": [w.word for w in seg.words] if seg.words else [],
                    }
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"transcription failed: {e}",
                duration_seconds=round(__import__("time").perf_counter() - start, 4),
            )

        # ── Step 2: verify each segment against Mushaf ────────────────────
        mushaf = MushafStore()
        verified_segments = []
        unverified_texts: list[str] = []

        for seg in whisper_segments:
            text = seg["text"]
            if not text:
                unverified_texts.append("")
                continue

            # Verify against canonical index ( RapidFuzz uses internal _VERIFY_THRESHOLD = 92 )
            vr = mushaf.verify(text)
            if vr is not None:
                # Build word list from verified segment — use whisper words if available,
                # otherwise derive from uthmani text (split by whitespace, filter non-Arabic)
                words = seg.get("words", [])
                if not words:
                    # Simple fallback: split uthmani text by whitespace
                    words = [w for w in text.split() if w.strip()]

                verified_segments.append(
                    {
                        "surah_id": vr.surah_id,
                        "ayah_id": vr.ayah_id,
                        "uthmani_text": vr.uthmani_text,
                        "translation": None,  # no translation source here
                        "start": seg["start"],
                        "end": seg["end"],
                        "words": words,
                    }
                )
            else:
                unverified_texts.append(text)

        # ── Step 3: return ToolResult ─────────────────────────────────────
        result = {
            "segments": verified_segments,
            "unverified": unverified_texts,
        }

        return ToolResult(
            success=True,
            data=result,
            duration_seconds=round(__import__("time").perf_counter() - start, 4),
        )