"""Noor Cinematic Studio engine — native OpenMontage extension (lib/noor).

Pure engines shared by BaseTool plugins and the noor_studio workstation.
No external AI calls here; fully local and deterministic.

mushaf_store and storage are imported lazily (below) so this package
imports cleanly before Tasks A.4/A.5 create those modules.
"""

from __future__ import annotations

from .schemas import (
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
    DSPConfig,
    DSPAnalysis,
    Preset,
    NoorProject,
    VerseRef,
)

__all__ = [
    "LUTStyle",
    "MosqueAcousticSpace",
    "CapCutNoiseMode",
    "CapCutDeepBassMode",
    "MobileMicCalibrationMode",
    "QuranTypographyStyle",
    "WaveformStyle",
    "AspectRatio",
    "SplitMode",
    "SpiritualAtmosphere",
    "OfficialStudioPresets",
    "DSPConfig",
    "DSPAnalysis",
    "Preset",
    "NoorProject",
    "VerseRef",
]


def _import_mushaf_store():
    from .mushaf_store import MushafStore

    return MushafStore


def _import_storage():
    from .storage import NoorStore

    return NoorStore
