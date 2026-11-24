# Noor Cinematic Studio — Full System Architecture, IEEE-830 SRS, Python Backend + GUI Blueprint & Master Build Prompt

> **Document Scope & Grounding Policy:**  
> This document is generated directly from a full inspection of the **Noor Cinematic (`v3.3.0`, build `2026.08.23-pro`)** Android repository (`com.aistudio.noorcinematic.stduio`). It separates **Observed Implemented Features**, **Observed Declared/Partial Prototype Elements**, and the **Target Production Python Backend + Desktop GUI Architecture**, concluding with a complete, copy-pasteable **Prompt-Format Master Feature Specification**.

---

## Table of Contents
1. [Complete Feature Audit (Repository Ground Truth)](#1-complete-feature-audit-repository-ground-truth)
2. [IEEE-830 Software Requirements Specification (SRS)](#2-ieee-830-software-requirements-specification-srs)
3. [Decoupled Python Backend + GUI Architecture](#3-decoupled-python-backend--gui-architecture)
4. [Canonical Data Contracts (Pydantic v2 / JSON)](#4-canonical-data-contracts-pydantic-v2--json)
5. [Recommended Python Libraries Stack](#5-recommended-python-libraries-stack)
6. [Best AI Models & Hardware Deployment Matrix](#6-best-ai-models--hardware-deployment-matrix)
7. [Engineering Pitfalls & Verification Gate](#7-engineering-pitfalls--verification-strategy)
8. [Prompt-Format Master Specification (All Features Ready to Copy-Paste)](#8-prompt-format-master-specification-all-features-ready-to-copy-paste)

---

## 1. Complete Feature Audit (Repository Ground Truth)

### 1.1 Feature Truthfulness Matrix

| Feature Domain | Observed Implemented in Android Repo | Declared / Partial / Stubbed in Android Repo (Must Be Completed in Python) |
| :--- | :--- | :--- |
| **Workstation Shell & Bilingual UX** | Runtime bilingual switching (`ar` default / `en`); Obsidian & Signal Blue dark theme (`Color.kt`, `Theme.kt`, `Type.kt`); 5 workflow tabs (`VIDEO` / قديروف, `AUDIO` / صوت الحرم, `VIRAL` / التريند, `PRESETS` / القوالب, `PIPELINE` / سلسلة المؤثرات); `SmartInfoTooltip` (`ℹ️` User Benefit + Technical Engineering Detail); Quick-Import dropdown (Video / Audio); `VersionModal` changelog (`v3.3.0`, `v3.2.0`). | `MediaType` declares `CAMERA` and `IMAGE`, while quick-import currently triggers video & audio pickers (`StudioHeader.kt`). |
| **Viewport, Split Compare & Direct Manipulation** | 4 Preview Modes (`SPLIT` draggable `0.02..0.98`, `FILTERED`, `ORIGINAL`, `SIDE_BY_SIDE`); Hold-to-Compare raw toggle; Fullscreen Cinema dialog (`CapCutFullScreenPreviewDialog`); draggable Face Glow reticle (`faceManualX/Y`); CapCut bounding boxes (`AYAH_CARD`, `WAVEFORM`, `HOOK_HEADER`, `FACE_GLOW`); Safe Zone Guides (3×3 rule-of-thirds + TikTok/Reels HUD exclusion masks); `TrimRange` scrubbing & duration clamp; 1-click Pro Audio HUD (`Zero-Noise`, `Haram Reverb`, `Deep Bass`). | Uses a procedural reciter/mosque bitmap when no external video is loaded (`VideoRenderingEngine`). |
| **Video FX & Color Grading Engine** | 8 `LUTStyle` presets (`KADYROV_GOLD`, `ROYAL_DARK`, `MAKKAH_SUNRISE`, `MADINA_EMERALD`, `DAWN_SPIRITUAL`, `VINTAGE_FILM`, `PURE_MUSHAF`, `DRAMATIC_MONOCHROME`) + `lutIntensity` (`0–100%`); `faceGlow`, `skinSmooth`, `sharpen`, `lightRays`, `bloom`, `filmGrain`, `vignette`, `warmth`, `contrast`, `dynamicExposure`. | `bgBlur` (Bokeh), `saturation` (`-50..100%`), and real ML face tracking (`faceDetectionEnabled` currently defaults to fixed `(0.5, 0.42)`) are exposed in `VideoFilterSettings` & `VideoControlPanel` but not executed in `VideoRenderingEngine`. |
| **Quranic Audio DSP Mastering ("Golden Order")** | Real-time 44.1 kHz stereo playback; 12s offline synthesized harmonic+vibrato demo reciter cache; 48-bin FFT spectrum + 6-band log EQ curve (`AudioVisualizer`) + LUFS/Clarity telemetry; Pre-Amp (`0.5x–4.0x`); `micAirFilter` HPF (`40–75 Hz`); `spectralDeReverb` (`420 Hz` cut); `silenceGate` (`-60..-20 dB`); `deEsserSensitivity` (`6.8 kHz`); `MobileMicCalibrationMode` (`STUDIO_NEUMANN`, `BROADCAST_SHURE`, `SMOOTH_WARM`, `RAW_CALIBRATED`) + `vocalClarityBooster`; `CapCutDeepBassMode` (`OFF`, `WARM`, `CAPCUT_PRO`, `KADYROV_ELITE`) + sub (`65 Hz`), chest (`130–140 Hz`), drive; 6-Band Parametric EQ (`80/120/250/2500/5000/10000 Hz`, `±12 dB`); `warmHarmonics` (`tanh`); `doubleVoice` (`24 ms` chorus); `echo` circular delay (`50–800 ms`, `0–90%` feedback); 5 `MosqueAcousticSpace` spaces (`HARAM_MAKKAH`, `PROPHET_MADINA`, `ALAQSA`, `PRO_STUDIO`, `DOME_HALL`) via Freeverb (8 comb + 4 allpass); `stereoWidth` M/S; `masterVolume` + brickwall `tanh` limiter. | External audio file import currently falls back to `MediaType.SAMPLE` rather than decoding external MP3/WAV PCM; `CapCutNoiseMode` (`OFF`, `STANDARD`, `PRO_CLEAN`, `EXTREME`), `capcutNoiseReduction`, `capcutHissRemover`, `capcutHumRemover`, `dogBarkNoiseCanceler`, and `compressorEnabled` (`compressorThreshold`, `compressorRatio`) exist in `AudioFilterSettings`/UI/DB but need STFT/AI denoising, 50/60 Hz notch, and RMS dynamic compressor in DSP. |
| **Viral Social & Quranic Calligraphy Toolkit** | Aspect Ratios (`9:16`, `1:1`, `16:9`, `4:5`); Top Viral Hook pill banner + 8 `ViralTrendHooksList` templates; 6 `ViralAyahTemplatesList` + 8 `CuratedSpiritualAyahsList` inspirations with Maqam & Tafsir; editable Arabic Ayah, English translation, Surah, Ayah #, Reciter watermark; 4 `QuranTypographyStyle` themes (`UTHMANI_GOLD`, `PURE_WHITE`, `ROYAL_EMERALD`, `AMBER_GLOW`); `cardBackdropBlur` + `cardOpacity`; Y-position sliders; reactive waveform (`gold`, `emerald`, `white`); atmospheric FX (`goldenDustParticles`, `godRaysSunbeams`, `cinematicRain`). | `WaveformStyle` defines 4 styles (`SOLID`, `GLASS_MODERN`, `GLASS_BARS`, `VINTAGE_DOTS`), while rendering primarily draws bar style; `Audio` MP3 export is described in `VersionModal v3.3.0` while exporter currently writes stereo WAV. |
| **Studio Recorder Modal** | `MobileStudioRecorderModal` with wired-headphone anti-feedback alert, `3-2-1` countdown, live timer, animated VU meter, and 4 live DSP profiles (`NEUMANN`, `HARAM`, `DEEP_BASS`, `RAW`). | Simulates timer & VU levels rather than capturing real hardware microphone PCM. |
| **Presets Vault & Local Persistence** | 8 Official Master Presets (`kadyrov_master`, `capcut_pro_elite`, `kadyrov_elite_bass`, `podcast_serat_sawy`, `viral_islam_sobhi`, `viral_hazza_albalushi`, `grand_mosque_haram`, `pro_studio_master`); Custom Preset CRUD in SQLite (`Room` `PresetEntity`) + Reset Defaults. | No portable `.noorproj` / `.noorpreset` file import/export yet. |
| **Interactive Effect Pipeline** | `EffectPipelineScreen` connected node-and-arrow graph across `AUDIO`, `VIDEO`, `OVERLAY`, Active-Only filter, KPI pills (Total Nodes, Active FX, DSP Latency), tap-to-inspect, left/right reorder buttons, jump-to-tab. | Reorder state lives in local Compose UI state (`remember`) rather than driving actual execution order in the audio/video engines. |
| **Spiritual Journey, Sanctuary & Mastery** | Collapsible 4-station `SpiritualJourneyBanner` + 4 `SpiritualAtmosphere` 1-click moods (`SAKINA_DAWN`, `JALAL_MAJESTY`, `RAJAA_HOPE`, `TAHAJJUD_SOLITUDE`); Fullscreen `ContemplationModeDialog` (محراب التدبر) with breathing cadence; Searchable `SpiritualKnowledgeModal` (5 deep Quranic acoustic/visual lessons); `TransformationDashboardModal` (Streak, +150 XP/export, 3 pillars, 5 milestone badges). | Mastery XP/streak counters live in session ViewModel memory unless explicitly persisted to DB. |
| **Export & Sharing Pipeline** | 3 Export Modes: **Video** (`MP4 H.264 + AAC 192kbps`, `4K`/`1080p`/`720p`, `60/30/24 FPS`, `ULTRA 16M`/`VIRAL 8M`/`LIGHT 4M`), **Audio** (`Stereo 44.1kHz 16-bit WAV`), **Cover Image** (`PNG`); Trim enforcement; progress %, stage telemetry, cancel/retry, completion XP card, OS Share + Edit in CapCut. | Android `MediaCodec` loop encountered mobile device timeout/frame-rate bottlenecks; Python desktop backend solves this via pipelined GPU OpenGL rendering + native `FFmpeg` (`NVENC`/`VideoToolbox`/`libx264`). |

---

## 2. IEEE-830 Software Requirements Specification (SRS)

### 2.1 Purpose & User Personas
**Product:** Noor Cinematic Studio (Python Backend Engine + Desktop Workstation GUI)  
**Mission:** Local-first, studio-grade Quranic recitation mastering, cinematic portrait color grading, AI speech restoration, and viral Arabic calligraphy video production.

**Primary Personas:**
1. **The Quran Reciter (القارئ):** Records voice via USB/XLR mic, needs `< 15 ms` live monitor latency, zero-artifact denoising that preserves *Tajweed* (*Ghunnah*, *Qalqalah*, *Madd*), authentic Haramain reverb, and calm distraction-free recording.
2. **The Viral Islamic Creator (صانع المحتوى):** Imports video/audio clips, applies 1-click Kadyrov/Haram presets, auto-aligns Quran verses with audio, snaps hooks/cards to TikTok/Reels safe zones, and exports crisp 1080p/4K 60 FPS MP4s fast.
3. **The Podcast & Khutbah Producer:** Requires `-14 LUFS` loudness normalization, 50/60 Hz hum removal, de-essing, boxiness cleanup, and batch WAV/MP3/MP4 rendering.

### 2.2 Functional Requirements

| ID | Subsystem | Specification |
| :--- | :--- | :--- |
| **FR-01** | **Media Ingestion & Projects** | Ingest `MP4/MOV/MKV/WEBM` video, `WAV/MP3/FLAC/M4A/AAC` audio, `PNG/JPG/WEBP` images, and live mic streams (`44.1k/48k Hz float32`). Extract stream metadata via `PyAV`/`ffprobe`, normalize VFR videos to constant frame rate (CFR), and support `.noorproj` JSON project save/load. |
| **FR-02** | **Multi-Mode Real-Time Viewport** | Render interactive preview at $\ge 30$ FPS (target 60 FPS) across `SPLIT` (`0.02..0.98` draggable wipe), `FILTERED`, `ORIGINAL`, and `SIDE_BY_SIDE`. Include Hold-to-Compare raw toggle, Fullscreen preview, draggable Face Glow reticle `(x, y)`, bounding-box HUD selection (`AYAH_CARD`, `WAVEFORM`, `HOOK_HEADER`, `FACE_GLOW`), and Safe Zone overlays (3×3 grid + TikTok/Reels HUD zones). |
| **FR-03** | **Live Studio Recorder** | Capture real `48 kHz` microphone PCM via `sounddevice` (PortAudio WASAPI/CoreAudio/ASIO/ALSA) with headphone feedback warning, `3-2-1` countdown, live peak/RMS dBFS VU meter, switchable live DSP monitor profiles (`NEUMANN`, `HARAM`, `DEEP_BASS`, `RAW`), and direct timeline insertion. |
| **FR-04** | **Quranic Audio DSP ("Golden Order")** | Process stereo `float32` audio through a bypassable, reorderable chain: Pre-Amp gain (`0.5x–4.0x`) → AI Speech Denoise/De-Reverb + 50/60 Hz Notch Hum + Hiss Remover → Breath-Aware Silence Gate (`-60..-20 dB`) → Split-Band De-Esser (`6.8 kHz`) → Mic Calibration & Vocal Clarity (`2.8–3.6 kHz`) → Deep Bass (`65 Hz` Sub, `135 Hz` Chest, Soft-Clip Drive) → 6-Band Parametric EQ (`80/120/250/2500/5000/10000 Hz`, `±12 dB`) → RMS Vocal Compressor → Tube Warm Harmonics (`tanh`) & 24 ms Double-Voice Chorus → Circular Tape Echo (`50–800 ms`, `0–90%` feedback) → Mosque Acoustics (Real FFT Impulse Convolution + Freeverb fallback for Makkah, Madinah, Al-Aqsa, Dome Hall, Pro Studio) → M/S Stereo Width → True-Peak Limiter (`-1.0 dBTP`) + ITU-R BS.1770 LUFS & 48-bin FFT stream. |
| **FR-05** | **Video FX, Face AI & Depth Bokeh** | Execute GPU fragment shaders (`ModernGL`): 3D `.cube` LUT trilinear grading (8 built-in + custom `.cube`), Color Balance (`warmth`, `contrast`, `dynamicExposure`, `saturation`), ML Face Landmark Tracking (`auto` per-frame smoothed `(x, y, radius)` or manual override), Skin-Masked Bilateral Smoothing, Face Glow & Unsharp Sharpen, True Depth/Matting Background Bokeh (`bgBlur`), and Atmospheric Shaders (`lightRays`, `bloom`, `filmGrain`, `vignette`, dust particles, cinematic rain). |
| **FR-06** | **Arabic Uthmani Calligraphy & Overlays** | Render Uthmani Arabic with full HarfBuzz + FriBiDi `GPOS` diacritic positioning (`libraqm`/`uharfbuzz`) across `9:16`, `1:1`, `16:9`, `4:5` canvases; Viral Hook banner; 4 Typography Themes; frosted glass blur card; 4 `WaveformStyle` renderers (`SOLID`, `GLASS_MODERN`, `GLASS_BARS`, `VINTAGE_DOTS`); and optional word-by-word Tajweed/Karaoke highlight from forced alignment. |
| **FR-07** | **Executable Dynamic Pipeline DAG** | Mutating node order or bypass toggles in the Pipeline view directly rewires the execution sequence in `audio/engine.py` and `video/gl_renderer.py`, reporting measured real per-node latency (`ms`). |
| **FR-08** | **Presets Vault & Persistence** | Pre-seed the 8 Official Master Presets in SQLite WAL via `SQLAlchemy`; support Create, Edit, Duplicate, Import/Export (`.noorpreset`), Delete, Reset Defaults, plus persistent Mastery XP, streaks, and export history. |
| **FR-09** | **AI Copilot & Spiritual Sanctuary** | Provide: (a) Automatic Ayah identification & forced timestamp alignment verified strictly against a local canonical Tanzil Uthmani Mushaf JSON (zero unverified hallucinated verses), (b) AI Creative Copilot for hooks, Tafsir reflections, and mood-to-preset parameter mapping, (c) 4-station `SpiritualJourneyBanner` + 4 `SpiritualAtmosphere` presets, (d) Fullscreen `ContemplationModeDialog` (محراب التدبر), (e) Searchable `SpiritualKnowledgeModal`, and (f) `TransformationDashboardModal`. |
| **FR-10** | **Deterministic Pipelined Export** | Export **Video** (`MP4 H.264/H.265 + AAC 192–320 kbps` at `4K/1080p/720p`, `60/30/24 FPS`, `ULTRA/VIRAL/LIGHT`), **Audio** (`WAV 16/24-bit` + `MP3 320 kbps` + `FLAC`), and **Cover** (`PNG`). Stream frames directly via pipe to `FFmpeg` (`NVENC`/`VideoToolbox`/`QSV`/`libx264`) with real-time progress %, ETA, FPS telemetry, safe cancellation, and zero 25s mobile timeout limit. |
| **FR-11** | **Bilingual Accessibility & Shortcuts** | Full Arabic (RTL mirrored layout) and English (LTR) switching, WCAG 2.1 AA contrast (`>= 4.5:1`), NLE keyboard shortcuts (`Space`, `J/K/L`, `I/O`, `Ctrl/Cmd+E`, `Ctrl/Cmd+Z`), and dual-layer `SmartInfoTooltip` (`Simple User Benefit` + `Engineering Algorithm Detail`). |

### 2.3 Non-Functional Requirements
- **Audio Round-Trip Latency:** $\le 15\text{ ms}$ (`512–1024` samples @ `48 kHz`) in C++/Numba callback with zero Python heap allocations on the audio thread.
- **Viewport Frame Rate:** $\ge 30\text{ FPS}$ interactive scrubbing (target `60 FPS`) on `720p` preview textures via `ModernGL`.
- **Export Determinism & Memory Ceiling:** Exact frame count `round(duration_s * fps)`, streaming generator pattern keeping peak RAM $< 2\text{ GB}$ (excluding optional local LLM weights), automatic cleanup of temp pipes/files on abort.
- **Security & Privacy:** Local-first by default; bearer-authenticated localhost IPC (`127.0.0.1`); OS Keyring / `.env` secret management; strict file magic-byte & path-traversal validation; zero unsanitized `NaN`/`Inf` in JSON payloads.
- **Sacred Text Integrity:** All AI-recognized Quran verses must resolve via canonical Mushaf hash/index lookup; LLM-generated reflections are always visually distinct from verbatim Ayah text.

---

## 3. Decoupled Python Backend + GUI Architecture

### 3.1 Architecture Overview
Python's Global Interpreter Lock (GIL) makes single-process Tkinter/pure-Python audio+video choppy. The system solves this by isolating **UI**, **Orchestration**, **Real-Time Audio C++**, **GPU Shaders**, and **FFmpeg/AI Workers**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    noor_gui (PySide6 / Qt 6 Workstation)                    │
│  ┌──────────────┐  ┌─────────────────────────┐  ┌────────────────────────┐  │
│  │ StudioHeader │  │ QOpenGLWidget Viewport  │  │ 5 Inspector Tabs       │  │
│  │ Import/Lang  │  │ Split/2-Up/SafeZones    │  │ Video|Audio|Viral|     │  │
│  │ Export/Play  │  │ Draggable Reticle/Boxes │  │ Presets|Pipeline DAG   │  │
│  └──────┬───────┘  └────────────▲────────────┘  └───────────┬────────────┘  │
│         │ REST Commands         │ SharedMem Frame Ring /    │ Debounced     │
│         │ (HTTP/JSON + Token)   │ WS 30-60Hz FFT & LUFS     │ State Patches │
└─────────┼───────────────────────┼───────────────────────────┼───────────────┘
          ▼                       │                           ▼
┌─────────────────────────────────┴───────────────────────────────────────────┐
│                  noor_backend (FastAPI + AsyncIO Daemon)                    │
│  ┌─────────────────────┐  ┌───────────────────────┐  ┌───────────────────┐  │
│  │ Session State Store │  │ Pipeline DAG Compiler │  │ SQLite WAL Store  │  │
│  │ (Pydantic v2 Models)│  │ (Dynamic Node Order)  │  │ Presets/XP/History│  │
│  └─────────┬───────────┘  └───────────┬───────────┘  └───────────────────┘  │
│            │                          │                                     │
│   ┌────────▼─────────┐      ┌─────────▼──────────┐    ┌──────────────────┐  │
│   │  Audio Subsystem │      │  Video & GFX Eng.  │    │   AI Subsystem   │  │
│   │ • sounddevice    │      │ • PyAV (CFR Decode)│    │ • DeepFilterNet3 │  │
│   │ • Pedalboard(C++)│      │ • ModernGL Shaders │    │ • MossFormer2    │  │
│   │ • SciPy/Numba DSP│      │ • HarfBuzz / Skia  │    │ • Whisper Quran  │  │
│   │ • Partitioned IR │      │ • Particle Engine  │    │ • MediaPipe/Depth│  │
│   └────────┬─────────┘      └─────────┬──────────┘    └────────┬─────────┘  │
│            │                          │                        │            │
│            └──────────────►┌──────────▼───────────┐◄───────────┘            │
│                            │ Export Worker Process│                         │
│                            │ Raw Pipe -> FFmpeg   │                         │
│                            │ (NVENC/QSV/libx264)  │                         │
│                            └──────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Directory Layout

```text
noor_cinematic_python/
├── pyproject.toml                  # Dependencies, ruff, mypy, pytest
├── .env.example                    # Optional GEMINI_API_KEY / HF_TOKEN placeholders
├── assets/
│   ├── fonts/                      # KFGQPC Uthmanic Script Hafs, Amiri Quran, Inter, JetBrains Mono
│   ├── luts/                       # 8 .cube 3D LUTs matching LUTStyle enum
│   ├── impulse_responses/          # Makkah, Madinah, Al-Aqsa, Dome Hall .wav IRs
│   └── quran/                      # Canonical Tanzil Uthmani JSON + CuratedSpiritualAyahs
├── backend/
│   ├── main.py                     # FastAPI + Uvicorn launcher, localhost bearer auth, WS hub
│   ├── schemas/
│   │   ├── studio_state.py         # Pydantic v2 models + NaN/Inf finite guards
│   │   ├── pipeline_dag.py         # Reorderable PipelineNode DAG & cycle validation
│   │   └── export_job.py           # ExportConfig, ExportProgress, MasteryStats
│   ├── audio/
│   │   ├── engine.py               # Golden Order dynamic DSP runner (live & offline)
│   │   ├── biquad_eq.py            # SciPy SOS 6-band EQ, HPF, De-Esser, 50/60Hz Notch, Bass
│   │   ├── acoustics.py            # Partitioned FFT Convolution IR + Freeverb Mosque engine
│   │   ├── dynamics.py             # Pedalboard Compressor/Limiter + Silero-assisted Silence Gate
│   │   ├── analyzer.py             # 48-bin FFT spectrum + pyloudnorm LUFS + Clarity telemetry
│   │   └── recorder.py             # Real 48kHz sounddevice mic capture & monitor routing
│   ├── video/
│   │   ├── decoder.py              # PyAV VFR->CFR frame-accurate decoder + proxy cache
│   │   ├── gl_renderer.py          # ModernGL shader chain (LUT3D, Bokeh, Rays, Bloom, Split)
│   │   ├── calligraphy.py          # Libraqm/HarfBuzz/Skia Uthmani Arabic + frosted card + waveform
│   │   └── exporter.py             # Process-isolated rawvideo+WAV pipe -> FFmpeg NVENC/libx264
│   ├── ai/
│   │   ├── speech_enhance.py       # DeepFilterNet3 (live 48kHz) + ClearerVoice MossFormer2 (offline)
│   │   ├── quran_aligner.py        # tarteel-ai/whisper-base-ar-quran + RapidFuzz Mushaf + WhisperX
│   │   ├── face_depth.py           # MediaPipe Face Landmarker + Depth-Anything-V2 / MODNet bokeh
│   │   └── creative_copilot.py     # Gemini / Ollama structured Hook, Tafsir & Mood-to-Preset
│   ├── storage/
│   │   ├── database.py             # SQLAlchemy 2.0 async SQLite WAL engine
│   │   ├── models.py               # PresetORM, MasteryProgressORM, ExportHistoryORM
│   │   └── seed_presets.py         # 8 Official Presets + 4 Atmospheres + 5 Masterclass Lessons
│   └── api/
│       ├── routes_project.py       # Media import, seek, trim, .noorproj save/load
│       ├── routes_dsp.py           # Parameter patches, Pipeline DAG reorder, Recorder control
│       ├── routes_presets.py       # Preset CRUD, Reset, Mastery XP
│       ├── routes_ai.py            # Auto Ayah align, AI denoise pass, Copilot assist
│       └── routes_export.py        # Start / Cancel / Progress / Output open
└── gui/
    ├── app.py                      # PySide6 QApplication, Obsidian & Signal Blue QSS, RTL/LTR
    ├── state_client.py             # Async HTTP + WebSocket + SharedMem consumer
    ├── widgets/
    │   ├── header_bar.py           # Brand, Media dropdown, Lang toggle, Export button
    │   ├── gl_viewport.py          # QOpenGLWidget + interactive reticle, bounding boxes, safe zones
    │   ├── spectrum_visualizer.py  # 60fps QPainter 48-bin spectrum + 6-band EQ overlay
    │   ├── panels/                 # video_panel.py, audio_panel.py, viral_panel.py, presets_panel.py, pipeline_panel.py
    │   └── modals/                 # export_modal.py, recorder_modal.py, contemplation_modal.py, knowledge_modal.py, dashboard_modal.py, version_modal.py
    └── resources/                  # SVG icons, ar.json/en.json i18n, obsidian_signal.qss
```

---

## 4. Canonical Data Contracts (Pydantic v2 / JSON)

All enums and parameter bounds map 1:1 to `com.example.model.StudioModels.kt` and `PresetsData.kt` with strict finite-float validators (`math.isfinite`):

1. **`LUTStyle` (8):** `kadyrov_gold`, `royal_dark`, `makkah_sunrise`, `madina_emerald`, `dawn_spiritual`, `vintage_film`, `pure_mushaf`, `dramatic_monochrome`.
2. **`MosqueAcousticSpace` (5):** `haram_makkah` (8.5s), `prophet_madina` (5.2s), `alaqsa` (6.0s), `pro_studio` (dry), `dome_hall` (9.0s).
3. **`CapCutNoiseMode` (4):** `off`, `standard`, `pro_clean`, `extreme`.
4. **`CapCutDeepBassMode` (4):** `off`, `warm`, `capcut_pro`, `kadyrov_elite`.
5. **`MobileMicCalibrationMode` (4):** `studio_neumann`, `broadcast_shure`, `smooth_warm`, `raw_calibrated`.
6. **`QuranTypographyStyle` (4):** `uthmani_gold`, `pure_white`, `royal_emerald`, `amber_glow`.
7. **`WaveformStyle` (4):** `solid`, `glass_modern`, `glass_bars`, `vintage_dots`.
8. **`AspectRatio` (4):** `9:16`, `1:1`, `16:9`, `4:5`.
9. **`SplitMode` (4):** `split`, `filtered`, `original`, `side-by-side`.
10. **`SpiritualAtmosphere` (4):** `sakina_dawn`, `jalal_majesty`, `rajaa_hope`, `tahajjud_solitude`.
11. **`OfficialStudioPresets` (8):** `kadyrov_master`, `capcut_pro_elite`, `kadyrov_elite_bass`, `podcast_serat_sawy`, `viral_islam_sobhi`, `viral_hazza_albalushi`, `grand_mosque_haram`, `pro_studio_master`.

---

## 5. Recommended Python Libraries Stack

| Layer | Libraries | Technical Justification |
| :--- | :--- | :--- |
| **Desktop GUI** | `PySide6` + `qasync` | Native C++ Qt6 speed, automatic RTL layout mirroring (`Qt.LayoutDirection.RightToLeft`), `QOpenGLWidget` zero-copy GPU viewport, spring animations via `QPropertyAnimation`. *(Optional Web shell: `Tauri + React` consuming the same FastAPI server).* |
| **Audio I/O** | `sounddevice` + `soundfile` | Direct `float32` NumPy callback over PortAudio (ASIO/WASAPI/CoreAudio/ALSA) for `< 15 ms` live monitoring & 24-bit WAV capture. |
| **Audio DSP** | `pedalboard` (Spotify C++/JUCE) + `scipy.signal` + `numba` + `pyloudnorm` | `pedalboard` runs Reverb, Convolution, Compressor, Limiter, Chorus, Delay, and Filters in C++ releasing the GIL; `scipy.signal.sosfilt` guarantees numerically stable biquad cascades; `pyloudnorm` measures ITU-R BS.1770 LUFS. |
| **Video Decode & Export** | `PyAV` (`av`) + `FFmpeg` subprocess pipe | `PyAV` handles frame-accurate seeking and VFR-to-CFR normalization; piping rendered frames + mastered audio to `FFmpeg` enables `h264_nvenc`, `h264_videotoolbox`, `h264_qsv`, and `libx264` with zero frame drops. |
| **GPU Video FX** | `ModernGL` + `OpenCV` + `NumPy` | Single GLSL fragment pass applies 3D `.cube` LUT trilinear interpolation, Gaussian bloom, radial God Rays, depth bokeh blur, vignette, film grain, and interactive split wipe in `< 2 ms` per 1080p frame. |
| **Uthmani Arabic Typography** | `Pillow` (`libraqm` / HarfBuzz + FriBiDi) OR `skia-python` + `uharfbuzz` | Preserves OpenType `GPOS` anchor positioning so *Tashkeel/Harakat* and *Waqf* marks never collide or detach from base Arabic glyphs. |
| **Backend API & DB** | `FastAPI` + `Uvicorn` + `Pydantic v2` + `SQLAlchemy 2.0` + `aiosqlite` + `Alembic` | Typed REST + WebSocket telemetry (`ws://`), strict schema & finite-number enforcement, and ACID SQLite WAL persistence. |

---

## 6. Best AI Models & Hardware Deployment Matrix

| Feature / Gap | Best Local Open-Source Models | Cloud / Hybrid Option | Integration Design |
| :--- | :--- | :--- | :--- |
| **Live & Offline Noise Isolation, Hiss, Hum, Bark Cancel** | **Live 48 kHz:** `DeepFilterNet3` (`deepfilternet`)<br>**Offline Studio Pre-Pass:** `MossFormer2_SE_48K` (`clearvoice` / ClearerVoice-Studio)<br>**Breath-Safe VAD:** `Silero VAD` | Local only (privacy + latency) | `DeepFilterNet3` runs low-latency frame streaming during mic monitoring; `MossFormer2_SE_48K` runs as an optional 1-click "Studio Deep Clean" pass; `Silero VAD` prevents `silenceGate` from cutting soft Tajweed endings. |
| **Spectral De-Reverb (Room Removal)** | `MossFormer2` De-Reverb / `UVR-DeEcho-DeReverb` (MDX-Net) | Local only | Strips home/bedroom boxiness *before* applying clean Makkah/Madinah Impulse Response convolution. |
| **Quran Ayah Detection & Word-Level Karaoke Sync** | **ASR:** `tarteel-ai/whisper-base-ar-quran` (or CTranslate2 `faster-whisper-base-ar-quran`)<br>**Alignment:** `WhisperX` / `Wav2Vec2-Large-XLSR-53-Arabic` | Optional `Gemini` for topic hints only | Transcribe audio → fuzzy-match (`RapidFuzz`) against verified local **Tanzil Uthmani Mushaf JSON** → pull 100% authentic verse + Surah/Ayah/Translation → run forced alignment for word-by-word highlight timing. |
| **Face Tracking, Skin Mask & Depth Bokeh (`bgBlur`)** | **Face Landmarks:** `MediaPipe Face Landmarker` (478 pts)<br>**Bokeh/Matting:** `Depth-Anything-V2-Small` + `MODNet` / `BiRefNet` | Local only | Tracks speaker face `(x, y, radius)` with Kalman/EMA smoothing; restricts `skinSmooth` strictly inside skin polygon (keeping beard/eyes sharp); drives graduated depth-of-field bokeh on background. |
| **Creative Copilot (Hooks, Tafsir, Mood Presets)** | `Qwen2.5-14B-Instruct` or `Llama-3.3-8B` via `Ollama` | `Gemini 2.5 Flash / Pro` | Generates bilingual hooks, concise Tafsir reflections, and mood-to-preset JSON validated by Pydantic bounds. |

### Hardware Tier Matrix

| Tier | Target Machine | Audio AI | Video & Bokeh AI | Export Encoder |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: CPU Laptop** | 8+ Cores, 16 GB RAM | `DeepFilterNet3` (ONNX CPU) + `Pedalboard` | `MediaPipe` CPU + `ModernGL` iGPU | `libx264` (`faster`) / `h264_qsv` |
| **Tier 2: RTX Workstation** | NVIDIA RTX 3060+ (8+ GB VRAM) | `MossFormer2_SE_48K` + `DeepFilterNet3` + `Pedalboard` | `MediaPipe` + `Depth-Anything-V2` FP16 + `ModernGL` | `h264_nvenc` / `hevc_nvenc` |
| **Tier 3: Apple Silicon** | M1/M2/M3/M4 | `DeepFilterNet3` MPS/CPU + `Pedalboard` | `MediaPipe` + `Depth-Anything-V2` CoreML/MPS | `h264_videotoolbox` |

---

## 7. Engineering Pitfalls & Verification Strategy

1. **VFR-to-CFR Sync:** Mobile clips often use Variable Frame Rate; `PyAV` must resample PTS onto constant frame grid before `ModernGL` and `FFmpeg`.
2. **Uthmani Diacritics Shaping:** Always verify golden PNG renders of complex Quranic glyphs (`ٱلرَّحْمَـٰنِ`, *Waqf* marks, *Alif Khanjariyya*) rendered through `libraqm`/`uharfbuzz`.
3. **Zero Clipping & Zero `NaN`:** All audio DSP paths operate in `float32/float64` with explicit denominator checks and final `-1.0 dBTP` true-peak limiting.
4. **Automated Test Suite (`pytest`):**
   - *Audio DSP:* FFT impulse tests verifying 6-band EQ, HPF, 50/60 Hz notch, and LUFS metering; edge-case tests on silence, clipped `+10 dBFS` bursts, and empty buffers.
   - *Video & Export:* Render 3-second test video at `1080p60` → assert via `ffprobe` (`nb_frames == 180`, `h264`, `yuv420p`, `aac`, `size > 0`).
   - *AI Grounding:* Assert `quran_aligner` never emits raw unverified ASR strings as official Ayahs and always maps to canonical Mushaf IDs.

---

## 8. Prompt-Format Master Specification (All Features Ready to Copy-Paste)

Use the prompt below directly to instruct an engineering agent (or yourself across sprints) to build the entire Python Backend + Desktop GUI cleanly from scratch without missing a single feature:

```markdown
# MASTER BUILD PROMPT: NOOR CINEMATIC STUDIO (PYTHON BACKEND + DESKTOP GUI)

Build a production-grade, local-first desktop application called **"Noor Cinematic Studio"** using a cleanly decoupled **Python Backend (`FastAPI` + `Uvicorn` + `WebSockets` + `Pydantic v2` + `SQLAlchemy` SQLite WAL)** and a **Native Desktop GUI (`PySide6` / Qt 6 + `QOpenGLWidget`)**.

## ARCHITECTURAL RULES (NON-NEGOTIABLE)
1. **Strict Decoupling:** All media decoding, audio DSP, AI inference, shader rendering, database persistence, and FFmpeg exporting live strictly inside `backend/`. The `gui/` layer communicates exclusively via authenticated localhost REST (`http://127.0.0.1:<port>`) + WebSocket telemetry (`ws://`) + shared-memory frame buffers (`mmap`) for 60 FPS preview.
2. **No Toy/Stub Implementations:** Every slider, toggle, preset, AI model hook, recorder button, pipeline node, and export mode must execute real signal processing, GPU shaders, hardware audio capture, or FFmpeg encoding.
3. **Numerical & Sacred-Text Safety:** Guard every numerical boundary against `NaN`/`Inf`/divide-by-zero. Never let an LLM or ASR model output unverified Quranic text—always resolve Ayahs against a local canonical Tanzil Uthmani Mushaf JSON database.
4. **Bilingual RTL/LTR & Obsidian Design System:** Support instant runtime switching between **Arabic (RTL default)** and **English (LTR)** with Apple-inspired Obsidian & Signal Blue dark styling, high contrast (`>= 4.5:1`), NLE keyboard shortcuts (`Space`, `J/K/L`, `I/O`, `Ctrl/Cmd+E`), and dual-perspective **Smart Info Tooltips (`ℹ️`)** explaining both (a) Simple User Benefit and (b) Under-the-Hood Engineering Algorithm.

---

## COMPLETE REQUIRED FEATURE CHECKLIST (IMPLEMENT 100%)

### MODULE 1: Media Ingestion, Timeline & Multi-Mode Viewport
- [ ] **File Import:** Video (`MP4/MOV/MKV/WEBM` via `PyAV` with VFR-to-CFR normalization), Audio (`WAV/MP3/FLAC/M4A/AAC`), and Background Image plates (`PNG/JPG/WEBP`), plus built-in procedural Mosque/Reciter demo mode + synthesized harmonic reciter sample when no file is loaded.
- [ ] **Project Files:** Save and load portable `.noorproj` JSON manifests containing media paths, trim range, active preset/settings, and custom pipeline DAG order.
- [ ] **4 Viewport Split Modes:**
  - `SPLIT`: Interactive horizontal wipe slider (`0.02..0.98`) comparing Raw vs. Graded live.
  - `FILTERED`: Full processed output.
  - `ORIGINAL`: Raw bypass.
  - `SIDE_BY_SIDE`: Dual 2-Up synchronized frame comparison.
- [ ] **Direct Manipulation & Safe Zones:**
  - Hold-to-Compare raw button + Fullscreen Cinema Preview window.
  - Draggable Face Glow spotlight reticle `(faceManualX, faceManualY)`.
  - CapCut-style interactive selection bounding boxes (`AYAH_CARD`, `WAVEFORM`, `HOOK_HEADER`, `FACE_GLOW`) with Y-position drag/nudge/reset.
  - Toggleable **Safe Zone Overlay** (3×3 rule-of-thirds grid + TikTok/Reels top search bar, right engagement rail, and bottom caption exclusion zones).
- [ ] **Timeline & Trim:** Scrubbing slider + `TrimRange` `[start_s, end_s]` enforcement + 1-click Pro Audio HUD toggles (`Zero-Noise`, `Haram Reverb`, `Deep Bass`).

### MODULE 2: Real-Time Studio Voice Recorder
- [ ] **Hardware Capture:** Real `48 kHz / float32` microphone input via `sounddevice` (PortAudio) with input device selector.
- [ ] **Safety & Ergonomics:** Anti-feedback wired-headphone safety alert, `3-2-1` pre-roll countdown, live recording timer, real-time Peak/RMS `dBFS` VU meter, and 4 instant live monitor DSP profiles (`NEUMANN`, `HARAM`, `DEEP_BASS`, `RAW`).
- [ ] **Direct Take Commit:** Save take as lossless WAV and load immediately into the studio timeline.

### MODULE 3: "Golden Order" Quranic Audio DSP Engine & Live Visualizer
- [ ] **Execution Engine:** Process stereo `float32` PCM via `pedalboard` (Spotify C++/JUCE) + `scipy.signal.sosfilt` + `numba` + `pyloudnorm` with `< 15 ms` monitor latency.
- [ ] **Complete DSP Stages (All Exposed & Functional):**
  1. Pre-Amp Gain (`0.5x–4.0x`).
  2. Noise Isolation & Restoration: `CapCutNoiseMode` (`off`, `standard`, `pro_clean`, `extreme`), `capcutNoiseReduction`, `capcutHissRemover`, `capcutHumRemover` (50/60 Hz Notch), `dogBarkNoiseCanceler`, `micAirFilter` (HPF `40–75 Hz`), `spectralDeReverb` (`420 Hz` boxiness cut + AI de-reverb), powered by `DeepFilterNet3` (live) and `MossFormer2_SE_48K` (studio offline pass).
  3. Breath-Aware Silence Gate (`silenceGateEnabled`, `silenceGateThreshold -60..-20 dB`) assisted by `Silero VAD` to protect soft Tajweed tails.
  4. Split-Band De-Esser (`6.8 kHz`, `deEsserSensitivity 0–100%`).
  5. Mic Calibration (`studio_neumann`, `broadcast_shure`, `smooth_warm`, `raw_calibrated`) + `vocalClarityBooster` (`2.8–3.6 kHz`).
  6. Deep Bass Sub/Chest Exciter (`CapCutDeepBassMode`: `off`, `warm`, `capcut_pro`, `kadyrov_elite`, plus `deepBass`, `deepBassSub 65 Hz`, `deepBassChest 135 Hz`, `deepBassDrive`).
  7. 6-Band Parametric Reciter EQ (`80 Hz` LowShelf, `120 Hz`, `250 Hz`, `2500 Hz`, `5000 Hz`, `10000 Hz` HighShelf; `-12..+12 dB`).
  8. RMS Vocal Compressor (`compressorEnabled`, `compressorThreshold`, `compressorRatio`).
  9. Warm Harmonics (`tanh` tube saturation) & Double-Voice Chorus (`24 ms` modulated delay).
  10. Circular Tape Echo (`echoEnabled`, `echoTime 50–800 ms`, `echoFeedback 0–90%`, `echoLevel`).
  11. Mosque Acoustic Space (`haram_makkah` 8.5s, `prophet_madina` 5.2s, `alaqsa` 6.0s, `pro_studio` dry, `dome_hall` 9.0s) using real partitioned FFT Impulse Response convolution + algorithmic Freeverb fallback (`roomSize`, `wet`, `dry`, `decay`, `preDelay`, `mosqueAmbience`).
  12. M/S Stereo Width (`0–100%`), Master Volume (`0–150%`), and True-Peak Brickwall Limiter (`-1.0 dBTP`).
- [ ] **Live Analyzer (`AudioVisualizer`):** 60 FPS `QPainter` 48-bin FFT frequency spectrum, overlaid 6-band logarithmic EQ curve, and real-time ITU-R BS.1770 LUFS (`Momentary`, `Integrated`, `True Peak`) + Clarity score telemetry.

### MODULE 4: GPU Video FX, Face AI & Optics (`ModernGL` Shaders)
- [ ] **8 3D `.cube` LUT Styles + Custom `.cube` Import:** `KADYROV_GOLD`, `ROYAL_DARK`, `MAKKAH_SUNRISE`, `MADINA_EMERALD`, `DAWN_SPIRITUAL`, `VINTAGE_FILM`, `PURE_MUSHAF`, `DRAMATIC_MONOCHROME` + `lutIntensity` (`0–100%`).
- [ ] **Color Balance:** `warmth (-50..100%)`, `contrast (-50..100%)`, `dynamicExposure (-50..100%)`, `saturation (-50..100%)`.
- [ ] **Face AI & Portrait Enhancement:** Automatic `MediaPipe Face Landmarker` per-frame tracking with EMA/Kalman smoothing (plus manual reticle override), `faceGlow`, `skinSmooth` (confined strictly to skin mask preserving eyes/beard sharpness), `sharpen`.
- [ ] **Optics & True Depth Bokeh:** True foreground/background bokeh (`bgBlur`) driven by `Depth-Anything-V2-Small` / `MODNet` alpha matting, plus `lightRays` (radial God Rays), `bloom`, `filmGrain`, and `vignette`.

### MODULE 5: Viral Social & Authentic Uthmani Arabic Calligraphy Toolkit
- [ ] **Aspect Ratios:** `9:16` (TikTok/Reels/Shorts), `1:1` (Square), `16:9` (YouTube), `4:5` (Portrait Feed).
- [ ] **Perfect Arabic Shaping:** Render Uthmani script via `Pillow + libraqm` (HarfBuzz + FriBiDi) or `skia-python + uharfbuzz` so *Tashkeel/Harakat* and *Waqf* marks never break or overlap.
- [ ] **Overlay Elements:**
  - Toggleable Top Viral Hook pill banner + 8 `ViralTrendHooksList` presets + Y-pos & font size.
  - Curated Spiritual Ayah Sanctuary Carousel (8 curated inspirations with Maqam & Tafsir) + Searchable full canonical Tanzil Mushaf picker.
  - Editable Arabic Ayah, English Translation, Surah Name, Ayah Number, Reciter Watermark; 4 `QuranTypographyStyle` themes (`UTHMANI_GOLD`, `PURE_WHITE`, `ROYAL_EMERALD`, `AMBER_GLOW`), `cardBackdropBlur`, `cardOpacity`, `textShadowGlow`, `ayahPositionY`.
  - Reactive Audio Waveform (`gold`, `emerald`, `white`) supporting all 4 `WaveformStyle` renderers (`SOLID`, `GLASS_MODERN`, `GLASS_BARS`, `VINTAGE_DOTS`), height, and Y-pos.
  - Atmospheric Shaders: `goldenDustParticles`, `godRaysSunbeams`, `cinematicRain`.
- [ ] **AI Auto-Ayah & Karaoke Sync:** `tarteel-ai/whisper-base-ar-quran` (`faster-whisper`) + `RapidFuzz` canonical Mushaf verification + `WhisperX` word-level timestamps for optional word-by-word highlight synced to audio.

### MODULE 6: Executable Dynamic Effect Pipeline DAG
- [ ] **Live Execution Graph:** Interactive horizontal node-and-arrow graph across `AUDIO`, `VIDEO`, and `OVERLAY` categories with Active-Only filter, Total/Active/Measured-Latency KPI strip, node inspection, left/right reordering, bypass toggles, and jump-to-tab.
- [ ] **Real Engine Binding:** Reordering or bypassing nodes in the Pipeline tab must dynamically recompile the execution order in `audio/engine.py` and `video/gl_renderer.py`.

### MODULE 7: Presets Vault, Spiritual Journey & Mastery Modals
- [ ] **8 Official Master Presets (Seeded & Immutable) + Custom CRUD:** Seed `kadyrov_master`, `capcut_pro_elite`, `kadyrov_elite_bass`, `podcast_serat_sawy`, `viral_islam_sobhi`, `viral_hazza_albalushi`, `grand_mosque_haram`, and `pro_studio_master`. Support Save, Update, Duplicate, Delete, Export/Import `.noorpreset`, and Reset Defaults in SQLite (`SQLAlchemy`).
- [ ] **Guided Spiritual Journey Banner:** Collapsible 4-station workflow (`Intention & Atmosphere` → `Sacred Acoustics` → `Ayah & Calligraphy` → `Contemplation & Export`) + 4 1-click `SpiritualAtmosphere` presets (`SAKINA_DAWN`, `JALAL_MAJESTY`, `RAJAA_HOPE`, `TAHAJJUD_SOLITUDE`).
- [ ] **Contemplation Sanctuary (`ContemplationModeDialog` / محراب التدبر):** Fullscreen breathing-animated sanctuary view with live graded background, Ayah card, 28-bar reactive wave, play/pause, and export jump.
- [ ] **Sacred Acoustic Masterclass (`SpiritualKnowledgeModal`):** Searchable, category-filtered modal with 5 deep Quranic acoustic/visual lessons + 1-click navigation hints.
- [ ] **Transformation & Mastery Dashboard (`TransformationDashboardModal`):** Persisted streak counter, XP (+150 XP per completed export), completed exports count, 3 mastery pillars, and 5 unlockable badges.
- [ ] **AI Creative Copilot:** Integrated assistant (`Gemini` via `.env` OR local `Ollama Qwen2.5-14B`) that suggests viral hooks, concise Tafsir reflections, and mood-to-preset JSON patches.
- [ ] **Version & Changelog Modal:** Displays version history and feature badges.

### MODULE 8: Deterministic Pipelined Export Engine
- [ ] **Export Targets:**
  - **Video:** `MP4` (`H.264` / `HEVC` via `h264_nvenc`, `h264_videotoolbox`, `h264_qsv`, or `libx264` + `AAC 192–320 kbps`) at `4K (2160p)`, `1080p`, `720p`; `60 / 30 / 24 FPS`; Bitrate tiers (`ULTRA 16 Mbps`, `VIRAL 8 Mbps`, `LIGHT 4 Mbps`).
  - **Audio:** `Stereo 44.1/48 kHz 16/24-bit WAV`, `MP3 320 kbps`, and `FLAC`.
  - **Cover Image:** High-res graded `PNG` snapshot with overlays.
- [ ] **Pipeline Safety:** Frame-by-frame deterministic generator piped directly to `FFmpeg` `stdin` + muxed mastered WAV. Display progress %, current stage, real-time FPS & ETA, safe cancel (`SIGTERM` + temp cleanup), retry on failure, and post-export XP reward + "Open Output Folder".

### ACCEPTANCE & VERIFICATION GATES (MUST PASS BEFORE COMPLETION)
1. Run `pytest` covering:
   - Audio DSP FFT impulse tests (verifying all 6 EQ bands, HPF, 50/60 Hz notch, LUFS compliance, and zero `NaN`/`Inf` on edge-case buffers).
   - Deterministic 3-second `1080p60` MP4 export verified via `ffprobe` (`nb_frames == 180`, valid `h264` + `aac`, non-zero size).
   - Arabic Uthmani calligraphy golden render check confirming intact Harakat/Tashkeel shaping.
   - AI Mushaf grounding test verifying recognized verses always resolve to valid canonical Surah:Ayah IDs.
2. Launch `noor_backend` + `noor_gui`, verify live audio playback/spectrum telemetry, viewport split wipe, preset switching, pipeline reordering, and full MP4/WAV/PNG export end-to-end.
```


Yes — **`https://github.com/OpenMontageInc/OpenMontage` is a massive head start** for Noor Cinematic Studio, **as long as you understand one key architectural boundary** before you start coding.

---

### 1. Ground Truth: What `OpenMontage` Gives You vs. What You Must Add

`OpenMontage` (`AGPL-3.0`, Python 3.10+ / Node.js 22+ / FFmpeg) is an **agent-orchestrated video production framework**. It already ships:
* **Auto-discovered Tool Runtime:** 181+ `BaseTool` modules in `tools/` discovered automatically by `tools/tool_registry.py` (`tools/audio/`, `tools/enhancement/`, `tools/analysis/`, `tools/video/`, `tools/subtitle/`, `tools/publishers/`).
* **Existing Baseline Media Tools:** `audio_enhance`, `audio_mixer`, `color_grade`, `face_enhance`, `face_restore`, `eye_enhance`, `bg_remove`, `upscale`, `transcriber` (`faster-whisper`), `scene_detect`, `frame_sampler`, `video_compose`, `video_stitch`, `video_trimmer`, `auto_reframe`, `silence_cutter`.
* **3 Render Engines:** `Remotion` (`remotion-composer/`), `HyperFrames` (HTML/CSS/GSAP via `npx hyperframes`), and `FFmpeg`.
* **YAML Pipelines, Playbooks & Live Board:** `pipeline_defs/*.yaml`, `styles/*.yaml`, `schemas/artifacts/*.json`, `lib/checkpoint.py`, and **`backlot/`** (a FastAPI + SSE local storyboard viewer on `127.0.0.1:4750`).

#### The Key Architectural Gap (Crucial!)
In upstream OpenMontage:
1. **There is no Python orchestrator or interactive NLE GUI** — the AI coding assistant (Claude/Cursor/Codex) drives batch stages via Markdown skills, and `backlot/` is **read-only**.
2. **Real-time workstation features** from your Noor spec — `< 15 ms` `sounddevice` live mic monitoring, 60 FPS interactive `SPLIT` wipe (`0.02..0.98`), draggable Face Glow reticle, 60 Hz FFT spectrum + LUFS meter, executable Pipeline DAG reordering, Contemplation Sanctuary (`محراب التدبر`), and standalone non-coding-agent usage — **do not exist in OpenMontage**.

**The Solution (Dual-Mode Architecture):**  
Build Noor's core engines as **OpenMontage-compliant `BaseTool` plugins + a new `noor-quranic-cinematic` pipeline + `styles/` playbooks + Remotion/HyperFrames templates**, and layer a **`noor_studio/` Interactive Workstation (FastAPI + PySide6 `QOpenGLWidget`)** on top of the exact same `lib/noor/` DSP & shader engines. That way:
* Coding agents can run Noor headlessly through OpenMontage's native pipeline (`AGENT_GUIDE.md` compliant).
* Creators get the full standalone real-time desktop studio GUI (`noor_studio/`).

> **License Note:** `OpenMontageInc/OpenMontage` uses **GNU AGPL-3.0**. If you fork/modify it and distribute it or run it as a hosted web service, you must comply with AGPL-3.0 source disclosure obligations.

---

### 2. Complete Feature-to-OpenMontage Mapping (All 8 Modules)

| Noor Module | What OpenMontage Already Has | What You Build / Extend Inside OpenMontage |
| :--- | :--- | :--- |
| **1. Shell, Viewport & Projects** | `projects/<id>/` workspace + `backlot/` read-only FastAPI board | Add `noor_studio/` (FastAPI + WebSocket + PySide6 `QOpenGLWidget`) with `SPLIT`/`FILTERED`/`ORIGINAL`/`SIDE_BY_SIDE`, Hold-to-Compare, Fullscreen, draggable reticle & bounding boxes, Safe Zones (3×3 + TikTok/Reels), RTL/LTR Arabic/English, `.noorproj` import/export, and `PyAV` VFR→CFR decoding. |
| **2. Studio Voice Recorder** | `tools/capture/` (screen capture only) | Add `tools/audio/noor_mic_recorder.py` (`BaseTool`) + real-time `48 kHz float32` `sounddevice` engine in `lib/noor/recorder.py` with wired-headphone alert, `3-2-1` countdown, dBFS VU meter, and 4 live DSP monitor profiles (`NEUMANN`, `HARAM`, `DEEP_BASS`, `RAW`). |
| **3. "Golden Order" Audio DSP & Analyzer** | `tools/audio/audio_enhance.py` (FFmpeg EQ/loudnorm) & `audio_mixer.py` | Build `lib/noor/audio_dsp.py` (`pedalboard` C++ + `scipy.signal.sosfilt` + `numba` + `pyloudnorm`) + `tools/audio/noor_audio_master.py` (`BaseTool`). Includes Pre-Amp, 50/60 Hz Notch, Hiss/De-Reverb, `DeepFilterNet3` + `MossFormer2_SE_48K`, `Silero VAD` Silence Gate, 6.8 kHz De-Esser, 4 Mic Calibrations, Deep Bass (`65/135 Hz`), 6-Band EQ, Compressor, Tube `tanh`, 24 ms Chorus, Tape Echo, 5 Mosque IR Convolutions + Freeverb, M/S Width, `-1.0 dBTP` Limiter, and 48-bin FFT + LUFS stream. |
| **4. GPU Video FX, Face AI & Depth Bokeh** | `tools/enhancement/color_grade.py`, `face_enhance.py`, `bg_remove.py` | Build `lib/noor/gl_renderer.py` (`ModernGL` shaders) + `tools/enhancement/noor_video_fx.py` (`BaseTool`). Adds 8 `.cube` LUTs + custom `.cube`, warmth/contrast/exposure/saturation, `MediaPipe` 478-pt face tracking + skin-polygon smoothing, `Depth-Anything-V2-Small` / `MODNet` true `bgBlur` bokeh, God rays, bloom, film grain, vignette. |
| **5. Viral Social, Uthmani Calligraphy & Auto-Ayah** | `tools/subtitle/subtitle_gen.py`, `remotion-composer/`, `HyperFrames` | Add `tools/analysis/quran_ayah_aligner.py` (`tarteel-ai/whisper-base-ar-quran` + `RapidFuzz` canonical Tanzil JSON + `WhisperX` word timestamps). Build Uthmani renderer via `Pillow+libraqm` / `skia+uharfbuzz` **plus** `remotion-composer/src/NoorQuranReel.tsx` and HyperFrames template (`dir="rtl"` + KFGQPC Hafs font) for 4 aspect ratios, 4 typography themes, 4 waveform styles, viral hooks, and dust/rays/rain FX. |
| **6. Executable Effect Pipeline DAG** | Declarative `pipeline_defs/*.yaml` | Add `lib/noor/pipeline_dag.py` so reordering/bypassing `AUDIO`/`VIDEO`/`OVERLAY` nodes in the GUI dynamically rewires `audio_dsp.py` and `gl_renderer.py` and measures real per-node `ms` latency. |
| **7. Presets Vault, Sanctuary, XP & Copilot** | `styles/*.yaml` (`playbook.schema.json`) + agent LLM | Seed 8 Official Presets & 4 Atmospheres as `styles/noor-*.yaml` + SQLite WAL (`lib/noor/store.py`) for custom presets, `.noorpreset` import/export, XP (`+150/export`), streaks, and badges. Add Contemplation Sanctuary (`محراب التدبر`), Knowledge Masterclass, Version modal, and standalone Copilot (`Gemini`/`Ollama`) inside `noor_studio/`. |
| **8. Deterministic Pipelined Export** | `lib/media_profiles.py`, `video_compose.py`, `tools/publishers/` | Extend `lib/media_profiles.py` with Noor `4K/1080p/720p @ 60/30/24 FPS` & `ULTRA/VIRAL/LIGHT` profiles. Build `tools/publishers/noor_export.py` (`BaseTool`) + streaming `FFmpeg` pipe (`h264_nvenc`, `h264_videotoolbox`, `h264_qsv`, `libx264`), plus `WAV`/`MP3 320`/`FLAC` and `PNG` cover exports with real-time FPS/ETA & clean `SIGTERM` cancel. |

---

### 3. Target Repository Layout Inside OpenMontage

Keep OpenMontage's existing structure intact and plug Noor cleanly into its extension points (`lib/`, `tools/`, `pipeline_defs/`, `styles/`, `schemas/`, `skills/`, `remotion-composer/`, `tests/`) plus the new `noor_studio/` workstation app:

```text
OpenMontage/
├── assets/
│   └── noor/
│       ├── fonts/                    # KFGQPC Uthmanic Script Hafs, Amiri Quran, Inter, JetBrains Mono
│       ├── luts/                     # 8 .cube LUTs (kadyrov_gold ... dramatic_monochrome)
│       ├── impulse_responses/        # makkah.wav, madinah.wav, alaqsa.wav, dome_hall.wav
│       └── quran/                    # Canonical Tanzil Uthmani JSON + 8 CuratedSpiritualAyahs
├── lib/
│   ├── media_profiles.py             # [EXTEND] Add Noor 4K/1080p/720p 60fps & bitrate tier profiles
│   └── noor/                         # [NEW] Pure engine & persistence layer (used by tools AND GUI)
│       ├── schemas.py                # Pydantic v2 models + math.isfinite() guards
│       ├── storage.py                # SQLAlchemy 2.0 SQLite WAL (presets, XP, streaks, history)
│       ├── mushaf_store.py           # Canonical Tanzil index + RapidFuzz verifier (zero hallucination)
│       ├── audio_dsp.py              # "Golden Order" engine (Pedalboard, SciPy SOS, IR, LUFS/FFT)
│       ├── recorder.py               # Real 48kHz sounddevice mic capture + live DSP monitor
│       ├── video_decoder.py          # PyAV VFR->CFR decoder + preview frame cache
│       ├── gl_renderer.py            # ModernGL fragment pipeline (LUT3D, bokeh, rays, split wipe)
│       ├── calligraphy.py            # libraqm/uharfbuzz Uthmani shaping + waveforms + safe zones
│       ├── pipeline_dag.py           # Dynamic reorderable AUDIO/VIDEO/OVERLAY graph compiler
│       └── exporter.py               # Process-isolated rawvideo+WAV pipe -> FFmpeg NVENC/libx264
├── tools/
│   ├── audio/
│   │   ├── noor_audio_master.py      # [NEW BaseTool] Wraps lib/noor/audio_dsp.py + DeepFilterNet/MossFormer2
│   │   └── noor_mic_recorder.py      # [NEW BaseTool] Wraps lib/noor/recorder.py
│   ├── enhancement/
│   │   ├── noor_video_fx.py          # [NEW BaseTool] Wraps ModernGL LUT/FX + MediaPipe + Depth-Anything-V2
│   ├── analysis/
│   │   └── quran_ayah_aligner.py     # [NEW BaseTool] Whisper Quran + Mushaf lock + WhisperX word sync
│   ├── graphics/
│   │   └── uthmani_overlay.py        # [NEW BaseTool] Renders Arabic cards, hooks, waveforms, particles
│   └── publishers/
│       └── noor_export.py            # [NEW BaseTool] MP4 / WAV / MP3 / FLAC / PNG deterministic export
├── pipeline_defs/
│   └── noor-quranic-cinematic.yaml   # [NEW] 8-stage agentic pipeline manifest
├── styles/
│   └── noor/                         # [NEW] 8 Official Presets + 4 Spiritual Atmospheres (YAML)
├── schemas/artifacts/
│   └── noor_*.schema.json            # [NEW] JSON Schemas for Quranic alignment, DSP config, presets
├── skills/
│   ├── pipelines/noor-quranic-cinematic/  # [NEW] 7 stage-director skills (idea -> publish)
│   └── creative/quranic-cinematic.md      # [NEW] Tajweed preservation & Uthmani visual rules
├── remotion-composer/src/
│   └── NoorQuranReel.tsx             # [NEW] Optional React composition for agentic Remotion runs
├── noor_studio/                      # [NEW] Standalone Interactive Workstation (FastAPI + PySide6 GUI)
│   ├── server.py                     # FastAPI daemon (bearer auth, WS 60Hz telemetry, mmap frames)
│   ├── copilot.py                    # Standalone Gemini / Ollama creative copilot
│   └── gui/                          # PySide6 Obsidian & Signal Blue workstation (RTL/LTR, all modals)
└── tests/
    ├── contracts/test_noor_tools.py  # OpenMontage BaseTool & registry contract tests
    └── qa/test_noor_*.py             # FFT impulse, Uthmani shaping, Mushaf lock, ffprobe 1080p60
```

---

### 4. Step-by-Step Build Plan (6 Sprints with Hard Verification Gates)

#### Sprint 0: Fork, Baseline Setup & Asset Preparation
1. Clone & set up OpenMontage and verify its baseline environment:
   ```bash
   git clone https://github.com/OpenMontageInc/OpenMontage.git noor-openmontage
   cd noor-openmontage
   make setup
   python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.provider_menu_summary(), indent=2))"
   ```
   *(On Windows without `make`, follow OpenMontage's PowerShell venv + `requirements.txt` + `remotion-composer` `npm install` steps).*
2. Add optional Noor dependencies into a new `requirements-noor.txt` (do **not** break `requirements.txt`!):
   * `pedalboard`, `scipy`, `numba`, `pyloudnorm`, `sounddevice`, `soundfile`
   * `av`, `moderngl`, `opencv-python-headless`, `pillow` (built with `libraqm`), `uharfbuzz`
   * `sqlalchemy`, `aiosqlite`, `alembic`, `PySide6`, `qasync`, `pytest-qt`
   * AI tier: `deepfilternet`, `faster-whisper`, `rapidfuzz`, `mediapipe`, `transformers`, `torch` (or `requirements-gpu.txt`)
3. Populate `assets/noor/` with Uthmani fonts, the 8 `.cube` LUTs, the 4 Mosque `.wav` Impulse Responses, and the verified Tanzil Uthmani JSON.
4. Save your full spec as `docs/NOOR_MASTER_SPEC.md`.

---

#### Sprint 1: Data Contracts, Canonical Mushaf, SQLite Vault & Playbooks
**Goal:** Establish 100% strict contracts before touching DSP or UI.
1. **`lib/noor/schemas.py`**: Implement Pydantic v2 models for all 11 enums (`LUTStyle`, `MosqueAcousticSpace`, `CapCutNoiseMode`, `CapCutDeepBassMode`, `MobileMicCalibrationMode`, `QuranTypographyStyle`, `WaveformStyle`, `AspectRatio`, `SplitMode`, `SpiritualAtmosphere`, `OfficialStudioPresets`) and all parameter bounds with `math.isfinite()` validators.
2. **`lib/noor/mushaf_store.py`**: Load Tanzil Uthmani JSON into an indexed lookup structure + `RapidFuzz` matcher returning exact `(surah_id, ayah_id, uthmani_text, translation)`.
3. **`lib/noor/storage.py`**: Async SQLite WAL (`SQLAlchemy 2.0` + `aiosqlite`) storing custom presets, `.noorpreset` import/export, `.noorproj` manifests, streak count, XP (`+150` per export), badges, and export history. Seed all **8 Official Presets**, **4 Spiritual Atmospheres**, and **5 Acoustic Lessons**.
4. **`styles/noor/*.yaml`**: Mirror the 8 presets and 4 atmospheres into OpenMontage playbooks validated against `schemas/styles/playbook.schema.json`.
* **Gate 1:** `pytest tests/noor/test_schemas_and_storage.py` passes (bounds, `NaN`/`Inf` rejection, preset reset, Mushaf lookup).

---

#### Sprint 2: "Golden Order" Audio DSP, Live Recorder & AI Speech Restoration
**Goal:** Real `< 15 ms` audio mastering + OpenMontage `BaseTool` integration.
1. **`lib/noor/audio_dsp.py`**: Implement the reorderable, bypassable chain in `float32`:
   * Pre-Amp (`0.5x–4.0x`) → 50/60 Hz Notch + Hiss + `420 Hz` De-Reverb + HPF (`40–75 Hz`) → Breath-safe Silence Gate (`-60..-20 dB` + `Silero VAD`) → Split-Band De-Esser (`6.8 kHz`) → Mic Calibration (`4 modes` + `2.8–3.6 kHz` clarity) → Deep Bass (`65 Hz` sub, `135 Hz` chest, soft-clip drive) → 6-Band Parametric EQ (`80/120/250/2500/5000/10000 Hz`, `±12 dB`) → RMS Compressor → Tube `tanh` + `24 ms` Chorus → Circular Tape Echo (`50–800 ms`, `0–90%`) → Mosque IR Convolution (real `.wav` IRs + Freeverb fallback) → M/S Stereo Width → Master Volume + `-1.0 dBTP` True-Peak Limiter.
   * Built-in `analyzer` computing 48-bin FFT + ITU-R BS.1770 LUFS (`pyloudnorm`) + Clarity score, plus 12s synthesized harmonic+vibrato offline demo reciter cache.
2. **`lib/noor/recorder.py`**: Real `48 kHz` `sounddevice` input stream with live DSP monitor routing (`NEUMANN`, `HARAM`, `DEEP_BASS`, `RAW`) and WAV commit.
3. **AI Speech (`lib/noor/speech_ai.py`)**: `DeepFilterNet3` for live streaming denoising; `MossFormer2_SE_48K` for optional "Studio Deep Clean" offline pass.
4. **OpenMontage Tools**: Wrap into `tools/audio/noor_audio_master.py` and `tools/audio/noor_mic_recorder.py` inheriting from `tools/base_tool.py` (`BaseTool`).
* **Gate 2:** `pytest tests/contracts/` passes (OpenMontage `ToolRegistry` discovers both tools cleanly) + `pytest tests/qa/test_noor_audio_dsp.py` passes FFT impulse verification on all 6 EQ bands, HPF, 50/60 Hz notch, LUFS targets, and zero `NaN`/`Inf` on silence and `+10 dBFS` bursts.

---

#### Sprint 3: Video Decode, ModernGL Shaders, Face/Depth AI & Uthmani Calligraphy
**Goal:** GPU-accelerated portrait grading, depth bokeh, and unbroken Arabic diacritics.
1. **`lib/noor/video_decoder.py`**: `PyAV` VFR-to-CFR frame-accurate decoder, image plate loader, and procedural mosque/reciter fallback frame generator.
2. **`lib/noor/gl_renderer.py`**: Single-pass/multi-pass `ModernGL` fragment shaders for:
   * 8 trilinear 3D `.cube` LUTs + custom `.cube` + `lutIntensity`
   * Warmth, contrast, dynamic exposure, saturation
   * `SPLIT` (`0.02..0.98`), `FILTERED`, `ORIGINAL`, `SIDE_BY_SIDE`
   * Radial God rays (`lightRays`), Gaussian bloom, film grain, vignette, dust particles, cinematic rain
   * Face Glow spotlight + skin-masked bilateral smoothing + unsharp sharpen + true `bgBlur` bokeh.
3. **`lib/noor/face_depth_ai.py`**: `MediaPipe Face Landmarker` (478 pts) with EMA/Kalman smoothing (and manual `(x, y)` override) + skin-polygon mask + `Depth-Anything-V2-Small` / `MODNet` alpha/depth map for `bgBlur`.
4. **`lib/noor/calligraphy.py`**: Render Uthmani Arabic via `Pillow + libraqm` (or `skia-python + uharfbuzz`) across `9:16`, `1:1`, `16:9`, `4:5` with Viral Hook pill banner, 4 `QuranTypographyStyle` themes, frosted glass backdrop blur, 4 `WaveformStyle` renderers (`SOLID`, `GLASS_MODERN`, `GLASS_BARS`, `VINTAGE_DOTS`), and TikTok/Reels Safe Zone overlays.
5. **AI Quran Aligner (`tools/analysis/quran_ayah_aligner.py`)**: `tarteel-ai/whisper-base-ar-quran` (`faster-whisper`) → `mushaf_store` canonical lookup → `WhisperX` word-level karaoke timestamps.
6. **OpenMontage Tools**: Wrap into `tools/enhancement/noor_video_fx.py`, `tools/graphics/uthmani_overlay.py`, and `tools/analysis/quran_ayah_aligner.py`.
* **Gate 3:** Golden PNG tests verify intact Uthmani Harakat/Tashkeel (`ٱلرَّحْمَـٰنِ`, *Waqf* marks), split-wipe shader boundaries, and strict Mushaf grounding (zero unverified ASR verses).

---

#### Sprint 4: Deterministic Pipelined Export & OpenMontage Native Pipeline
**Goal:** Fast hardware-encoded exports + full agentic OpenMontage workflow support.
1. **`lib/noor/exporter.py` + `lib/media_profiles.py`**:
   * Streaming generator piping exact `round(duration_s * fps)` frames + mastered WAV directly to `FFmpeg` (`h264_nvenc` / `h264_videotoolbox` / `h264_qsv` / `libx264` + `AAC 192–320 kbps`).
   * Supports Video (`4K/1080p/720p`, `60/30/24 FPS`, `ULTRA 16M / VIRAL 8M / LIGHT 4M`), Audio (`WAV 16/24-bit`, `MP3 320k`, `FLAC`), and Cover (`PNG`), with real-time FPS/ETA, `SIGTERM` cancel + temp cleanup, and XP award (`+150`).
2. **`tools/publishers/noor_export.py`**: `BaseTool` wrapper for agentic exports.
3. **OpenMontage Native Pipeline & Templates**:
   * Create `pipeline_defs/noor-quranic-cinematic.yaml` + `skills/pipelines/noor-quranic-cinematic/*-director.md` (`idea` → `publish`).
   * Add `remotion-composer/src/NoorQuranReel.tsx` and HyperFrames composition skill (`skills/core/noor-hyperframes.md`) so OpenMontage agents can also produce Noor reels natively using `video_compose`.
* **Gate 4:** Render a 3-second `1080p60` test clip via `noor_export` and assert via `ffprobe`: `nb_frames == 180`, `h264`, `yuv420p`, `aac`, `size > 0`.

---

#### Sprint 5: Interactive Workstation Backend & PySide6 GUI (`noor_studio/`)
**Goal:** Deliver the complete real-time desktop studio experience on top of `lib/noor/`.
1. **`noor_studio/server.py` (FastAPI Daemon on `127.0.0.1`)**:
   * Bearer-token-authenticated REST routes (`/project`, `/dsp`, `/video`, `/viral`, `/presets`, `/pipeline`, `/ai`, `/export`, `/recorder`)
   * WebSocket (`ws://`) pushing 60 Hz 48-bin FFT, LUFS, VU levels, and export progress
   * Shared-memory (`mmap`) preview frame buffer for zero-copy 60 FPS viewport updates.
2. **`noor_studio/copilot.py`**: Structured-output assistant (`Gemini` via `.env` or local `Ollama Qwen2.5-14B`) returning bilingual viral hooks, concise Tafsir reflections (visually separated from canonical Mushaf text), and Pydantic-validated mood-to-preset patches.
3. **`noor_studio/gui/` (PySide6 / Qt 6)**:
   * Obsidian & Signal Blue QSS theme, instant runtime **Arabic (`ar` RTL mirrored) / English (`en` LTR)** switching, NLE shortcuts (`Space`, `J/K/L`, `I/O`, `Ctrl/Cmd+E`, `Ctrl/Cmd+Z`), and dual-layer `SmartInfoTooltip` (`ℹ️`).
   * `gl_viewport.py` (`QOpenGLWidget`): 4 preview modes, draggable Split wipe, draggable Face Glow reticle, clickable CapCut bounding boxes, Safe Zone guides, TrimRange scrubbing, 1-click Pro Audio HUD (`Zero-Noise`, `Haram Reverb`, `Deep Bass`).
   * 5 Workflow Tabs: `VIDEO` (قديروف), `AUDIO` (صوت الحرم + 60 FPS `QPainter` visualizer), `VIRAL` (التريند + Mushaf carousel/picker), `PRESETS` (القوالب), `PIPELINE` (سلسلة المؤثرات — live node reorder & bypass wired directly to `pipeline_dag.py`).
   * All 6 Modals + Journey Banner: `StudioRecorderModal`, `ExportModal`, `ContemplationModeDialog` (محراب التدبر), `SpiritualKnowledgeModal`, `TransformationDashboardModal`, `VersionModal`, and collapsible 4-station `SpiritualJourneyBanner`.
* **Gate 5:** `pytest-qt` tests verify RTL layout switching, slider/DAG state sync, modal workflows, and live `< 15 ms` audio monitor callback stability.

---

#### Sprint 6: End-to-End Acceptance & OpenMontage PR/Contract Audit
1. Run OpenMontage's full contract and QA test suites (`pytest tests/contracts/ tests/qa/`), `ruff check`, and `mypy`.
2. Verify all 4 mandatory acceptance gates end-to-end:
   * Real mic capture + live DSP + 60 Hz spectrum/LUFS.
   * Split wipe, Face AI tracking, Depth bokeh, and Uthmani calligraphy in 4 aspect ratios.
   * Pipeline DAG node reordering changing real DSP/shader output & measured `ms` latency.
   * Full `MP4` (`1080p60` & `4K`), `WAV`/`MP3`/`FLAC`, and `PNG` exports + XP increment + Backlot board compatibility (`python -m backlot open`).

---

### 5. Immediate Next Step (Copy-Paste Prompt for Your Coding Agent)

Once you clone `OpenMontageInc/OpenMontage` and run `make setup`, save your Master Spec to `docs/NOOR_MASTER_SPEC.md` and give your coding agent (Claude Code, Cursor, Codex, etc.) this prompt to start **Sprint 1** cleanly inside OpenMontage's rules:

```text
Read AGENT_GUIDE.md, PROJECT_CONTEXT.md, docs/ARCHITECTURE.md, and docs/NOOR_MASTER_SPEC.md.

We are integrating "Noor Cinematic Studio" into OpenMontage as:
1) A compliant OpenMontage extension: pure engines in lib/noor/, BaseTool plugins in
   tools/ (discovered via tools/tool_registry.py), YAML playbooks in styles/noor/,
   and a new pipeline_defs/noor-quranic-cinematic.yaml + stage director skills.
2) An interactive desktop workstation in noor_studio/ (FastAPI + PySide6 QOpenGLWidget)
   that reuses lib/noor/ for <15ms live audio monitoring, 60fps OpenGL preview, and
   real-time pipeline DAG reordering.

Respect OpenMontage's BaseTool contract and schemas/styles/playbook.schema.json.
Start with Sprint 1 ONLY: create requirements-noor.txt, lib/noor/schemas.py (with
strict math.isfinite() validators for all enums/bounds), lib/noor/mushaf_store.py,
lib/noor/storage.py (SQLite WAL + 8 seeded presets + 4 atmospheres + 5 lessons),
styles/noor/*.yaml, and Sprint 1 pytest verification. Do not write Sprint 2+ yet.
```

If you tell me **your OS + GPU** (e.g., Windows + NVIDIA RTX, macOS Apple Silicon, or Linux CPU) and **which AI coding assistant** you're running OpenMontage with, I can give you the exact `requirements-noor.txt` and `ffmpeg` encoder flags tailored to your machine.


Your **ASUS TUF Gaming F16 on Windows 11** is a **Tier 2 RTX Workstation**—meaning you have both **Intel multi-core CPU** and an **NVIDIA GeForce RTX Laptop GPU** (RTX 3050/4050/4070 or RTX 5070 depending on your exact F16 sub-model, 6–8 GB VRAM).

That lets you run **every local AI model**, **60 FPS OpenGL shaders**, and **hardware `NVENC` MP4/4K exports** locally at high speed—provided you handle **4 Windows 11 / TUF F16 pitfalls** up front.

---

### 1. Windows 11 & ASUS TUF F16 Hardware Setup Checklist

#### A. Critical Windows Pitfalls to Avoid Before Installing
1. **Use Official Python (NOT Microsoft Store Python):** Install Python **3.11 or 3.12 (64-bit)** from `python.org` (checking *"Add Python to PATH"*). Store-sandboxed Python breaks `fribidi.dll`, CUDA paths, and subprocess piping.
2. **Force NVIDIA RTX GPU for Python & GUI (MUX / Optimus):**
   * On TUF F16 laptops, Windows often routes Python scripts to the Intel iGPU by default.
   * Open **Windows Settings → System → Display → Graphics → Add desktop app**, add your `.venv\Scripts\python.exe`, and set GPU preference to **High Performance (NVIDIA GeForce RTX)** (or switch Armoury Crate / MUX to Discrete/Standard when plugged in).
3. **Node.js `22.x` & Windows `npm` Fix:** OpenMontage's HyperFrames requires **Node.js 22.23.4+**. If `npm install` inside `remotion-composer` throws `ERR_INVALID_ARG_TYPE` on Windows, run `npx --yes npm install` instead.
4. **Arabic Uthmani Diacritics on Windows (`libraqm` Trap):**
   * `pip install pillow` on Windows **does not** enable `raqm` by default (`PIL.features.check_feature("raqm")` returns `False`) unless `fribidi.dll` is on `PATH`.
   * **Best Windows 11 choice:** Use **`uharfbuzz` + `skia-python`** (or **`PySide6` `QImage` + `QPainter`**, which uses Windows DirectWrite/HarfBuzz natively with zero missing DLLs) for Uthmani calligraphy rendering, and add a `pytest` gate verifying *Tashkeel/Harakat* never detach.

---

### 2. Exact Windows 11 PowerShell Setup Commands

Open **Windows Terminal (PowerShell)** *(run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once if script activation is blocked)*:

```powershell
# 1. Verify system prerequisites
py -3 --version          # Python 3.11 or 3.12
node --version           # v22.23.4+ recommended
ffmpeg -version          # Confirm h264_nvenc is listed: ffmpeg -encoders | findstr nvenc
git --version

# 2. Clone OpenMontage and create venv
git clone https://github.com/OpenMontageInc/OpenMontage.git noor-openmontage
cd noor-openmontage
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade "pip>=26.2.2"

# 3. Install OpenMontage base requirements + Node composer
python -m pip install -r requirements.txt
cd remotion-composer
npx --yes npm install
cd ..
python -m pip install piper-tts
copy .env.example .env
```

*(If `ffmpeg` isn't installed yet on Windows 11: `winget install Gyan.FFmpeg` and restart your terminal so `h264_nvenc` / `hevc_nvenc` are available in `PATH`.)*

---

### 3. Tailored `requirements-noor.txt` for Your ASUS TUF F16 (CUDA + PySide6)

Save this as `requirements-noor.txt` in the repo root and install it into `.venv` **after** `requirements.txt` (installing PyTorch CUDA wheel explicitly first so `pip` doesn't pull CPU-only `torch`):

```powershell
# Step A: Install CUDA-enabled PyTorch for your RTX Laptop GPU (check `nvidia-smi` for CUDA 12.4/12.6)
python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124

# Step B: Install Noor DSP, OpenGL, Uthmani, AI, and PySide6 Workstation packages
python -m pip install -r requirements-noor.txt
```

**`requirements-noor.txt`:**
```text
# --- Audio I/O & "Golden Order" DSP (<15ms WASAPI/ASIO) ---
sounddevice>=0.5.1
soundfile>=0.12.1
pedalboard>=0.9.16
scipy>=1.14.0
numba>=0.60.0
pyloudnorm>=0.1.1

# --- Video Decode, ModernGL Shaders & Portrait Vision ---
av>=13.1.0
moderngl>=5.11.0
opencv-python-headless>=4.10.0
numpy>=1.26.4,<2.2

# --- Uthmani Arabic Shaping (Windows-Safe, No Missing libraqm DLLs) ---
uharfbuzz>=0.42.0
skia-python>=87.6
python-bidi>=0.6.0

# --- AI Speech, Quran Alignment & Depth Bokeh (RTX CUDA Accelerated) ---
deepfilternet>=0.5.6
faster-whisper>=1.1.0
rapidfuzz>=3.10.0
mediapipe>=0.10.18
transformers>=4.46.0
accelerate>=1.1.0

# --- Storage, API Daemon & PySide6 Desktop Workstation ---
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlalchemy>=2.0.36
aiosqlite>=0.20.0
alembic>=1.14.0
PySide6>=6.8.0
qasync>=0.27.1

# --- Testing & Verification ---
pytest>=8.3.0
pytest-asyncio>=0.24.0
pytest-qt>=4.4.0
ruff>=0.8.0
mypy>=1.13.0
```

*(Note: Keep `clearvoice` / `MossFormer2_SE_48K` in a separate optional install step after verifying Sprint 2, as it pulls heavier model checkpoints on first run; also ensure you stay on **6–8 GB VRAM budgets** by loading `faster-whisper` in `int8_float16` and `Depth-Anything-V2-Small` in `fp16` so you never hit VRAM OOM when `ModernGL` is running simultaneously!)*

---

### 4. Exact Hardware-Tuned Engine Settings for Your Laptop

Tell your coding agent to bake these TUF F16 defaults into `lib/noor/`:

1. **FFmpeg Export (`lib/noor/exporter.py` & `lib/media_profiles.py`):**
   * Primary encoder: **`h264_nvenc`** (or `hevc_nvenc` for 4K) with `-preset p5 -rc vbr -cq 19 -pix_fmt yuv420p -movflags +faststart` and `aac -b:a 256k`.
   * Automatic fallback to `libx264` if `nvenc` is unavailable in headless/CI tests.
   * **Expected speed on your RTX GPU:** `1080p60` renders faster than real-time (`60–120+ FPS`) instead of stalling.
2. **VRAM Coexistence Guard (`6–8 GB` Laptop VRAM):**
   * `faster-whisper` (`tarteel-ai/whisper-base-ar-quran`): `device="cuda"`, `compute_type="int8_float16"` (~400 MB VRAM).
   * `Depth-Anything-V2-Small`: `torch.float16` (~350 MB VRAM), unloaded cleanly when `bgBlur == 0`.
   * Leaves `> 4.5 GB` VRAM headroom for `ModernGL` 4K textures and Windows compositor.
3. **Low-Latency Windows Audio (`lib/noor/recorder.py`):**
   * Select **WASAPI** (`sd.query_hostapis()` → `"Windows WASAPI"`) at `48000 Hz`, `blocksize=512` (`10.67 ms` buffer), `dtype="float32"`.
   * Warn users in `StudioRecorderModal` if the selected mic is a Bluetooth Hands-Free profile (which forces 16 kHz mono and high latency).

---

### 5. Your Updated Sprint 1 Kickoff Prompt (Tuned for Windows 11 + TUF F16)

Paste this directly into your coding assistant inside `noor-openmontage` after running the setup commands above:

```text
Read AGENT_GUIDE.md, PROJECT_CONTEXT.md, docs/ARCHITECTURE.md, and docs/NOOR_MASTER_SPEC.md.

Target Environment: Windows 11, ASUS TUF Gaming F16 (Intel HX + NVIDIA RTX Laptop GPU,
6-8 GB VRAM), Python 3.11/3.12, FFmpeg with h264_nvenc, Node 22+.

We are integrating "Noor Cinematic Studio" into OpenMontage as:
1) Native OpenMontage extensions: pure engines in lib/noor/, BaseTool plugins in tools/
   (discovered by tools/tool_registry.py), YAML playbooks in styles/noor/, and
   pipeline_defs/noor-quranic-cinematic.yaml.
2) An interactive PySide6 + FastAPI workstation in noor_studio/ reusing lib/noor/.

Windows-specific rules:
- Use PySide6 QPainter / skia-python + uharfbuzz for Uthmani Arabic rendering (do NOT rely
  on Pillow libraqm DLLs on Windows).
- Default hardware exporter to h264_nvenc with automatic libx264 fallback.
- Configure WASAPI 48kHz float32 (blocksize=512) for sounddevice capture.
- Guard all VRAM models (fp16 / int8_float16) for 6-8 GB laptop VRAM.

Start with Sprint 1 ONLY:
Create requirements-noor.txt, lib/noor/schemas.py (all 11 enums + math.isfinite()
guards), lib/noor/mushaf_store.py (canonical Tanzil index + RapidFuzz verifier),
lib/noor/storage.py (async SQLite WAL with 8 seeded presets, 4 atmospheres, 5 lessons),
styles/noor/*.yaml (conforming to schemas/styles/playbook.schema.json), and full
pytest verification in tests/noor/test_sprint1.py. Run pytest and report real output.
```

Once Sprint 1 passes `pytest`, move sequentially to **Sprint 2 (Audio DSP + WASAPI Recorder)**, **Sprint 3 (ModernGL + Uthmani + Quran Aligner)**, **Sprint 4 (`h264_nvenc` Export + OpenMontage Pipeline)**, and **Sprint 5 (`noor_studio/` PySide6 Workstation)**.

