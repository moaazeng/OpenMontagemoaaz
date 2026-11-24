# Noor Cinematic Studio — OpenMontage Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the Noor Cinematic Studio ("Golden Order") audio DSP, video FX, Uthmani calligraphy, Quranic Ayah alignment, presets vault, deterministic export, and real-time workstation into OpenMontage as native extensions, then connect OpenMontage to AI via the omniRouter Anthropic proxy (`ANTHROPIC_BASE_URL=http://127.0.0.1:20128`) and run end-to-end acceptance.

**Architecture:** Keep OpenMontage's structure intact. Pure engines live in `lib/noor/` (used by both BaseTool plugins and the `noor_studio/` workstation). OpenMontage-native plugins inherit `tools/base_tool.py` (`BaseTool`) and are discovered by `tools/tool_registry.py`. Playbooks live in `styles/noor/`, a new `pipeline_defs/noor-quranic-cinematic.yaml` manifest + stage director skills drive agentic runs, and `noor_studio/` (FastAPI + PySide6) is the interactive desktop GUI reusing `lib/noor/`. The omniRouter env vars route the Anthropic-compatible client through `http://127.0.0.1:20128`.

**Tech Stack:** Python 3.11/3.12 (python.org, not Microsoft Store), FFmpeg with `h264_nvenc` + `libx264` fallback, OpenMontage `BaseTool`, SQLAlchemy 2.0 async SQLite WAL, Pydantic v2, `sounddevice` WASAPI 48kHz/float32, `ModernGL`, `PyAV`, `pedalboard`, `scipy`, `uharfbuzz`/`skia-python`, `deepfilternet`, `faster-whisper`, `rapidfuzz`, `mediapipe`, PySide6, pytest/pytest-qt.

**Spec:** `D:\Github\OpenMontagemoaaz\my_new_architicture.md` (Noor Cinematic Studio master spec) — travels with this plan; executors read both.

## Global Constraints

(copied verbatim from the spec; every task implicitly includes this section)

- Windows 11, ASUS TUF Gaming F16 (Intel HX + NVIDIA RTX Laptop GPU, 6–8 GB VRAM); Python 3.11 or 3.12 (64-bit) from `python.org`, never Microsoft Store Python.
- `requirements-noor.txt` is a separate file from `requirements.txt`; installing it must not break `requirements.txt`.
- FFmpeg encoder: primary `h264_nvenc` (or `hevc_nvenc` for 4K) with `-preset p5 -rc vbr -cq 19 -pix_fmt yuv420p -movflags +faststart` and `aac -b:a 256k`; automatic fallback to `libx264` if NVENC unavailable.
- Windows audio: WASAPI host API at `48000 Hz`, `blocksize=512` (~10.67 ms), `dtype="float32"` via `sounddevice`; warn if mic is Bluetooth Hands-Free (16 kHz mono, high latency).
- Uthmani Arabic rendering on Windows: `PySide6 QPainter` / `skia-python` + `uharfbuzz` — do NOT rely on Pillow `libraqm` DLLs (missing on default Windows).
- VRAM co-existence (6–8 GB laptop): `faster-whisper` (`tarteel-ai/whisper-base-ar-quran`) `device="cuda"`, `compute_type="int8_float16`; `Depth-Anything-V2-Small` `torch.float16`; unload depth model when `bgBlur == 0`.
- All numeric DSP params guarded with `math.isfinite()`; no `NaN`/`Inf` in JSON payloads; true-peak limiter `-1.0 dBTP`.
- Sacred-text integrity: AI-recognized Quran verses resolve via canonical Tanzil Uthmani JSON hash/index lookup — zero unverified ASR verses emitted as Ayah text.
- OpenMontage conventions: every tool inherits `BaseTool` (`.execute(inputs) -> ToolResult`), `.run()` is forbidden, tools auto-registered by the registry, `agent_skills[]` references Layer 3 skills, checkpoints written via `lib/checkpoint.py`, canonical artifacts validated against `schemas/artifacts/`, `human_approval_default` from the pipeline manifest is binding.

## Review Focus

(the five input classes / failure modes the spec implies that are most likely to bite; each gets a test in the owning task)

