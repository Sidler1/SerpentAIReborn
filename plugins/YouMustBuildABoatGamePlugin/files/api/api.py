from serpent.game_api import GameAPI


class YouMustBuildABoatAPI(GameAPI):
    """You Must Build A Boat is a match-3 played by dragging tiles with the mouse.

    Inputs are board-coordinate drags rather than a fixed keyboard map, so the
    concrete action set is produced by the (not-yet-ported) agent from the parsed
    board. ``game_inputs`` is left empty here; see the agent scaffold.
    """

    def __init__(self, game=None):
        super().__init__(game=game)

        self.game_inputs = {}
