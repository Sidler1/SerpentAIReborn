"""Peglin aiming strategy (from the wiki's combat rules).

Priority, per the orb's "accumulate damage then deal it on exit" model:
1. **Crit peg** — aim at the top-most crit peg so the orb routes through it early;
   crit applies to the whole chain that shot (the single highest-value play).
2. **Refresh peg** when the board is nearly empty — extends the shot by refilling.
3. Otherwise aim at the **top of the densest peg column** to hit the most pegs.

Pegs are ``(x, y, kind)`` from ``vision.detect_pegs``. A richer policy
(trajectory simulation / RL over aim angles) can replace ``choose_aim`` later.
"""

from __future__ import annotations

import numpy as np

from .vision import DEFAULT_BOARD, board_box

BAND_WIDTH_PX = 80
THIN_BOARD = 8  # pegs remaining at/below which a refresh peg is worth targeting


def _topmost(pegs):
    return min(pegs, key=lambda p: p[1])  # smallest y = highest on screen


def choose_aim(pegs, frame_shape, board=DEFAULT_BOARD):
    """Return the aim point ``(x, y)`` in frame pixels for the current pegs."""
    top, left, bottom, right = board_box(frame_shape, board)

    if not pegs:
        return ((left + right) // 2, top + (bottom - top) // 5)

    crit = [p for p in pegs if p[2] == "crit"]
    if crit:
        x, y, _ = _topmost(crit)
        return (x, y)

    refresh = [p for p in pegs if p[2] == "refresh"]
    if refresh and len(pegs) <= THIN_BOARD:
        x, y, _ = _topmost(refresh)
        return (x, y)

    # Densest vertical column of all pegs.
    xs = np.array([p[0] for p in pegs])
    ys = np.array([p[1] for p in pegs])

    bins = max(4, (right - left) // BAND_WIDTH_PX)
    histogram, edges = np.histogram(xs, bins=bins, range=(left, right))

    densest = int(np.argmax(histogram))
    low, high = edges[densest], edges[densest + 1]
    in_band = (xs >= low) & (xs <= high)

    return (int(xs[in_band].mean()), int(ys[in_band].min()))


__all__ = ["choose_aim"]
