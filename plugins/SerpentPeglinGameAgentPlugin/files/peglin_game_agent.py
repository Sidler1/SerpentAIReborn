"""Peglin game agent.

Each step, with a short cooldown between actions:
1. If a green **Continue** button is on screen (rewards / level-up / confirm), buy
   the offered relics/potions and then click it — these screens have no peg field,
   so the agent would otherwise stall (and would never collect any upgrades).
2. Otherwise, if pegs are detected (combat), aim crit-peg-first (then refresh when
   the board is thin, else the densest peg column) and fire the orb.
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

        # 1) Reward / level-up / confirm screens (checked first: these yield
        #    spurious "pegs", but combat has no large green button). Buy the
        #    offered relics/potions first, then advance with Continue.
        button = navigation.find_continue_button(frame)
        if button is not None:
            self._handle_reward_screen(frame, button)
            self._last_action = time.perf_counter()
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

    def _handle_reward_screen(self, frame, continue_button):
        # Reward rows offer relics/potions to pick up — click each before
        # continuing so the run actually accumulates upgrades. We only target the
        # top item row (avoids the "Upgrade an Orb" sub-screen lower down, which
        # needs its own handling). Best-effort: a click may open a confirm popup,
        # which the next Continue press dismisses.
        items = vision.detect_reward_items(frame)
        for item_x, item_y in items:
            self._click(item_x, item_y)
            time.sleep(0.4)

        self._click(*continue_button)
        print(
            f"Peglin: reward screen -> picked {len(items)} item(s), "
            f"clicked Continue at {continue_button}"
        )

    def _click(self, frame_x, frame_y):
        # Pass window-relative (frame) coords: InputController.move() adds the
        # window offset itself (adding it here too double-counted it — clicks
        # landed window_geometry["y_offset"] px too low).
        self.input_controller.move(x=frame_x, y=frame_y, duration=0.15)
        self.input_controller.click(button=MouseButton.LEFT)
