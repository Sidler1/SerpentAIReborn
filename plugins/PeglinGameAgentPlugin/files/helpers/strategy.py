"""Peglin aiming strategy.

The orb launches from the top and falls through the peg field, so to hit as many
pegs as possible we aim at the **densest vertical band** of pegs and at the top of
that band (the orb's entry point). This is a deliberately simple, dependency-free
heuristic; richer policies (trajectory simulation, targeting crit/special pegs, or
an RL agent over discretized aim angles) can replace ``choose_aim`` later.
"""

from __future__ import annotations

import numpy as np

from .vision import DEFAULT_BOARD, board_box

BAND_WIDTH_PX = 80


def choose_aim(pegs, frame_shape, board=DEFAULT_BOARD):
    """Return the aim point ``(x, y)`` in frame pixels for the current pegs."""
    top, left, bottom, right = board_box(frame_shape, board)

    if not pegs:
        # No pegs detected — aim into the upper-centre of the board.
        return ((left + right) // 2, top + (bottom - top) // 5)

    xs = np.array([p[0] for p in pegs])
    ys = np.array([p[1] for p in pegs])

    bins = max(4, (right - left) // BAND_WIDTH_PX)
    histogram, edges = np.histogram(xs, bins=bins, range=(left, right))

    densest = int(np.argmax(histogram))
    low, high = edges[densest], edges[densest + 1]

    in_band = (xs >= low) & (xs <= high)

    target_x = int(xs[in_band].mean())
    target_y = int(ys[in_band].min())  # top of the densest column = orb entry point

    return (target_x, target_y)


__all__ = ["choose_aim"]
