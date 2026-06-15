"""Peglin game agent — a runnable reference for the mouse-aim play loop.

Peglin combat is turn-based: aim the orb with the mouse and left-click to fire,
then watch it bounce. This reference agent waits a fixed number of frames between
shots (so it doesn't spam clicks mid-bounce), aims at a point in the upper play
area, and fires. The aiming policy is intentionally naive (random horizontal
sweep) — replace ``_aim_point`` with a real policy (peg/enemy detection via the
frame + screen_regions, trajectory planning, or an RL agent over discretized aim
angles).
"""

import random

from serpent.game_agent import GameAgent
from serpent.input_controller import MouseButton

# Peglin combat is turn-based; wait this many frames between shots so the orb
# finishes bouncing before the next aim+fire.
FIRE_INTERVAL_FRAMES = 30


class PeglinGameAgent(GameAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play
        self.frame_handler_setups["PLAY"] = self.setup_play

    def setup_play(self):
        self._frames_since_fire = 0

    def handle_play(self, game_frame, game_frame_pipeline, **kwargs):
        self._frames_since_fire += 1

        if self._frames_since_fire < FIRE_INTERVAL_FRAMES:
            return

        self._frames_since_fire = 0

        aim_x, aim_y = self._aim_point()

        self.input_controller.move(x=aim_x, y=aim_y, duration=0.2)
        self.input_controller.click(button=MouseButton.LEFT)

        print(f"Peglin: fired orb aimed at ({aim_x}, {aim_y})")

    def _aim_point(self):
        # Absolute screen coordinates within the upper-middle of the game window.
        geometry = self.game.window_geometry

        x = geometry["x_offset"] + random.randint(
            int(geometry["width"] * 0.30), int(geometry["width"] * 0.70)
        )
        y = geometry["y_offset"] + int(geometry["height"] * 0.35)

        return x, y