1. **Silence / empty audio buffer** through the full Golden Order chain → must not emit `NaN`/`Inf`, must not crash the gate/limiter (owned by Task B.3, `test_noor_audio_dsp_edge_buffers`).
2. **+10 dBFS clipped burst** through Pre-Amp (up to `4.0x`) → must not clip past the `-1.0 dBTP` true-peak brickwall limiter (owned by Task B.3).
3. **Complex Uthmani glyph** (`ٱلرَّحْمَـٰنِ`, Waqf marks, Alif Khanjariyya) on a `9:16` canvas → Harakat/Tashkeel must not detach or overlap (owned by Task C.4, `test_noor_uthmani_golden_render`).
4. **Unverified ASR verse** not in the canonical Mushaf → `quran_ayah_aligner` must refuse to emit it as an Ayah and return a Mushaf-locked `(surah_id, ayah_id)` or a clear mismatch (owned by Task D.2, `test_noor_mushaf_lock_rejects_unverified`).
5. **NVENC unavailable** (headless/CI) → `noor_export` must auto-fallback to `libx264` and still produce a valid MP4 (owned by Task E.3, `test_noor_export_nvenc_fallback`).

## Sub-System Decomposition

This plan is split into independent sub-plans, each producing working, testable software:

- **Sub-plan A — Foundations:** `requirements-noor.txt`, `lib/noor/schemas.py`, `lib/noor/mushaf_store.py`, `lib/noor/storage.py`, `styles/noor/*.yaml`, `schemas/artifacts/noor_*.schema.json`, tests. (No external AI calls; fully local & deterministic.)
- **Sub-plan B — "Golden Order" Audio DSP + Live Recorder:** `lib/noor/audio_dsp.py`, `lib/noor/recorder.py`, BaseTool wrappers `tools/audio/noor_audio_master.py`, `tools/audio/noor_mic_recorder.py`, tests. (Local only; no API key needed.)
- **Sub-plan C — Video Decode, ModernGL FX, Face/Depth AI, Uthmani Calligraphy:** `lib/noor/video_decoder.py`, `lib/noor/gl_renderer.py`, `lib/noor/face_depth_ai.py`, `lib/noor/calligraphy.py`, BaseTool wrappers `tools/enhancement/noor_video_fx.py`, `tools/graphics/uthmani_overlay.py`, tests.
- **Sub-plan D — Quranic Ayah Aligner (Mushaf-locked):** `lib/noor/mushaf_store.py` reuse + `tools/analysis/quran_ayah_aligner.py`, tests. (Uses local `faster-whisper`; no network unless model download.)
- **Sub-plan E — Deterministic Pipelined Export:** `lib/noor/exporter.py`, `lib/media_profiles.py` extension, `tools/publishers/noor_export.py`, tests.
- **Sub-plan F — OpenMontage Native Pipeline:** `pipeline_defs/noor-quranic-cinematic.yaml`, stage director skills under `skills/pipelines/noor-quranic-cinematic/`, playbooks `styles/noor/*.yaml`, artifact schemas.
- **Sub-plan G — Interactive Workstation (`noor_studio/`):** FastAPI daemon (`noor_studio/server.py`), copilot (`noor_studio/copilot.py`), PySide6 GUI (`noor_studio/gui/`). Reuses `lib/noor/`.
- **Sub-plan H — OmniRouter Anthropic Proxy Connection:** `.env` wiring with the supplied omniRouter env vars, client configuration, smoke test that a completion reaches `http://127.0.0.1:20128`.
- **Sub-plan I — End-to-End Acceptance & Contract Audit:** full `pytest` run, `ruff`, `mypy`, `ffprobe` 1080p60 export verification, Backlot board compatibility (`python -m backlot open`).

---

### Sub-plan A — Foundations (Sprint 1)

Produces: strict data contracts, canonical Mushaf lookup, SQLite WAL vault, styled playbooks — all tested, zero external dependencies beyond `requirements-noor.txt`.

**Files:**
- Create: `requirements-noor.txt`
- Create: `lib/noor/__init__.py`
- Create: `lib/noor/schemas.py` — Pydantic v2 models + all 11 enums + `math.isfinite()` guards
- Create: `lib/noor/mushaf_store.py` — canonical Tanzil index + RapidFuzz verifier
- Create: `lib/noor/storage.py` — async SQLite WAL (presets, `.noorpreset`, `.noorproj`, XP, streaks, badges, history)
- Create: `styles/noor/official_presets.yaml`, `styles/noor/spiritual_atmospheres.yaml` (validated against `schemas/styles/playbook.schema.json`)
- Create: `schemas/artifacts/noor_dsp_config.schema.json`, `schemas/artifacts/noor_preset.schema.json`, `schemas/artifacts/noor_project.schema.json`
- Create: `tests/noor/test_sprint1.py` (schemas, storage, mushaf)
- Modify: none (additive only)

