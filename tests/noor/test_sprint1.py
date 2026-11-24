"""Sprint 1 foundations — TDD RED tests.

These tests are written BEFORE the production modules they import
(lib/noor/schemas.py, lib/noor/mushaf_store.py, lib/noor/storage.py).
They are expected to FAIL (not skip) with ImportError/AttributeError
until the matching modules are implemented in Tasks A.3–A.5.

Exact enum member values and spec constants are pinned from the plan's
Interfaces blocks — they are the contract later tasks implement to.
"""

from __future__ import annotations

import asyncio
import math
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Fail loudly if OpenMontage root isn't importable.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── Test 1: enum member values match the spec verbatim ──────────────────────

def test_enums_match_spec():
    """All 11 enums construct with the exact spec-pinned member values."""
    from lib.noor.schemas import (  # noqa: F401
        LUTStyle,
        MosqueAcousticSpace,
        CapCutNoiseMode,
        CapCutDeepBassMode,
        MobileMicCalibrationMode,
        QuranTypographyStyle,
        WaveformStyle,
        AspectRatio,
        SplitMode,
        SpiritualAtmosphere,
        OfficialStudioPresets,
    )

    assert LUTStyle("kadyrov_gold").value == "kadyrov_gold"
    assert LUTStyle("royal_dark").value == "royal_dark"
    assert LUTStyle("makkah_sunrise").value == "makkah_sunrise"
    assert LUTStyle("madina_emerald").value == "madina_emerald"
    assert LUTStyle("dawn_spiritual").value == "dawn_spiritual"
    assert LUTStyle("vintage_film").value == "vintage_film"
    assert LUTStyle("pure_mushaf").value == "pure_mushaf"
    assert LUTStyle("dramatic_monochrome").value == "dramatic_monochrome"

    assert MosqueAcousticSpace("haram_makkah").value == "haram_makkah"
    assert MosqueAcousticSpace("prophet_madina").value == "prophet_madina"
    assert MosqueAcousticSpace("alaqsa").value == "alaqsa"
    assert MosqueAcousticSpace("pro_studio").value == "pro_studio"
    assert MosqueAcousticSpace("dome_hall").value == "dome_hall"

    assert CapCutNoiseMode("off").value == "off"
    assert CapCutNoiseMode("standard").value == "standard"
    assert CapCutNoiseMode("pro_clean").value == "pro_clean"
    assert CapCutNoiseMode("extreme").value == "extreme"

    assert CapCutDeepBassMode("off").value == "off"
    assert CapCutDeepBassMode("warm").value == "warm"
    assert CapCutDeepBassMode("capcut_pro").value == "capcut_pro"
    assert CapCutDeepBassMode("kadyrov_elite").value == "kadyrov_elite"

    assert MobileMicCalibrationMode("studio_neumann").value == "studio_neumann"
    assert MobileMicCalibrationMode("broadcast_shure").value == "broadcast_shure"
    assert MobileMicCalibrationMode("smooth_warm").value == "smooth_warm"
    assert MobileMicCalibrationMode("raw_calibrated").value == "raw_calibrated"

    assert QuranTypographyStyle("uthmani_gold").value == "uthmani_gold"
    assert QuranTypographyStyle("pure_white").value == "pure_white"
    assert QuranTypographyStyle("royal_emerald").value == "royal_emerald"
    assert QuranTypographyStyle("amber_glow").value == "amber_glow"

    assert WaveformStyle("solid").value == "solid"
    assert WaveformStyle("glass_modern").value == "glass_modern"
    assert WaveformStyle("glass_bars").value == "glass_bars"
    assert WaveformStyle("vintage_dots").value == "vintage_dots"

    assert AspectRatio("9:16").value == "9:16"
    assert AspectRatio("1:1").value == "1:1"
    assert AspectRatio("16:9").value == "16:9"
    assert AspectRatio("4:5").value == "4:5"

    assert SplitMode("split").value == "split"
    assert SplitMode("filtered").value == "filtered"
    assert SplitMode("original").value == "original"
    assert SplitMode("side-by-side").value == "side-by-side"

    assert SpiritualAtmosphere("sakina_dawn").value == "sakina_dawn"
    assert SpiritualAtmosphere("jalal_majesty").value == "jalal_majesty"
    assert SpiritualAtmosphere("rajaa_hope").value == "rajaa_hope"
    assert SpiritualAtmosphere("tahajjud_solitude").value == "tahajjud_solitude"

    assert OfficialStudioPresets("kadyrov_master").value == "kadyrov_master"
    assert OfficialStudioPresets("capcut_pro_elite").value == "capcut_pro_elite"
    assert OfficialStudioPresets("kadyrov_elite_bass").value == "kadyrov_elite_bass"
    assert OfficialStudioPresets("podcast_serat_sawy").value == "podcast_serat_sawy"
    assert OfficialStudioPresets("viral_islam_sobhi").value == "viral_islam_sobhi"
    assert OfficialStudioPresets("viral_hazza_albalushi").value == "viral_hazza_albalushi"
    assert OfficialStudioPresets("grand_mosque_haram").value == "grand_mosque_haram"
    assert OfficialStudioPresets("pro_studio_master").value == "pro_studio_master"


