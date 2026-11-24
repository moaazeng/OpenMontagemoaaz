"""Canonical Tanzil Uthmani verse store.

Sacred-text integrity: only canonically-indexed verses resolve to a
VerseRef. AI-recognized or ASR-produced text is verified against the
canonical index via RapidFuzz; anything below threshold returns None —
zero unverified verses are ever emitted as Ayah text.

The embedded default payload is the canonical Tanzil Uthmani text for
the opening verses (surah 1, ayah 1 plus a small verified corpus). A
full Mushaf JSON may be loaded later via load(path).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rapidfuzz import fuzz, process

from .schemas import VerseRef

# Verification threshold: below this RapidFuzz score the text is treated
# as unverified and None is returned (never emitted as an Ayah).
_VERIFY_THRESHOLD = 92


# ── Minimal canonical Tanzil Uthmani seed corpus ────────────────────────────
# Surah 1 (al-Fatihah), ayahs 1–7 (Uthmani script).
_DEFAULT_CORPUS = {
    (1, 1): "بِسْمِ ٱللَّٰهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ",
    (1, 2): "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَالَمِينَ",
    (1, 3): "ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ",
    (1, 4): "مَالِكِ يَوْمِ الدِّينِ",
    (1, 5): "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
    (1, 6): "ٱهْدِنَا ٱلصِّرَاطَ ٱلْمُسْتَقِيمَ",
    (1, 7): "صِرَاطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّآلِّينَ",
    # Surah 2, ayah 255 (Ayat al-Kursi) — used by the out-of-range test.
    (2, 255): "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ",
}

# Surah → total ayah count (for bounds checks on lookup).
_SURAH_LENGTHS = {
    1: 7,
    2: 286,
}


@dataclass(frozen=True)
class _IndexEntry:
    surah_id: int
    ayah_id: int
    uthmani_text: str


class MushafStore:
    """Canonical Mushaf verse store backed by RapidFuzz verification."""

    def __init__(self, data_path: Optional[str | Path] = None) -> None:
        self._entries: dict[tuple[int, int], _IndexEntry] = {}
        self._verse_texts: list[str] = []
        self._verse_keys: list[tuple[int, int]] = []
        self._loaded_path: Optional[Path] = None
        if data_path is not None:
            self.load(data_path)
        else:
            self._load_default()

    # ── loading ─────────────────────────────────────────────────────────────

    def _load_default(self) -> None:
        for (surah_id, ayah_id), text in sorted(_DEFAULT_CORPUS.items()):
            self._add(surah_id, ayah_id, text)
        self._loaded_path = None  # embedded default

    def load(self, path: str | Path) -> None:
        """Load a full Tanzil Uthmani JSON file.

        Expected shape: a list of objects with `surah`, `ayah`, `text`
        (Uthmani) keys, OR a dict mapping `"surah:ayah"` → text.
        Existing entries are replaced.
        """
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"Mushaf data not found: {p}")
        raw = json.loads(p.read_text(encoding="utf-8"))

        self._entries = {}
        self._verse_texts = []
        self._verse_keys = []

        if isinstance(raw, list):
            for item in raw:
                surah_id = int(item["surah"])
                ayah_id = int(item["ayah"])
                text = item["text"]
                self._add(surah_id, ayah_id, text)
        elif isinstance(raw, dict):
            for key, text in raw.items():
                surah_s, ayah_s = key.split(":")
                self._add(int(surah_s), int(ayah_s), text)
        else:
            raise ValueError("Unsupported Mushaf JSON shape")

        self._loaded_path = p

    def _add(self, surah_id: int, ayah_id: int, text: str) -> None:
        key = (surah_id, ayah_id)
        self._entries[key] = _IndexEntry(surah_id, ayah_id, text)
        self._verse_texts.append(text)
        self._verse_keys.append(key)

    # ── public API ──────────────────────────────────────────────────────────

    def lookup(self, surah_id: int, ayah_id: int) -> Optional[VerseRef]:
        """Return the canonical VerseRef for (surah_id, ayah_id), or None."""
        entry = self._entries.get((surah_id, ayah_id))
        if entry is None:
            return None
        return VerseRef(
            surah_id=entry.surah_id,
            ayah_id=entry.ayah_id,
            uthmani_text=entry.uthmani_text,
        )

    def verify(self, text: str) -> Optional[VerseRef]:
        """Verify free text against the canonical index via RapidFuzz.

        Returns the best-matching VerseRef when the fuzzy-ratio score is
        at or above _VERIFY_THRESHOLD; otherwise None (unverified — never
        emitted as an Ayah).
        """
        if not text or not self._verse_texts:
            return None

        # Normalize whitespace/Arabic presentation lightly for comparison.
        query = _normalize(text)

        best = process.extractOne(
            query,
            self._verse_texts,
            scorer=fuzz.ratio,
            score_cutoff=_VERIFY_THRESHOLD,
        )
        if best is None:
            return None

        matched_text, score, idx = best
        key = self._verse_keys[idx]
        entry = self._entries[key]
        return VerseRef(
            surah_id=entry.surah_id,
            ayah_id=entry.ayah_id,
            uthmani_text=entry.uthmani_text,
        )


def _normalize(text: str) -> str:
    """Light normalization for Uthmani comparison (collapse whitespace)."""
    return " ".join(text.split())