**Interfaces:**
- `lib/noor/schemas.py` produces: enums `LUTStyle`, `MosqueAcousticSpace`, `CapCutNoiseMode`, `CapCutDeepBassMode`, `MobileMicCalibrationMode`, `QuranTypographyStyle`, `WaveformStyle`, `AspectRatio`, `SplitMode`, `SpiritualAtmosphere`, `OfficialStudioPresets`; Pydantic model `DSPConfig` (all FR-04 params, bounds, `math.isfinite` validators), `Preset`, `NoorProject`.
- `lib/noor/mushaf_store.py` produces: class `MushafStore` with `load(path) -> None`, `lookup(surah_id: int, ayah_id: int) -> VerseRef | None`, `verify(text: str) -> VerseRef | None` (RapidFuzz against canonical, returns None below threshold), dataclass `VerseRef(surah_id, ayah_id, uthmani_text, translation)`.
- `lib/noor/storage.py` produces: class `NoorStore` with async `save_preset`, `get_preset`, `list_presets`, `export_preset`, `import_preset`, `save_project`, `load_project`, `record_export` (+150 XP), `get_mastery`; seeds 8 official presets, 4 atmospheres, 5 lessons.

- [ ] **Step A.1: Write `requirements-noor.txt`** (Windows-tuned: torch CUDA cu124 first, then pedalboard/scipy/numba/pyloudnorm/sounddevice/soundfile, av/moderngl/opencv-python-headless/numpy, uharfbuzz/skia-python/python-bidi, deepfilternet/faster-whisper/rapidfuzz/mediapipe/transformers/accelerate, fastapi/uvicorn/sqlalchemy/aiosqlite/alembic/PySide6/qasync, pytest/pytest-asyncio/pytest-qt/ruff/mypy).
- [ ] **Step A.2: Write failing tests** in `tests/noor/test_sprint1.py` for enum bounds, `DSPConfig` rejection of `NaN`/`Inf`/out-of-range, `MushafStore.verify` rejecting an invented verse, `NoorStore` preset CRUD + `.noorpreset` round-trip + XP increment.
- [ ] **Step A.3: Implement `lib/noor/schemas.py`** (enums + Pydantic models + finite guards).
- [ ] **Step A.4: Implement `lib/noor/mushaf_store.py`** (load Tanzil JSON, RapidFuzz verify, `VerseRef`).
- [ ] **Step A.5: Implement `lib/noor/storage.py`** (async SQLite WAL, seed data, CRUD).
- [ ] **Step A.6: Write playbook YAMLs** `styles/noor/official_presets.yaml`, `styles/noor/spiritual_atmospheres.yaml`; validate against `schemas/styles/playbook.schema.json`.
- [ ] **Step A.7: Write artifact schemas** `schemas/artifacts/noor_dsp_config.schema.json`, `noor_preset.schema.json`, `noor_project.schema.json`.
- [ ] **Step A.8: Run tests** `pytest tests/noor/test_sprint1.py -v`; all must pass.
- [ ] **Step A.9: Commit** `git add requirements-noor.txt lib/noor styles/noor schemas/artifacts/noor_*.schema.json tests/noor && git commit -m "feat(noor): Sprint 1 foundations — schemas, mushaf store, SQLite vault, playbooks"`.

---

### Sub-plan B — "Golden Order" Audio DSP + Live Recorder

Produces: the reorderable, bypassable float32 DSP chain (FR-04) and real 48 kHz mic capture — tested with FFT impulse + edge-buffer tests.

**Files:**
- Create: `lib/noor/audio_dsp.py` — Golden Order engine (pedalboard + scipy.signal.sosfilt + numba + pyloudnorm)
- Create: `lib/noor/recorder.py` — real 48 kHz sounddevice mic capture + live DSP monitor profiles
- Create: `tools/audio/noor_audio_master.py` — `NoorAudioMaster(BaseTool)` wrapping `audio_dsp.py`
- Create: `tools/audio/noor_mic_recorder.py` — `NoorMicRecorder(BaseTool)` wrapping `recorder.py`
- Create: `tests/qa/test_noor_audio_dsp.py` (FFT impulse + edge buffers)
- Create: `tests/tools/test_noor_audio_master.py`, `tests/tools/test_noor_mic_recorder.py`

