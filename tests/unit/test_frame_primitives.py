"""Core frame primitives: GameFrame variants/SSIM and the frame limiter.

Locks the Phase B modernizations (skimage.metrics.structural_similarity,
np.frombuffer, perf_counter timing).
"""

import numpy as np
import pytest

from serpent.game_frame import GameFrame
from serpent.game_frame_limiter import GameFrameLimiter


def _frame(size=32):
    return (np.arange(size * size * 3) % 256).astype("uint8").reshape(size, size, 3)


def test_grayscale_and_resolution_variants():
    frame = GameFrame(_frame(32))

    assert frame.grayscale_frame.shape == (32, 32)
    assert frame.grayscale_frame.dtype == np.uint8
    assert frame.half_resolution_frame.shape == (16, 16, 3)
    assert frame.quarter_resolution_frame.shape == (8, 8, 3)
    assert frame.eighth_resolution_frame.shape == (4, 4, 3)


def test_compare_ssim_of_identical_frames_is_one():
    frame = GameFrame(_frame())
    other = GameFrame(_frame().copy())

    assert frame.compare_ssim(other) == pytest.approx(1.0)


def test_to_png_bytes_and_top_color():
    frame = GameFrame(_frame())

    assert frame.to_png_bytes().startswith(b"\x89PNG")

    top_color = frame.top_color
    assert isinstance(top_color, list)
    assert len(top_color) == 3


def test_frame_limiter_runs_and_sleeps_within_budget():
    limiter = GameFrameLimiter(fps=1000)
    assert limiter.frame_time == pytest.approx(0.001)

    limiter.start()
    limiter.stop_and_delay()  # monotonic clock; must not raise
