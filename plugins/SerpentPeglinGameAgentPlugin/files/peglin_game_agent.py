"""Peglin game agent.

Each turn: analyze the frame for pegs, aim at the densest peg column, and fire the
orb with a left-click. Combat is turn-based, so the agent waits a cooldown between
shots (so the orb finishes bouncing) and only fires when pegs are actually
detected. Vision lives in ``helpers/vision.py`` and the aiming policy in
``helpers/strategy.py``; swap those out to make it smarter.

Calibrate `helpers/vision.DEFAULT_BOARD` (and add a colour mask / HP / turn-cue
detection) against a real 1280x720 frame for best results.
"""

import time

from serpent.game_agent import GameAgent
from serpent.input_controller import MouseButton

from .helpers import strategy, vision

# Seconds to wait between shots (combat is turn-based; let the orb finish bouncing).
# Time-based so it's independent of the capture frame rate.
FIRE_COOLDOWN_SECONDS = 4.0


class SerpentPeglinGameAgent(GameAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play
        self.frame_handler_setups["PLAY"] = self.setup_play

    def setup_play(self):
        self._last_fire = 0.0  # ready to fire on the first turn

    def handle_play(self, game_frame, game_frame_pipeline, **kwargs):
        if time.perf_counter() - self._last_fire < FIRE_COOLDOWN_SECONDS:
            return

        pegs = vision.detect_pegs(game_frame.frame)

        if not pegs:
            # Likely mid-bounce or not the player's turn — wait for a peg field.
            print("Peglin: no pegs detected (waiting)")
            return

        aim_x, aim_y = strategy.choose_aim(pegs, game_frame.frame.shape)
        self._fire(aim_x, aim_y)

        self._last_fire = time.perf_counter()

        print(f"Peglin: {len(pegs)} pegs -> aim ({aim_x}, {aim_y})")

    def _fire(self, frame_x, frame_y):
        geometry = self.game.window_geometry

        screen_x = geometry["x_offset"] + frame_x
        screen_y = geometry["y_offset"] + frame_y

        self.input_controller.move(x=screen_x, y=screen_y, duration=0.15)
        self.input_controller.click(button=MouseButton.LEFT)
