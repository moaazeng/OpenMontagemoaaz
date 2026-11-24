"""Noor Canonical Data Contracts (Pydantic v2 / JSON).

Strict data contracts for the Noor Cinematic Studio integration. Every
numeric DSP parameter is guarded with math.isfinite() so NaN/Inf can
never leak into JSON payloads or the DSP chain. Enum member values are
pinned verbatim from the spec (my_new_architicture.md / plan Interfaces
blocks).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ── Enums (member values pinned verbatim from the spec) ─────────────────────


class LUTStyle(str, Enum):
    kadyrov_gold = "kadyrov_gold"
    royal_dark = "royal_dark"
    makkah_sunrise = "makkah_sunrise"
    madina_emerald = "madina_emerald"
    dawn_spiritual = "dawn_spiritual"
    vintage_film = "vintage_film"
    pure_mushaf = "pure_mushaf"
    dramatic_monochrome = "dramatic_monochrome"


class MosqueAcousticSpace(str, Enum):
    haram_makkah = "haram_makkah"   # ~8.5 s reverb
    prophet_madina = "prophet_madina"  # ~5.2 s
    alaqsa = "alaqsa"             # ~6.0 s
    pro_studio = "pro_studio"     # dry
    dome_hall = "dome_hall"       # ~9.0 s


class CapCutNoiseMode(str, Enum):
    off = "off"
    standard = "standard"
    pro_clean = "pro_clean"
    extreme = "extreme"


class CapCutDeepBassMode(str, Enum):
    off = "off"
    warm = "warm"
    capcut_pro = "capcut_pro"
    kadyrov_elite = "kadyrov_elite"


class MobileMicCalibrationMode(str, Enum):
    studio_neumann = "studio_neumann"
    broadcast_shure = "broadcast_shure"
    smooth_warm = "smooth_warm"
    raw_calibrated = "raw_calibrated"


class QuranTypographyStyle(str, Enum):
    uthmani_gold = "uthmani_gold"
    pure_white = "pure_white"
    royal_emerald = "royal_emerald"
    amber_glow = "amber_glow"


class WaveformStyle(str, Enum):
    solid = "solid"
    glass_modern = "glass_modern"
    glass_bars = "glass_bars"
    vintage_dots = "vintage_dots"


class AspectRatio(str, Enum):
    r_9_16 = "9:16"
    r_1_1 = "1:1"
    r_16_9 = "16:9"
    r_4_5 = "4:5"


class SplitMode(str, Enum):
    split = "split"
    filtered = "filtered"
    original = "original"
    side_by_side = "side-by-side"


class SpiritualAtmosphere(str, Enum):
    sakina_dawn = "sakina_dawn"
    jalal_majesty = "jalal_majesty"
    rajaa_hope = "rajaa_hope"
    tahajjud_solitude = "tahajjud_solitude"


class OfficialStudioPresets(str, Enum):
    kadyrov_master = "kadyrov_master"
    capcut_pro_elite = "capcut_pro_elite"
    kadyrov_elite_bass = "kadyrov_elite_bass"
    podcast_serat_sawy = "podcast_serat_sawy"
    viral_islam_sobhi = "viral_islam_sobhi"
    viral_hazza_albalushi = "viral_hazza_albalushi"
    grand_mosque_haram = "grand_mosque_haram"
    pro_studio_master = "pro_studio_master"


# ── Pydantic models ─────────────────────────────────────────────────────────


class DSPConfig(BaseModel):
    """Golden Order DSP configuration — FR-04 parameters, all bounded."""

    preamp_gain: float = Field(default=1.0, ge=0.5, le=4.0)
    eq_band_1_gain_db: float = Field(default=0.0, ge=-12.0, le=12.0)
    eq_band_2_gain_db: float = Field(default=0.0, ge=-12.0, le=12.0)
    eq_band_3_gain_db: float = Field(default=0.0, ge=-12.0, le=12.0)
    eq_band_4_gain_db: float = Field(default=0.0, ge=-12.0, le=12.0)
    eq_band_5_gain_db: float = Field(default=0.0, ge=-12.0, le=12.0)
    eq_band_6_gain_db: float = Field(default=0.0, ge=-12.0, le=12.0)
    lut_intensity: int = Field(default=75, ge=0, le=100)
    deep_bass_mix: float = Field(default=0.5, ge=0.0, le=1.0)
    capcut_noise_mode: CapCutNoiseMode = CapCutNoiseMode.standard
    capcut_deep_bass_mode: CapCutDeepBassMode = CapCutDeepBassMode.off
    mobile_mic_calibration: MobileMicCalibrationMode = MobileMicCalibrationMode.studio_neumann
    mosque_acoustic_space: MosqueAcousticSpace = MosqueAcousticSpace.haram_makkah
    lut_style: LUTStyle = LUTStyle.kadyrov_gold

    @field_validator(
        "preamp_gain",
        "eq_band_1_gain_db",
        "eq_band_2_gain_db",
        "eq_band_3_gain_db",
        "eq_band_4_gain_db",
        "eq_band_5_gain_db",
        "eq_band_6_gain_db",
        "deep_bass_mix",
        mode="before",
    )
    @classmethod
    def _require_finite(cls, v: Any) -> Any:
        """Reject NaN/Inf before range validation."""
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError(f"must be finite, got {v!r}")
        return v

    @field_validator("lut_intensity", mode="before")
    @classmethod
    def _lut_intensity_finite(cls, v: Any) -> Any:
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError(f"must be finite, got {v!r}")
        return v


@dataclass(frozen=True)
class VerseRef:
    """Canonical Mushaf verse reference — only verified verses produce one."""
    surah_id: int
    ayah_id: int
    uthmani_text: str
    translation: Optional[str] = None


def _reject_non_finite(v: Any) -> Any:
    """Reject NaN/Inf (and any container holding them) so JSON can never emit null."""
    if isinstance(v, float):
        if not math.isfinite(v):
            raise ValueError(f"must be finite, got {v!r}")
        return v
    if isinstance(v, dict):
        for kk, vv in v.items():
            _reject_non_finite(vv)
        return v
    if isinstance(v, (list, tuple)):
        for item in v:
            _reject_non_finite(item)
        return v
    return v


class DSPAnalysis(BaseModel):
    """Momentary analysis output of the Golden Order DSP chain."""

    lufs_momentary: float
    lufs_integrated: float
    true_peak_db_tp: float
    clarity_ratio: float
    fft_bins: list[float]
    sample_rate: int = 48000

    @field_validator(
        "lufs_momentary",
        "lufs_integrated",
        "true_peak_db_tp",
        "clarity_ratio",
        mode="before",
    )
    @classmethod
    def _require_finite_scalar(cls, v: Any) -> Any:
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError(f"must be finite, got {v!r}")
        return v

    @field_validator("fft_bins", mode="before")
    @classmethod
    def _require_finite_bins(cls, v: Any) -> Any:
        if isinstance(v, list):
            for item in v:
                if isinstance(item, float) and not math.isfinite(item):
                    raise ValueError(f"fft_bins must be finite, got {v!r}")
        return v


class Preset(BaseModel):
    """A user-storable DSP preset (.noorpreset round-trippable)."""

    name: str = Field(min_length=1, max_length=100)
    dsp_config: dict[str, Any] = Field(default_factory=dict)
    lut_style: str = LUTStyle.kadyrov_gold.value
    aspect_ratio: str = AspectRatio.r_9_16.value

    @field_validator("dsp_config", mode="before")
    @classmethod
    def _dsp_config_no_nan(cls, v: Any) -> Any:
        _reject_non_finite(v)
        return v


class NoorProject(BaseModel):
    """A Noor project file (.noorproj)."""

    name: str = Field(min_length=1)
    version: str = "1.0"
    dsp_config: DSPConfig = Field(default_factory=DSPConfig)
    preset: Optional[Preset] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("metadata", mode="before")
    @classmethod
    def _metadata_no_nan(cls, v: Any) -> Any:
        _reject_non_finite(v)
        return v
