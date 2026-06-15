"""Peglin frame analysis.

The peg board is the part of the frame the agent reasons about. ``detect_pegs``
finds the circular pegs inside a board sub-region using Laplacian-of-Gaussian blob
detection on the grayscale image — no per-game colour calibration required to get
started (refine with a colour mask once a real frame is available).

Coordinates returned are in **frame pixels** (relative to the captured game
window, origin top-left), so the agent only needs to add the window offset to
click.
"""

from __future__ import annotations

import numpy as np
import skimage.color
import skimage.feature

# Board region as fractions of the window (top, left, bottom, right). The peg
# field sits in the centre; tighten these once calibrated to a real 1280x720 frame.
DEFAULT_BOARD = (0.15, 0.20, 0.90, 0.80)


def board_box(frame_shape, board=DEFAULT_BOARD):
    """Convert fractional board bounds to absolute pixel (top, left, bottom, right)."""
    height, width = frame_shape[0], frame_shape[1]
    top, left, bottom, right = board
    return (
        int(top * height),
        int(left * width),
        int(bottom * height),
        int(right * width),
    )


def detect_pegs(frame, board=DEFAULT_BOARD, min_sigma=2.0, max_sigma=8.0, threshold=0.08):
    """Return detected peg centres as ``[(x, y), ...]`` in frame-pixel coordinates."""
    top, left, bottom, right = board_box(frame.shape, board)

    region = frame[top:bottom, left:right]
    if region.size == 0:
        return []

    grayscale = skimage.color.rgb2gray(region) if region.ndim == 3 else region

    blobs = skimage.feature.blob_log(
        grayscale,
        min_sigma=min_sigma,
        max_sigma=max_sigma,
        num_sigma=5,
        threshold=threshold,
    )

    # blob_log rows are (y, x, sigma); shift back into full-frame coordinates.
    return [(int(x) + left, int(y) + top) for y, x, _ in blobs]


def peg_count(frame, **kwargs):
    return len(detect_pegs(frame, **kwargs))


__all__ = ["DEFAULT_BOARD", "board_box", "detect_pegs", "peg_count"]
