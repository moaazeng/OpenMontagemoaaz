"""TDD RED tests for the Noor "Golden Order" audio DSP chain.

Written BEFORE lib/noor/audio_dsp.py exists. Expected to fail with
ModuleNotFoundError (feature missing) until Task B.3 implements the
GoldenOrderDSP engine.

All tests use real scipy/pedalboard/pyloudnorm — no mocks.
"""

from __future__ import annotations

import numpy as np
import pytest

SAMPLE_RATE = 48000


def test_silence_produces_no_nan_inf():
    """Silence through the full chain must not emit NaN/Inf."""
    from lib.noor.audio_dsp import GoldenOrderDSP
    from lib.noor.schemas import DSPConfig

    dsp = GoldenOrderDSP(sample_rate=SAMPLE_RATE)
    silence = np.zeros(SAMPLE_RATE, dtype=np.float32)  # 1 second
    out = dsp.process(silence, DSPConfig())
    assert out.shape == silence.shape
    assert np.all(np.isfinite(out)), "silence produced NaN/Inf"


def test_clipped_burst_never_exceeds_true_peak_limit():
    """+10 dBFS burst through preamp (4.0x) must not pass -1.0 dBTP limiter."""
    from lib.noor.audio_dsp import GoldenOrderDSP
    from lib.noor.schemas import DSPConfig

    dsp = GoldenOrderDSP(sample_rate=SAMPLE_RATE)
    t = np.arange(SAMPLE_RATE, dtype=np.float32) / SAMPLE_RATE
    burst = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)  # ~-6 dBFS
    cfg = DSPConfig(preamp_gain=4.0)  # would clip hard without limiting
    out = dsp.process(burst, cfg)
    peak_db = 20 * np.log10(np.max(np.abs(out)) + 1e-12)
    assert peak_db <= -1.0, f"true peak {peak_db:.2f} dBTP exceeds -1.0 dBTP brickwall"


def test_eq_bands_affect_fft_bins():
    """Each EQ band must measurably shape its target frequency region."""
    from lib.noor.audio_dsp import GoldenOrderDSP
    from lib.noor.schemas import DSPConfig

    dsp = GoldenOrderDSP(sample_rate=SAMPLE_RATE)
    # 1 kHz tone — should land in band 3 region (approx 500-2k Hz).
    t = np.arange(SAMPLE_RATE, dtype=np.float32) / SAMPLE_RATE
    tone = np.sin(2 * np.pi * 1000 * t).astype(np.float32)

    def _fft_peak_db(samples: np.ndarray, freq: float) -> float:
        window = samples * np.hanning(len(samples))
        spectrum = np.abs(np.fft.rfft(window))
        freqs = np.fft.rfftfreq(len(samples), 1 / SAMPLE_RATE)
        idx = int(np.argmin(np.abs(freqs - freq)))
        mag = spectrum[idx] / (len(samples) / 2)
        return 20 * np.log10(mag + 1e-12)

    base = _fft_peak_db(tone, 1000.0)
    boosted = _fft_peak_db(dsp.process(tone, DSPConfig(eq_band_3_gain_db=+12.0)), 1000.0)
    cut = _fft_peak_db(dsp.process(tone, DSPConfig(eq_band_3_gain_db=-12.0)), 1000.0)

    assert boosted > base + 3.0, f"+12 dB EQ did not boost 1 kHz ({base:.1f} -> {boosted:.1f})"
    assert cut < base - 3.0, f"-12 dB EQ did not cut 1 kHz ({base:.1f} -> {cut:.1f})"


def test_hpf_and_notch_remove_low_frequencies():
    """HPF + 50/60 Hz notch must suppress sub-bass and mains hum."""
    from lib.noor.audio_dsp import GoldenOrderDSP
    from lib.noor.schemas import DSPConfig

    dsp = GoldenOrderDSP(sample_rate=SAMPLE_RATE)
    t = np.arange(SAMPLE_RATE, dtype=np.float32) / SAMPLE_RATE
    hum = (np.sin(2 * np.pi * 50 * t) + np.sin(2 * np.pi * 60 * t)).astype(np.float32)

    def _band_power(samples: np.ndarray, lo: float, hi: float) -> float:
        window = samples * np.hanning(len(samples))
        spectrum = np.abs(np.fft.rfft(window))
        freqs = np.fft.rfftfreq(len(samples), 1 / SAMPLE_RATE)
        mask = (freqs >= lo) & (freqs <= hi)
        return float(np.sum(spectrum[mask] ** 2))

    raw_power = _band_power(hum, 45, 65)
    out = dsp.process(hum, DSPConfig())
    out_power = _band_power(out, 45, 65)
    assert out_power < raw_power * 0.1, f"HPF+notch did not suppress 50/60 Hz hum ({raw_power:.2f} -> {out_power:.2f})"


def test_analyze_returns_finite_metrics():
    """analyze() must return finite LUFS momentary/integrated/true-peak + 48-bin FFT."""
    from lib.noor.audio_dsp import GoldenOrderDSP

    dsp = GoldenOrderDSP(sample_rate=SAMPLE_RATE)
    t = np.arange(SAMPLE_RATE // 2, dtype=np.float32) / SAMPLE_RATE  # 0.5 s
    tone = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    analysis = dsp.analyze(tone)
    assert analysis.sample_rate == SAMPLE_RATE
    assert len(analysis.fft_bins) == 48
    assert np.isfinite(analysis.lufs_momentary)
    assert np.isfinite(analysis.lufs_integrated)
    assert np.isfinite(analysis.true_peak_db_tp)
    assert np.isfinite(analysis.clarity_ratio)
    assert all(np.isfinite(b) for b in analysis.fft_bins)


def test_audio_dsp_suite_is_runnable():
    """This file itself is valid pytest; RED failures are import errors, not typos."""
    assert True
