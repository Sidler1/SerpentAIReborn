from serpent.game_api import GameAPI
from serpent.input_controller import KeyboardEvent, KeyboardEvents, KeyboardKey


class BindingOfIsaacRebirthAPI(GameAPI):
    """Isaac: move with WASD, shoot tears with the arrow keys."""

    def __init__(self, game=None):
        super().__init__(game=game)

        self.game_inputs = {
            "MOVEMENT": {
                "MOVE UP": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_W)],
                "MOVE LEFT": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)],
                "MOVE DOWN": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_S)],
                "MOVE RIGHT": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)],
                "DON'T MOVE": [],
            },
            "SHOOTING": {
                "SHOOT UP": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_UP)],
                "SHOOT LEFT": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT)],
                "SHOOT DOWN": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_DOWN)],
                "SHOOT RIGHT": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_RIGHT)],
                "DON'T SHOOT": [],
            },
        }
