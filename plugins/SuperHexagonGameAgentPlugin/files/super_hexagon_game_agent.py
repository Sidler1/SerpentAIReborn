"""A worked reference game agent ported to the modern Serpent API.

Super Hexagon is the simplest of the bundled games, so it serves as the end-to-end
example of the modern play loop: the ``PLAY`` frame handler reads each frame, picks
an action from the game's input map (``GameAPI.game_inputs``), and applies it via
the input controller. The policy here is intentionally trivial (random rotation) —
the point is to demonstrate the wiring, not to be good at the game. Swap
``_select_action`` for a real policy (e.g. a serpent RL ``Agent`` over the input
space, or a frame-analysis heuristic) to make it play well.
"""

import random

from serpent.game_agent import GameAgent


class SuperHexagonGameAgent(GameAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play
        self.frame_handler_setups["PLAY"] = self.setup_play

    def setup_play(self):
        # game_inputs maps action labels -> lists of KeyboardEvent.
        self.rotate_inputs = self.game.api.game_inputs["ROTATE"]

    def handle_play(self, game_frame, game_frame_pipeline, **kwargs):
        label = self._select_action(game_frame)
        keys = [event.keyboard_key for event in self.rotate_inputs[label]]

        if keys:
            self.input_controller.tap_keys(keys, duration=0.05)

        print(f"Super Hexagon action: {label}")

    def _select_action(self, game_frame):
        return random.choice(list(self.rotate_inputs.keys()))
