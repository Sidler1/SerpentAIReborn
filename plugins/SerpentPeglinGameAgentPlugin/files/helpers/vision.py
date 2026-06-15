"""Peglin frame analysis.

Pegs are bright dots on the dark-blue board: **white** (normal), **green**
(special/refresh) and **orange/gold** (crit). We isolate them with a brightness
mask over the board region, label connected components, keep peg-sized roughly
circular blobs, and classify each by colour. Coordinates are frame pixels
(relative to the captured game window).

Calibrated against a 1280x720 Forest combat frame.
"""

from __future__ import annotations

import numpy as np
import skimage.measure

# Board region (the dark-blue peg field) as fractions of the window
# (top, left, bottom, right) — excludes the side panels / launcher / HUD.
DEFAULT_BOARD = (0.30, 0.325, 0.82, 0.79)

# A peg blob's pixel area (the round pegs are ~12-18 px across); filters out
# texture speckle (too small) and the long peg-arcs / bombs (too big).
MIN_PEG_AREA = 40
MAX_PEG_AREA = 700

# Pixels brighter than this (max RGB channel) are peg/foreground vs dark board.
BRIGHTNESS_THRESHOLD = 150


def board_box(frame_shape, board=DEFAULT_BOARD):
    """Fractional board bounds -> absolute pixel (top, left, bottom, right)."""
    height, width = frame_shape[0], frame_shape[1]
    top, left, bottom, right = board
    return int(top * height), int(left * width), int(bottom * height), int(right * width)


def _classify(rgb):
    r, g, b = (int(c) for c in rgb)
    if g > 110 and g > r + 20 and g > b + 20:
        return "special"  # green refresh peg
    if r > 150 and g > 90 and b < 110 and r > b + 40:
        return "crit"  # orange/gold peg
    return "normal"


def detect_pegs(frame, board=DEFAULT_BOARD):
    """Return detected pegs as ``[(x, y, kind), ...]`` in frame-pixel coordinates.

    ``kind`` is one of ``"normal"``, ``"special"`` (green), ``"crit"`` (orange).
    """
    top, left, bottom, right = board_box(frame.shape, board)

    region = frame[top:bottom, left:right]
    if region.size == 0 or region.ndim != 3:
        return []

    mask = region.max(axis=2) > BRIGHTNESS_THRESHOLD
    labels = skimage.measure.label(mask)

    pegs = []
    for region_props in skimage.measure.regionprops(labels):
        if not (MIN_PEG_AREA <= region_props.area <= MAX_PEG_AREA):
            continue
        if region_props.eccentricity > 0.85:  # drop elongated arc fragments
            continue

        row, col = region_props.centroid
        x, y = int(col) + left, int(row) + top
        pegs.append((x, y, _classify(frame[y, x])))

    return pegs


def peg_count(frame, **kwargs):
    return len(detect_pegs(frame, **kwargs))


__all__ = ["DEFAULT_BOARD", "board_box", "detect_pegs", "peg_count"]
