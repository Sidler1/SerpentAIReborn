from serpent.game import Game
from serpent.utilities import Singleton

from .api.api import SuperHexagonAPI


class SuperHexagonGame(Game, metaclass=Singleton):
    def __init__(self, **kwargs):
        kwargs["platform"] = "steam"
        kwargs["app_id"] = "221640"
        kwargs["app_args"] = None

        kwargs["window_name"] = "Super Hexagon"

        super().__init__(**kwargs)

        self.api_class = SuperHexagonAPI
        self.api_instance = None

    @property
    def screen_regions(self):
        return {
            "SPLASH_ACTIONS": (349, 260, 391, 507),
            "GAME_HUD_TIME": (0, 562, 52, 768),
            "GAME_PLAYER_AREA": (129, 264, 366, 513),
            "DEATH_TIME_LAST": (158, 600, 207, 768),
        }
