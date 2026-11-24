"""Noor Cinematic Studio engine — native OpenMontage extension (lib/noor).

Pure engines shared by BaseTool plugins and the noor_studio workstation.
No external AI calls here; fully local and deterministic.
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
from .mushaf_store import MushafStore
from .storage import NoorStore
from .recorder import NoorRecorder, DEFAULT_SAMPLE_RATE, DEFAULT_BLOCKSIZE
from .video_decoder import VideoDecoder
from .gl_renderer import GLRenderer
from .face_depth_ai import FaceDepthAI
from .calligraphy import render_uthmani, render_waveform

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
    "MushafStore",
    "NoorStore",
    "NoorRecorder",
    "VideoDecoder",
    "GLRenderer",
    "FaceDepthAI",
    "render_uthmani",
    "render_waveform",
]