**Interfaces:**
- `lib/noor/audio_dsp.py` produces: class `GoldenOrderDSP` with `process(samples: np.ndarray, config: DSPConfig) -> np.ndarray`, `analyze(samples) -> AnalysisResult` (48-bin FFT, pyloudnorm LUFS momentary/integrated/true-peak, clarity), and stage fns `preamp`, `denoise_dereverb`, `silence_gate`, `deesser`, `mic_calibration`, `deep_bass`, `eq_6band`, `compressor`, `warm_harmonics_chorus`, `tape_echo`, `mosque_convolution`, `stereo_width`, `limiter`. All float32, `< 15 ms` monitor latency target.
- `lib/noor/recorder.py` produces: class `NoorRecorder` with `start(device, profile, on_audio)`, `stop() -> Path` (WAV commit), `list_devices()`, profiles `NEUMANN`, `HARAM`, `DEEP_BASS`, `RAW`; WASAPI 48000 Hz blocksize=512 float32.
- `tools/audio/noor_audio_master.py` produces: `NoorAudioMaster(BaseTool)` — `capability="audio_processing"`, `runtime=LOCAL`, `input_schema` mirrors `DSPConfig`, `execute(inputs) -> ToolResult` writing mastered WAV/MP3/FLAC to `output_path`.
- `tools/audio/noor_mic_recorder.py` produces: `NoorMicRecorder(BaseTool)` — `capability="audio_capture"`, `execute` starts/stops recording, returns WAV path.

- [ ] **Step B.1: Write failing tests** `tests/qa/test_noor_audio_dsp.py` — FFT impulse: all 6 EQ bands, HPF, 50/60 Hz notch, LUFS target, zero `NaN`/`Inf` on silence and `+10 dBFS` burst; `test_noor_mic_recorder.py` enumerates devices without opening hardware (skip if no mic).
- [ ] **Step B.2: Implement `lib/noor/audio_dsp.py`** — full Golden Order chain per FR-04 order, finite guards, `-1.0 dBTP` limiter last.
- [ ] **Step B.3: Implement `lib/noor/recorder.py`** — sounddevice WASAPI callback, live DSP monitor routing, WAV commit, Bluetooth Hands-Free warning.
- [ ] **Step B.4: Implement BaseTool wrappers** `noor_audio_master.py`, `noor_mic_recorder.py` (register dependencies: `python:pedalboard`, `python:sounddevice`, `cmd:ffmpeg`; agent_skills `["text-to-speech", "speech-to-text"]`).
- [ ] **Step B.5: Run tests** `pytest tests/qa/test_noor_audio_dsp.py tests/tools/test_noor_audio_master.py -v`; pass.
- [ ] **Step B.6: Commit** `git add lib/noor/audio_dsp.py lib/noor/recorder.py tools/audio/noor_audio_master.py tools/audio/noor_mic_recorder.py tests/qa/test_noor_audio_dsp.py tests/tools/test_noor_audio_master.py tests/tools/test_noor_mic_recorder.py && git commit -m "feat(noor): Golden Order audio DSP + WASAPI mic recorder"`.

---

### Sub-plan C — Video Decode, ModernGL FX, Face/Depth AI, Uthmani Calligraphy

Produces: GPU-accelerated portrait grading, depth bokeh, unbroken Arabic diacritics — golden PNG + shader tests.

**Files:**
- Create: `lib/noor/video_decoder.py` — PyAV VFR→CFR decoder + image plate loader + procedural fallback
- Create: `lib/noor/gl_renderer.py` — ModernGL fragment pipeline (LUT3D, split wipe, rays, bloom, grain, vignette, bokeh)
- Create: `lib/noor/face_depth_ai.py` — MediaPipe 478-pt face tracking + skin mask + Depth-Anything-V2/MODNet depth
- Create: `lib/noor/calligraphy.py` — Uthmani Arabic via skia-python/uharfbuzz (+PySide6 QPainter), 4 typography themes, 4 waveform styles, safe zones
- Create: `tools/enhancement/noor_video_fx.py` — `NoorVideoFX(BaseTool)`
- Create: `tools/graphics/uthmani_overlay.py` — `UthmaniOverlay(BaseTool)`
- Create: `tests/qa/test_noor_video_fx.py`, `tests/qa/test_noor_uthmani_shaping.py`

