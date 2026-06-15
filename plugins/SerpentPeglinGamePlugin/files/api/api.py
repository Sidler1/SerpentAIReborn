from serpent.game_api import GameAPI


class PeglinAPI(GameAPI):
    """Peglin is mouse-aimed (move to aim, left-click to fire), so there is no
    fixed discrete keyboard action set. ``game_inputs`` is left empty and the
    agent drives the mouse directly; game-specific helpers (board/HP parsing,
    aim math) belong here as they are added.
    """

    def __init__(self, game=None):
        super().__init__(game=game)

        self.game_inputs = {}
