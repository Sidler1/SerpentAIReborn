"""Peglin aiming strategy.

The orb launches from the top and falls through the pegs, so we aim at the **top
of the densest peg column** (the orb's entry point) to pass through the most pegs.
**Special** (green/refresh) and **crit** (orange) pegs are worth more, so if any
are present we aim at their densest column instead of the plain pegs.

Pegs are ``(x, y, kind)`` from ``vision.detect_pegs``. This is a simple, fast
heuristic; richer policies (trajectory simulation / an RL agent over aim angles)
can replace ``choose_aim`` later.
"""

from __future__ import annotations

import numpy as np

from .vision import DEFAULT_BOARD, board_box

BAND_WIDTH_PX = 80
PRIORITY_KINDS = ("special", "crit")


def choose_aim(pegs, frame_shape, board=DEFAULT_BOARD):
    """Return the aim point ``(x, y)`` in frame pixels for the current pegs."""
    top, left, bottom, right = board_box(frame_shape, board)

    if not pegs:
        return ((left + right) // 2, top + (bottom - top) // 5)

    priority = [p for p in pegs if p[2] in PRIORITY_KINDS]
    pool = priority if priority else pegs

    xs = np.array([p[0] for p in pool])
    ys = np.array([p[1] for p in pool])

    bins = max(4, (right - left) // BAND_WIDTH_PX)
    histogram, edges = np.histogram(xs, bins=bins, range=(left, right))

    densest = int(np.argmax(histogram))
    low, high = edges[densest], edges[densest + 1]
    in_band = (xs >= low) & (xs <= high)

    target_x = int(xs[in_band].mean())
    target_y = int(ys[in_band].min())  # top of the densest column

    return (target_x, target_y)


__all__ = ["choose_aim"]