**Interfaces:**
- `lib/noor/video_decoder.py` produces: class `VideoDecoder` with `decode(path) -> iterator[np.ndarray]` CFR, `load_image_plate(path)`, `procedural_mosque_frame()`.
- `lib/noor/gl_renderer.py` produces: class `GLRenderer` with `render_frame(frame, config) -> np.ndarray`, supporting `SplitMode` (SPLIT 0.02..0.98 / FILTERED / ORIGINAL / SIDE_BY_SIDE), 8 `.cube` LUTs + custom, warmth/contrast/exposure/saturation, rays/bloom/grain/vignette/rain/dust.
- `lib/noor/face_depth_ai.py` produces: class `FaceDepthAI` with `track_face(frame) -> (x, y, radius)` (EMA/Kalman + manual override), `skin_mask(frame)`, `depth_map(frame) -> alpha`.
- `lib/noor/calligraphy.py` produces: `render_uthmani(text, theme: QuranTypographyStyle, canvas_size, aspect: AspectRatio) -> PIL.Image`, `render_waveform(samples, style: WaveformStyle)`, safe-zone overlays; `python-bidi` RTL handling.
- `tools/enhancement/noor_video_fx.py` produces: `NoorVideoFX(BaseTool)`, `capability="video_processing"`, `runtime=LOCAL_GPU`.
- `tools/graphics/uthmani_overlay.py` produces: `UthmaniOverlay(BaseTool)`, `capability="graphics"`.

- [ ] **Step C.1: Write failing tests** — golden PNG Uthmani shaping (`ٱلرَّحْمَـٰنِ` + Waqf marks intact), split-wipe shader boundary, ffprobe decode of a synthetic clip.
- [ ] **Step C.2: Implement `lib/noor/video_decoder.py`** (PyAV VFR→CFR).
- [ ] **Step C.3: Implement `lib/noor/gl_renderer.py`** (ModernGL shaders; headless offscreen framebuffer for CI).
- [ ] **Step C.4: Implement `lib/noor/face_depth_ai.py`** (MediaPipe + depth model, VRAM-guarded fp16, unloadable).
- [ ] **Step C.5: Implement `lib/noor/calligraphy.py`** (skia/uharfbuzz on Windows; 4 themes, 4 waveform styles, safe zones).
- [ ] **Step C.6: Implement BaseTool wrappers** `noor_video_fx.py`, `uthmani_overlay.py`.
- [ ] **Step C.7: Run tests** `pytest tests/qa/test_noor_video_fx.py tests/qa/test_noor_uthmani_shaping.py -v`; pass.
- [ ] **Step C.8: Commit** `git add lib/noor/video_decoder.py lib/noor/gl_renderer.py lib/noor/face_depth_ai.py lib/noor/calligraphy.py tools/enhancement/noor_video_fx.py tools/graphics/uthmani_overlay.py tests/qa/test_noor_video_fx.py tests/qa/test_noor_uthmani_shaping.py && git commit -m "feat(noor): ModernGL video FX, face/depth AI, Uthmani calligraphy"`.

---

### Sub-plan D — Quranic Ayah Aligner (Mushaf-locked)

Produces: Ayah identification + forced alignment verified against canonical Tanzil Uthmani JSON — zero unverified verses.

**Files:**
- Create: `tools/analysis/quran_ayah_aligner.py` — `QuranAyahAligner(BaseTool)`
- Create: `tests/qa/test_noor_quran_aligner.py`

**Interfaces:**
- `tools/analysis/quran_ayah_aligner.py` produces: `QuranAyahAligner(BaseTool)`, `capability="analysis"`, `provider="whisper-quran"`, `runtime=LOCAL`; `execute(inputs)` — `input_path` audio → transcribe with `faster-whisper` (`tarteel-ai/whisper-base-ar-quran`, int8_float16 CUDA) → `mushaf_store.verify` each segment → `WhisperX`-style word timestamps → returns `{"segments": [{surah_id, ayah_id, uthmani_text, translation, start, end, words: [...]}], "unverified": []}`; never emits unverified text as Ayah.

