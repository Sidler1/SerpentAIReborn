"""Peglin frame analysis.

Pegs are bright dots on the dark-blue board, classified by colour (sampled from a
real frame):
- **crit**    — orange/gold (low blue, r>g>b). Highest value: routes the orb's
  whole chain into critical damage. ~rgb (255,198,55)/(142,90,6).
- **refresh** — green (low blue, g>r). Refreshes the board. ~rgb (155,188,14).
- **normal**  — cream/white (high blue). ~rgb (255,233,203)/(255,255,255).

We mask bright pixels over the board region, label connected components, keep
peg-sized roughly circular blobs, and classify by the centroid colour. Coordinates
are frame pixels (relative to the captured game window). Calibrated on a 1280x720
Forest combat frame.
"""

from __future__ import annotations

import skimage.measure

DEFAULT_BOARD = (0.30, 0.325, 0.82, 0.79)  # (top, left, bottom, right) fractions

# Reward-screen item row (relics/potions you can buy), as fractions.
REWARD_ROW = (0.25, 0.26, 0.40, 0.75)

MIN_PEG_AREA = 40
MAX_PEG_AREA = 700
MIN_REWARD_AREA = 800
BRIGHTNESS_THRESHOLD = 150
LOW_BLUE = 80


def _box(frame_shape, fractions):
    height, width = frame_shape[0], frame_shape[1]
    top, left, bottom, right = fractions
    return int(top * height), int(left * width), int(bottom * height), int(right * width)


def board_box(frame_shape, board=DEFAULT_BOARD):
    return _box(frame_shape, board)


def _classify(rgb):
    r, g, b = (int(c) for c in rgb)
    if b < LOW_BLUE:
        if g > r and g > 120:
            return "refresh"  # green
        if r > g > b and r > 120:
            return "crit"  # orange/gold
    return "normal"


def detect_pegs(frame, board=DEFAULT_BOARD):
    """Return pegs as ``[(x, y, kind), ...]`` (kind: normal/refresh/crit) in frame px."""
    top, left, bottom, right = board_box(frame.shape, board)

    region = frame[top:bottom, left:right]
    if region.size == 0 or region.ndim != 3:
        return []

    mask = region.max(axis=2) > BRIGHTNESS_THRESHOLD
    labels = skimage.measure.label(mask)

    pegs = []
    for props in skimage.measure.regionprops(labels):
        if not (MIN_PEG_AREA <= props.area <= MAX_PEG_AREA):
            continue
        if props.eccentricity > 0.85:
            continue

        row, col = props.centroid
        x, y = int(col) + left, int(row) + top
        pegs.append((x, y, _classify(frame[y, x])))

    return pegs


def detect_reward_items(frame, row=REWARD_ROW):
    """Return clickable reward-item centres ``[(x, y), ...]`` (left to right)."""
    top, left, bottom, right = _box(frame.shape, row)

    region = frame[top:bottom, left:right]
    if region.size == 0 or region.ndim != 3:
        return []

    mask = region.max(axis=2) > 120
    labels = skimage.measure.label(mask)

    items = []
    for props in skimage.measure.regionprops(labels):
        if props.area < MIN_REWARD_AREA:
            continue
        row_c, col_c = props.centroid
        items.append((int(col_c) + left, int(row_c) + top))

    return sorted(items)


def peg_count(frame, **kwargs):
    return len(detect_pegs(frame, **kwargs))


__all__ = ["DEFAULT_BOARD", "board_box", "detect_pegs", "detect_reward_items", "peg_count"]
