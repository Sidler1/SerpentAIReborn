"""Non-combat screen handling for Peglin.

Between battles Peglin shows reward/level-up/confirm screens with a green
**Continue** button. Detecting and clicking it advances past those screens (the
agent otherwise stalls, since they have no peg field). The button is a large
muted-green blob in the lower-centre of the screen; combat has no such blob (the
green *special pegs* are tiny), so checking for it first cleanly distinguishes
menu screens from combat.
"""

from __future__ import annotations

import numpy as np
import skimage.measure

# Minimum green-blob area to count as a button (filters out green special pegs).
MIN_BUTTON_AREA = 2000


def find_continue_button(frame, min_area=MIN_BUTTON_AREA):
    """Return the green Continue/confirm button centre ``(x, y)``, or None."""
    height, width = frame.shape[0], frame.shape[1]

    r = frame[..., 0].astype(int)
    g = frame[..., 1].astype(int)
    b = frame[..., 2].astype(int)
    green = (g > 90) & (g > r + 25) & (g > b + 25)

    region = np.zeros(green.shape, dtype=bool)
    region[int(0.55 * height):, int(0.20 * width):int(0.80 * width)] = True

    labels = skimage.measure.label(green & region)
    buttons = [p for p in skimage.measure.regionprops(labels) if p.area >= min_area]

    if not buttons:
        return None

    largest = max(buttons, key=lambda p: p.area)
    row, col = largest.centroid
    return (int(col), int(row))


__all__ = ["find_continue_button"]