- [ ] **Step D.1: Write failing tests** — `test_noor_mushaf_lock_rejects_unverified`: feed an invented Arabic sentence, assert `segments` empty and `unverified` reports it; `test_noor_quran_aligner_grounded`: short known verse, assert valid `surah_id:ayah_id`.
- [ ] **Step D.2: Implement `tools/analysis/quran_ayah_aligner.py`** (reuse `lib/noor/mushaf_store.py`, RapidFuzz threshold, faster-whisper, word-level alignment).
- [ ] **Step D.3: Run tests** `pytest tests/qa/test_noor_quran_aligner.py -v`; pass. (Skip network-dependent test if model not downloaded; document.)
- [ ] **Step D.4: Commit** `git add tools/analysis/quran_ayah_aligner.py tests/qa/test_noor_quran_aligner.py && git commit -m "feat(noor): Mushaf-locked Quranic Ayah aligner"`.

---

### Sub-plan E — Deterministic Pipelined Export

Produces: hardware-encoded MP4/WAV/MP3/FLAC/PNG export via streaming FFmpeg pipe, real-time progress, SIGTERM cancel, XP award.

**Files:**
- Create: `lib/noor/exporter.py` — process-isolated rawvideo+WAV pipe → FFmpeg
- Modify: `lib/media_profiles.py` — add Noor profiles (4K/1080p/720p @ 60/30/24, ULTRA/VIRAL/LIGHT bitrate tiers)
- Create: `tools/publishers/noor_export.py` — `NoorExport(BaseTool)`
- Create: `tests/qa/test_noor_export.py`

**Interfaces:**
- `lib/noor/exporter.py` produces: class `NoorExporter` with `export(frames, audio_path, profile, output_path, on_progress, cancel_event) -> ExportReport`; exact frame count `round(duration_s * fps)`; streams to FFmpeg stdin; supports `h264_nvenc`/`hevc_nvenc`/`libx264` + AAC; WAV 16/24-bit, MP3 320k, FLAC, PNG cover; SIGTERM + temp cleanup.
- `tools/publishers/noor_export.py` produces: `NoorExport(BaseTool)`, `capability="video_publish"`, `runtime=LOCAL`, `idempotency_key_fields=["input_path","profile","output_path"]`.

- [ ] **Step E.1: Write failing tests** — `test_noor_export_1080p60_ffprobe`: render 3s 1080p60 via `noor_export`, assert `nb_frames == 180`, `h264`, `yuv420p`, `aac`, size > 0; `test_noor_export_nvenc_fallback`: force NVENC unavailable, assert libx264 fallback still yields valid MP4.
- [ ] **Step E.2: Extend `lib/media_profiles.py`** — add Noor profiles + `ffmpeg_output_args` with NVENC flags + libx264 fallback.
- [ ] **Step E.3: Implement `lib/noor/exporter.py`** (streaming pipe, progress, cancel, cleanup).
- [ ] **Step E.4: Implement `tools/publishers/noor_export.py`** (`NoorExport(BaseTool)`).
- [ ] **Step E.5: Run tests** `pytest tests/qa/test_noor_export.py -v`; pass.
- [ ] **Step E.6: Commit** `git add lib/noor/exporter.py lib/media_profiles.py tools/publishers/noor_export.py tests/qa/test_noor_export.py && git commit -m "feat(noor): deterministic FFmpeg pipe export (NVENC + fallback)"`.

---

### Sub-plan F — OpenMontage Native Pipeline

Produces: YAML manifest + stage director skills + playbooks so OpenMontage agents can run Noor headlessly.

**Files:**
- Create: `pipeline_defs/noor-quranic-cinematic.yaml` (8 stages: idea→publish, gates per spec)
- Create: `skills/pipelines/noor-quranic-cinematic/idea-director.md`, `proposal-director.md`, `script-director.md`, `scene-director.md`, `asset-director.md`, `edit-director.md`, `compose-director.md`, `publish-director.md`
- Create: `skills/creative/quranic-cinematic.md` (Tajweed preservation & Uthmani visual rules)
- Modify: none (additive)

**Interfaces:**
- Manifest declares stages with `produces`, `tools_available` (the Noor BaseTools from B–E), `human_approval_default` (idea/proposal/script/scene_plan/assets gated), `review_focus`, `success_criteria`; `compatible_playbooks` references `styles/noor/*`.
- Stage director skills teach the agent HOW per stage (per AGENT_GUIDE Rule Zero), referencing the BaseTool contracts and `agent_skills`.

