"""You Must Build A Boat game agent — modern-API scaffold.

This plugin loads and validates against the modern Serpent API, but the
game-specific intelligence is NOT yet ported. The 2017 prototype shipped a large
agent (~23 KB) with board parsing, OCR, and an sklearn/Keras match-scoring model;
that logic lives in git history on the ``master`` branch
(``plugins/YouMustBuildABoatGameAgentPlugin``) and should be re-homed onto the
modern stack incrementally.

The bundled tile sprites under the GamePlugin's ``files/data/sprites`` are kept
for that future port. ``handle_play`` is a no-op placeholder for now.
"""

from serpent.game_agent import GameAgent


class YouMustBuildABoatGameAgent(GameAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play
        self.frame_handler_setups["PLAY"] = self.setup_play

    def setup_play(self):
        # TODO: port board parsing + tile sprite identification + match scoring from `master`.
        pass

    def handle_play(self, game_frame, game_frame_pipeline, **kwargs):
        # TODO: implement the ported YMBAB agent policy (mouse-drag tile swaps).
        pass
