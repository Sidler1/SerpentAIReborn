"""Binding of Isaac game agent — modern-API scaffold.

This plugin loads and validates against the modern Serpent API, but the
game-specific intelligence is NOT yet ported. The 2017 prototype shipped a large
agent (~40 KB) plus minimap/room/floor CV helpers and a Keras/DQN training flow;
that logic lives in git history on the ``master`` branch
(``plugins/BindingOfIsaacRebirthGameAgentPlugin``) and should be re-homed onto the
modern ``Agent`` abstraction and PyTorch incrementally.

The bundled sprite assets under ``files/data`` (minimap cell templates) are kept
for that future port. ``handle_play`` is a no-op placeholder for now.
"""

from serpent.game_agent import GameAgent


class BindingOfIsaacRebirthGameAgent(GameAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play
        self.frame_handler_setups["PLAY"] = self.setup_play

    def setup_play(self):
        # TODO: port minimap/room parsing + the RL policy from `master` (see module docstring).
        self.game_inputs = self.game.api.game_inputs

    def handle_play(self, game_frame, game_frame_pipeline, **kwargs):
        # TODO: implement the ported Isaac agent policy.
        pass