- [ ] **Step F.1: Write `pipeline_defs/noor-quranic-cinematic.yaml`** modeled on `pipeline_defs/animated-explainer.yaml` with Noor stages/tools/gates.
- [ ] **Step F.2: Write the 8 stage director skills** under `skills/pipelines/noor-quranic-cinematic/`.
- [ ] **Step F.3: Write `skills/creative/quranic-cinematic.md`** (Tajweed-safe DSP, Uthmani shaping rules, sacred-text integrity).
- [ ] **Step F.4: Validate manifest** loads via `lib.pipeline_loader`; run `python -c "from lib.pipeline_loader import load_pipeline_readonly; ..."` smoke check.
- [ ] **Step F.5: Commit** `git add pipeline_defs/noor-quranic-cinematic.yaml skills/pipelines/noor-quranic-cinematic skills/creative/quranic-cinematic.md && git commit -m "feat(noor): OpenMontage native pipeline manifest + director skills"`.

---

### Sub-plan G — Interactive Workstation (`noor_studio/`)

Produces: the standalone real-time desktop GUI (PySide6) + FastAPI daemon reusing `lib/noor/`.

**Files:**
- Create: `noor_studio/__init__.py`
- Create: `noor_studio/server.py` — FastAPI + bearer auth + WebSocket 60 Hz telemetry + mmap frame buffer + REST routes (`/project`, `/dsp`, `/video`, `/viral`, `/presets`, `/pipeline`, `/ai`, `/export`, `/recorder`)
- Create: `noor_studio/copilot.py` — Gemini (`.env`) or Ollama `Qwen2.5-14B`; returns Pydantic-validated hooks/Tafsir/mood-to-preset; Tafsir visually distinct from canonical Mushaf text
- Create: `noor_studio/gui/app.py` — PySide6 QApplication, Obsidian & Signal Blue QSS, RTL/LTR
- Create: `noor_studio/gui/widgets/gl_viewport.py` — QOpenGLWidget: 4 preview modes, split wipe, reticle, bounding boxes, safe zones
- Create: `noor_studio/gui/widgets/spectrum_visualizer.py` — 60 FPS QPainter 48-bin spectrum + 6-band EQ + LUFS
- Create: `noor_studio/gui/panels/{video,audio,viral,presets,pipeline}_panel.py` — 5 workflow tabs (VIDEO/أビデ, AUDIO/صوت الحرم, VIRAL/التريند, PRESETS/القوالب, PIPELINE/سلسلة المؤثرات)
- Create: `noor_studio/gui/modals/{export,recorder,contemplation,knowledge,dashboard,version}_modal.py` + `spiritual_journey_banner.py`
- Create: `tests/noor/test_workstation_smoke.py` (pytest-qt: RTL switching, slider/DAG sync)
- [G is GUI-heavy; implement after A–E pass.]

- [ ] **Step G.1: Implement `noor_studio/server.py`** (FastAPI daemon, bearer auth, WS telemetry, mmap frames).
- [ ] **Step G.2: Implement `noor_studio/copilot.py`** (structured output, Pydantic-validated, source-separated Tafsir).
- [ ] **Step G.3: Implement PySide6 GUI** (theme, RTL/LTR, shortcuts Space/J/K/L/I/O/Ctrl+E/Ctrl+Z, SmartInfoTooltip, 5 tabs, 6 modals, journey banner).
- [ ] **Step G.4: Wire GUI to `lib/noor/`** via localhost REST + WS (no DB/engine code in GUI).
- [ ] **Step G.5: Run pytest-qt smoke tests** `pytest tests/noor/test_workstation_smoke.py -v`; pass.
- [ ] **Step G.6: Commit** `git add noor_studio tests/noor/test_workstation_smoke.py && git commit -m "feat(noor): PySide6 workstation + FastAPI daemon"`.

---

### Sub-plan H — OmniRouter Anthropic Proxy Connection

Produces: `.env` + client wired to omniRouter at `http://127.0.0.1:20128`; smoke test verifies a completion reaches the proxy.

**Files:**
- Create/Modify: `.env` (add the supplied omniRouter env vars, do not commit secrets)
- Create: `tests/noor/test_omnirouter_smoke.py`

