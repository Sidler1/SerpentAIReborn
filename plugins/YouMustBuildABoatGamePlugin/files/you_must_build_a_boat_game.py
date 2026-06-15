from serpent.game import Game
from serpent.utilities import Singleton

from .api.api import YouMustBuildABoatAPI


class YouMustBuildABoatGame(Game, metaclass=Singleton):
    def __init__(self, **kwargs):
        kwargs["platform"] = "steam"
        kwargs["app_id"] = "290890"
        kwargs["app_args"] = None

        kwargs["window_name"] = "#ymbab"

        super().__init__(**kwargs)

        self.api_class = YouMustBuildABoatAPI
        self.api_instance = None

    @property
    def screen_regions(self):
        regions = {
            "MENU_CONTINUE": (287, 351, 342, 620),
            "MENU_NEW_GAME": (350, 376, 385, 595),
            "MENU_LOAD_GAME": (394, 376, 429, 595),
            "MENU_SETTINGS": (438, 376, 473, 595),
            "MENU_QUIT": (482, 376, 517, 595),
            "GAME_OVER_RUN_AGAIN": (600, 250, 673, 509),
        }

        # The match-3 board is a 6x8 grid of 84px tiles; generate a region per cell.
        rows = ["A", "B", "C", "D", "E", "F"]
        columns = [1, 2, 3, 4, 5, 6, 7, 8]

        start_x = 348
        start_y = 197

        for i, row in enumerate(rows):
            for ii, column in enumerate(columns):
                regions[f"GAME_BOARD_{row}{column}"] = (
                    start_y + (i * 84),
                    start_x + (ii * 84),
                    start_y + 79 + (i * 84),
                    start_x + 79 + (ii * 84),
                )

        return regions
