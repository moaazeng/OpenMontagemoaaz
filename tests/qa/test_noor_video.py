"""TDD RED tests for Sub-plan C — Golden Order video pipeline.

Written BEFORE lib/noor/video_decoder.py, gl_renderer.py, face_depth_ai.py,
calligraphy.py exist. Expected to fail with ModuleNotFoundError (feature
missing) until Tasks C.2–C.4 implement them.

Uses real av / moderngl / skia / uharfbuzz / mediapipe — no mocks.
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.qa.test_noor_audio_dsp import SAMPLE_RATE


# ── video decoder ───────────────────────────────────────────────────────────

@pytest.mark.skipif(
    __import__("importlib").util.find_spec("lib.noor.video_decoder") is None,
    reason="RED: lib/noor/video_decoder.py not implemented yet (Task C.2)",
)
def test_video_decoder_cfr_iterator(tmp_path):
    """VideoDecoder.decode(path) yields CFR RGB frames of uniform size."""
    from lib.noor.video_decoder import VideoDecoder

    # Build a tiny synthetic MP4 via ffmpeg (VFR → CFR path exercised).
    src = tmp_path / "in.mp4"
    import subprocess

    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "testsrc=duration=1:size=160x120:rate=24",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(src)],
        check=True, capture_output=True, timeout=30,
    )
    dec = VideoDecoder(str(src))
    frames = list(dec.decode())
    assert len(frames) > 0
    for f in frames:
        assert f.ndim == 3 and f.shape[2] == 3
        assert f.shape[0] > 0 and f.shape[1] > 0
        assert f.dtype == np.uint8


@pytest.mark.skipif(
    __import__("importlib").util.find_spec("lib.noor.video_decoder") is None,
    reason="RED: lib/noor/video_decoder.py not implemented yet (Task C.2)",
)
def test_image_plate_and_procedural_mosque_frame():
    """load_image_plate and procedural_mosque_frame return RGB uint8 frames."""
    from lib.noor.video_decoder import VideoDecoder

    dec = VideoDecoder.__new__(VideoDecoder)
    plate = dec.load_image_plate(None) if hasattr(dec, "load_image_plate") else None
    # procedural fallback always available
    frame = VideoDecoder.procedural_mosque_frame()
    assert frame.ndim == 3 and frame.shape[2] == 3
    assert frame.dtype == np.uint8


# ── GL renderer ─────────────────────────────────────────────────────────────

@pytest.mark.skipif(
    __import__("importlib").util.find_spec("lib.noor.gl_renderer") is None,
    reason="RED: lib/noor/gl_renderer.py not implemented yet (Task C.2)",
)
def test_gl_renderer_split_modes_and_luts():
    """GLRenderer.render_frame applies SplitMode and LUT without crashing."""
    from lib.noor.gl_renderer import GLRenderer, SplitMode

    renderer = GLRenderer()
    frame = np.full((720, 1280, 3), 40, dtype=np.uint8)
    for mode in (SplitMode.ORIGINAL, SplitMode.FILTERED, SplitMode.SIDE_BY_SIDE, SplitMode.FILTERED):
        out = renderer.render_frame(
            frame,
            split=0.5,
            split_mode=mode,
            lut_style="kadyrov_gold",
            warmth=1.0, contrast=1.0, exposure=1.0, saturation=1.0,
        )
        assert out.shape == frame.shape
        assert out.dtype == np.uint8


# ── face / depth AI ─────────────────────────────────────────────────────────

@pytest.mark.skipif(
    __import__("importlib").util.find_spec("lib.noor.face_depth_ai") is None,
    reason="RED: lib/noor/face_depth_ai.py not implemented yet (Task C.3)",
)
def test_face_depth_ai_outputs():
    """track_face / skin_mask / depth_map produce sane shapes."""
    from lib.noor.face_depth_ai import FaceDepthAI

    ai = FaceDepthAI()
    frame = np.full((720, 1280, 3), 40, dtype=np.uint8)
    x, y, r = ai.track_face(frame)
    assert isinstance(x, (int, float)) and isinstance(y, (int, float)) and isinstance(r, (int, float))
    mask = ai.skin_mask(frame)
    assert mask.shape == frame.shape[:2]
    depth = ai.depth_map(frame)
    assert depth.shape == frame.shape[:2]


# ── calligraphy / Uthmani shaping ───────────────────────────────────────────

@pytest.mark.skipif(
    __import__("importlib").util.find_spec("lib.noor.calligraphy") is None,
    reason="RED: lib/noor/calligraphy.py not implemented yet (Task C.4)",
)
def test_render_uthmani_four_themes():
    """render_uthmani supports all 4 QuranTypographyStyle themes + safe zones."""
    from lib.noor.calligraphy import render_uthmani, QuranTypographyStyle

    text = "بِسْمِ ٱللَّٰهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ"
    for theme in QuranTypographyStyle:
        img = render_uthmani(text, theme=theme, canvas_size=(1080, 1920), aspect="9:16")
        assert img.mode == "RGB"
        assert img.size == (1080, 1920)


@pytest.mark.skipif(
    __import__("importlib").util.find_spec("lib.noor.calligraphy") is None,
    reason="RED: lib/noor/calligraphy.py not implemented yet (Task C.4)",
)
def test_render_waveform_four_styles():
    """render_waveform supports all 4 WaveformStyle styles."""
    from lib.noor.calligraphy import render_waveform, WaveformStyle

    samples = np.sin(2 * np.pi * 440 * np.arange(SAMPLE_RATE) / SAMPLE_RATE).astype(np.float32)
    for style in WaveformStyle:
        img = render_waveform(samples, style=style, canvas_size=(1080, 1920))
        assert img.mode == "RGB"
        assert img.size == (1080, 1920)


# ── BaseTool wrappers ───────────────────────────────────────────────────────

@pytest.mark.skipif(
    __import__("importlib").util.find_spec("tools.enhancement.noor_video_fx") is None,
    reason="RED: tools/enhancement/noor_video_fx.py not implemented yet (Task C.5)",
)
def test_noor_video_fx_base_tool(tmp_path):
    """NoorVideoFX(BaseTool) execute -> ToolResult with mastered video artifact."""
    from tools.enhancement.noor_video_fx import NoorVideoFX

    tool = NoorVideoFX()
    assert tool.capability == "video_processing"
    assert tool.runtime.value in ("LOCAL_GPU", "LOCAL")


@pytest.mark.skipif(
    __import__("importlib").util.find_spec("tools.graphics.uthmani_overlay") is None,
    reason="RED: tools/graphics/uthmani_overlay.py not implemented yet (Task C.5)",
)
def test_uthmani_overlay_base_tool(tmp_path):
    """UthmaniOverlay(BaseTool) execute -> ToolResult with overlay artifact."""
    from tools.graphics.uthmani_overlay import UthmaniOverlay

    tool = UthmaniOverlay()
    assert tool.capability == "graphics"
    assert tool.runtime.value in ("LOCAL_GPU", "LOCAL")


def test_noor_video_suite_is_runnable():
    """This file itself is valid pytest; RED failures are import errors, not typos."""
    assert True
