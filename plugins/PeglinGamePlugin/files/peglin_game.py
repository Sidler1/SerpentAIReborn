from serpent.game import Game
from serpent.utilities import Singleton

from .api.api import PeglinAPI


class PeglinGame(Game, metaclass=Singleton):
    """Peglin (Steam app 1296610) — a pachinko/peggle roguelike.

    Combat is mouse-aimed: move the cursor to aim the orb's launch trajectory and
    left-click to fire; the orb bounces off pegs to deal damage. The agent drives
    the mouse directly (see PeglinGameAgent).
    """

    def __init__(self, **kwargs):
        kwargs["platform"] = "steam"
        kwargs["app_id"] = "1296610"
        kwargs["app_args"] = None

        # Verify with `serpent window-name` if window discovery fails.
        kwargs["window_name"] = "Peglin"

        super().__init__(**kwargs)

        self.api_class = PeglinAPI
        self.api_instance = None

    @property
    def screen_regions(self):
        # PLACEHOLDER regions (top, left, bottom, right) — calibrate to your
        # resolution/layout, e.g. with `serpent capture region Peglin`. They are
        # not required by the bundled reference agent (which uses window geometry).
        return {
            "ENEMY_AREA": (0, 0, 0, 0),
            "PEG_BOARD": (0, 0, 0, 0),
            "PLAYER_HP": (0, 0, 0, 0),
            "ENEMY_HP": (0, 0, 0, 0),
            "ORB_COUNT": (0, 0, 0, 0),
        }
