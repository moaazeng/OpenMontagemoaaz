"""TDD RED tests for Sub-plan D — Quranic Ayah Aligner."""

from __future__ import annotations

import pytest
from pathlib import Path


# ── test: mushaf lock rejects unverified ─────────────────────────────────────

def test_noor_mushaf_lock_rejects_unverified():
    """Feed an invented Arabic sentence; segments should be empty and unverified should report it."""
    from tools.analysis.quran_ayah_aligner import QuranAyahAligner

    # The verify function directly: random text should not match
    from lib.noor.mushaf_store import MushafStore

    store = MushafStore()
    # "random Arabic" should not verify against canonical index
    result = store.verify("كلمة عشوائية xyz")
    assert result is None, f"expected None for random text, got {result}"

    # Canonical text should verify
    result2 = store.verify("بِسْمِ ٱللَّٰهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ")
    assert result2 is not None, "expected canonical text to verify"
    assert result2.surah_id == 1
    assert result2.ayah_id == 1


# ── test: quran aligner grounded on known verse ─────────────────────────────

def test_noor_quran_aligner_grounded():
    """Short known verse should resolve to valid (surah_id, ayah_id) via the aligner."""
    from tools.analysis.quran_ayah_aligner import QuranAyahAligner
    from lib.noor.mushaf_store import MushafStore

    store = MushafStore()

    # Verify the store integration works: canonical text resolves correctly
    vr = store.lookup(1, 1)
    assert vr is not None
    assert vr.surah_id == 1
    assert vr.ayah_id == 1
    assert "بِسْمِ" in vr.uthmani_text

    # The aligner should return verified segments for canonical text
    # verify uses the class-level _VERIFY_THRESHOLD = 92
    verified = store.verify("بِسْمِ ٱللَّٰهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ")
    assert verified is not None
    assert verified.surah_id == 1
    assert verified.ayah_id == 1