"""Peglin game agent.

Each step, with a short cooldown between actions:
1. If a green **Continue** button is on screen (rewards / level-up / confirm), click
   it to advance — these screens have no peg field, so the agent would otherwise stall.
2. Otherwise, if pegs are detected (combat), aim at the densest special/crit peg
   column and fire the orb.
3. Otherwise wait (mid-bounce, or a screen we don't handle yet).

Vision is in ``helpers/vision.py``, the aim policy in ``helpers/strategy.py``, and
non-combat screen handling in ``helpers/navigation.py``.
"""

import time

from serpent.game_agent import GameAgent
from serpent.input_controller import MouseButton

from .helpers import navigation, strategy, vision

# Seconds between actions (let the orb finish bouncing / screens transition).
ACTION_COOLDOWN_SECONDS = 3.0


class SerpentPeglinGameAgent(GameAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play
        self.frame_handler_setups["PLAY"] = self.setup_play

    def setup_play(self):
        self._last_action = 0.0  # ready to act on the first frame

    def handle_play(self, game_frame, game_frame_pipeline, **kwargs):
        if time.perf_counter() - self._last_action < ACTION_COOLDOWN_SECONDS:
            return

        frame = game_frame.frame

        # 1) Advance reward / level-up / confirm screens (checked first: these
        #    yield spurious "pegs", but combat has no large green button).
        button = navigation.find_continue_button(frame)
        if button is not None:
            self._click(*button)
            self._last_action = time.perf_counter()
            print(f"Peglin: advancing menu -> clicked Continue at {button}")
            return

        # 2) Combat: aim at the best peg column and fire.
        pegs = vision.detect_pegs(frame)
        if not pegs:
            print("Peglin: no pegs / no button (waiting)")
            return

        aim_x, aim_y = strategy.choose_aim(pegs, frame.shape)
        self._click(aim_x, aim_y)
        self._last_action = time.perf_counter()
        print(f"Peglin: {len(pegs)} pegs -> aim ({aim_x}, {aim_y})")

    def _click(self, frame_x, frame_y):
        geometry = self.game.window_geometry

        screen_x = geometry["x_offset"] + frame_x
        screen_y = geometry["y_offset"] + frame_y

        self.input_controller.move(x=screen_x, y=screen_y, duration=0.15)
        self.input_controller.click(button=MouseButton.LEFT)