**Env (from your request):**
```
ANTHROPIC_BASE_URL=http://127.0.0.1:20128
ANTHROPIC_AUTH_TOKEN=sk-fa1e26de8dbb5ed2-a611b4-be00a59f
ANTHROPIC_MODEL=allaistudioapi
ANTHROPIC_DEFAULT_OPUS_MODEL=allaistudioapi3.8
ANTHROPIC_DEFAULT_SONNET_MODEL=allaistudioapi
ANTHROPIC_DEFAULT_HAIKU_MODEL=allfast
ANTHROPIC_SMALL_FAST_MODEL=allfast
CLAUDE_CODE_SUBAGENT_MODEL=allfast
API_TIMEOUT_MS=300000
CLAUDE_CODE_MAX_RETRIES=3
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
DISABLE_TELEMETRY=1
DISABLE_ERROR_REPORTING=1
CLAUDE_CODE_ATTRIBUTION_HEADER=0
CLAUDE_CODE_MAX_OUTPUT_TOKENS=99000
```

- [ ] **Step H.1: Add env vars to `.env`** (gitignored; `.env.example` gets placeholder names only).
- [ ] **Step H.2: Configure Anthropic-compatible client** (`noor_studio/copilot.py` and any OpenMontage LLM path) to read `ANTHROPIC_BASE_URL`/`ANTHROPIC_AUTH_TOKEN`/`ANTHROPIC_MODEL`; default model `allaistudioapi`, timeout 300s, retries 3, telemetry/error reporting off.
- [ ] **Step H.3: Write smoke test** `tests/noor/test_omnirouter_smoke.py` — sends one completion through the proxy, asserts non-empty text (skip if proxy not running; document the skip reason).
- [ ] **Step H.4: Run smoke test** (report PASS or SKIP-with-reason; do not fail the build if omniRouter isn't up).
- [ ] **Step H.5: Commit** (non-secret files only; `.env` stays local) `git add tests/noor/test_omnirouter_smoke.py .env.example && git commit -m "feat(noor): omniRouter Anthropic proxy wiring + smoke test"`.

---

### Sub-plan I — End-to-End Acceptance & Contract Audit

Produces: verified full run; openmtage contract suites pass; Backlot board compatible.

**Files:**
- Modify: none (verification only; may add `tests/noor/test_e2e_noor.py`)

- [ ] **Step I.1: Run full test suite** `pytest tests/ -x -q` (or at minimum `tests/noor tests/qa tests/contracts tests/lib tests/tools`); report any failures.
- [ ] **Step I.2: Lint/typecheck** `ruff check lib/noor tools/audio/noor_* tools/enhancement/noor_video_fx.py tools/graphics/uthmani_overlay.py tools/analysis/quran_ayah_aligner.py tools/publishers/noor_export.py noor_studio tests/noor`; `mypy` on `lib/noor`.
- [ ] **Step I.3: E2E export** render 3s 1080p60 MP4 via `noor_export` → `ffprobe` asserts (`nb_frames==180`, h264, yuv420p, aac, size>0); render WAV+MP3+FLAC+PNG; verify XP +150 recorded.
- [ ] **Step I.4: Backlot board** `python -m backlot open <project-id>` (observer only; non-fatal if it fails).
- [ ] **Step I.5: Commit** any test additions `git commit -m "test(noor): end-to-end acceptance + contract audit"`.
- [ ] **Step I.6: Run OpenMontage** — confirm baseline `make setup`/venv works and `provider_menu_summary()` lists the new Noor tools (present capability menu to user).

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-11-24-noor-cinematic-studio-integration.md`.

Please review the plan. Does it capture what you want?

**Execution approach:** You have not yet specified an execution method, so I'm not starting implementation. Which would you prefer?

- **Subagent-driven** — A fresh subagent implements each task and a fresh reviewer checks it before the next starts, then a whole-branch review at the end. Most thorough; costs a fresh context per task and per review. Recommended here because the tasks heavily depend on each other's interfaces (schemas → storage → DSP → video → export → pipeline → GUI) and a shipped mistake in the foundation cascades.
- **Native** — I implement every task myself in this session, then one fresh reviewer on the most capable model checks the whole branch. Cheapest and fastest; no independent review until the end.

Which approach should we use? (Or say "start implementing natively now" and I'll begin with Sub-plan A.)