# ── Test 2: DSPConfig rejects NaN / Inf / out-of-range ──────────────────────

def test_dsp_config_rejects_nan_inf_and_out_of_range():
    """DSPConfig Pydantic model guards every numeric param."""
    from pydantic import ValidationError

    from lib.noor.schemas import DSPConfig

    # Valid construction is accepted.
    cfg = DSPConfig(
        preamp_gain=2.0,
        eq_band_1_gain_db=6.0,
        eq_band_2_gain_db=-3.0,
        eq_band_3_gain_db=0.0,
        eq_band_4_gain_db=0.0,
        eq_band_5_gain_db=0.0,
        eq_band_6_gain_db=0.0,
        lut_intensity=75,
        deep_bass_mix=0.5,
    )
    assert cfg.preamp_gain == 2.0
    assert cfg.eq_band_1_gain_db == 6.0

    # NaN rejected by math.isfinite guard.
    with pytest.raises(ValidationError):
        DSPConfig(preamp_gain=float("nan"))

    # Inf rejected by math.isfinite guard.
    with pytest.raises(ValidationError):
        DSPConfig(preamp_gain=float("inf"))

    # Out-of-range EQ band (±12 dB) rejected.
    with pytest.raises(ValidationError):
        DSPConfig(eq_band_1_gain_db=20.0)

    # Out-of-range LUT intensity (0–100) rejected.
    with pytest.raises(ValidationError):
        DSPConfig(lut_intensity=150)

    # Negative deep-bass mix rejected.
    with pytest.raises(ValidationError):
        DSPConfig(deep_bass_mix=-0.1)


# ── Test 3: MushafStore rejects unverified verses ───────────────────────────

def test_mushaf_verify_rejects_unverified_verse():
    """Sacred-text integrity: canonical verses resolve; invented text returns None."""
    from lib.noor.mushaf_store import MushafStore
    from lib.noor.schemas import VerseRef

    store = MushafStore()
    # Canonical al-Fatihah opening (Uthmani) resolves to surah 1, ayah 1.
    ref = store.verify("بِسْمِ ٱللَّٰهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ")
    assert isinstance(ref, VerseRef)
    assert ref.surah_id == 1
    assert ref.ayah_id == 1

    # Invented text is never emitted as an Ayah.
    assert store.verify("this is not a real Quranic verse") is None
    assert store.verify("بِسْمِ λ렴 란") is None

    # Out-of-range ayah returns None (surah 2 has 286 ayahs; 287 is beyond).
    assert store.lookup(2, 287) is None


# ── Test 4: NoorStore preset CRUD + XP (+150 per export) ────────────────────

def test_noor_store_preset_crud_and_xp():
    """NoorStore async SQLite WAL: preset CRUD, .noorpreset round-trip, XP."""
    from lib.noor.storage import NoorStore, Preset


    fd, path = tempfile.mkstemp(suffix=".noor.db")
    os.close(fd)
    try:
        store = NoorStore(db_path=path)
        asyncio.run(store.init())

        # Seeded official presets present.
        presets = asyncio.run(store.list_presets())
        seeded = {p["name"] for p in presets}
        for name in [
            "kadyrov_master",
            "capcut_pro_elite",
            "kadyrov_elite_bass",
            "podcast_serat_sawy",
            "viral_islam_sobhi",
            "viral_hazza_albalushi",
            "grand_mosque_haram",
            "pro_studio_master",
        ]:
            assert name in seeded, f"seeded preset missing: {name}"

        # Custom preset save/get round-trip.
        custom = Preset(
            name="my_qa preset",
            dsp_config={"preamp_gain": 1.5, "eq_band_1_gain_db": 4.0},
            lut_style="makkah_sunrise",
        )
        asyncio.run(store.save_preset(custom))
        got = asyncio.run(store.get_preset("my_qa preset"))
        assert got is not None
        assert got.name == "my_qa preset"
        assert got.dsp_config["preamp_gain"] == 1.5

        # .noorpreset export / import round-trip.
        exported = asyncio.run(store.export_preset("my_qa preset"))
        assert exported is not None
        imported = asyncio.run(store.import_preset(exported))
        assert imported is not None
        assert imported.name == "my_qa preset"

        # record_export adds +150 XP per export.
        before = asyncio.run(store.get_mastery("audio_master"))
        asyncio.run(store.record_export("audio_master", 120.0))
        after = asyncio.run(store.get_mastery("audio_master"))
        assert after.xp == before.xp + 150
        assert after.exports_count == before.exports_count + 1
    finally:
        asyncio.run(store.close())
        Path(path).unlink(missing_ok=True)


# ── Non-import-gated smoke test: suite runs even when modules missing ──────

def test_sprint1_suite_is_runnable():
    """This file itself is valid pytest; RED failures are import errors, not typos."""
    assert True
