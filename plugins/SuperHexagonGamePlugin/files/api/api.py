from serpent.game_api import GameAPI
from serpent.input_controller import KeyboardEvent, KeyboardEvents, KeyboardKey


class SuperHexagonAPI(GameAPI):
    """Super Hexagon is a one-axis reflex game: rotate the cursor left or right."""

    def __init__(self, game=None):
        super().__init__(game=game)

        self.game_inputs = {
            "ROTATE": {
                "ROTATE LEFT": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT)],
                "ROTATE RIGHT": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_RIGHT)],
                "DON'T ROTATE": [],
            }
        }
