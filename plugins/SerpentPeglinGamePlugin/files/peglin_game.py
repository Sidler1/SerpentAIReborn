from serpent.game import Game
from serpent.utilities import Singleton

from .api.api import PeglinAPI


class SerpentPeglinGame(Game, metaclass=Singleton):
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
        # (top, left, bottom, right), calibrated to a 1280x720 *windowed* Forest
        # combat frame. PEG_BOARD matches helpers/vision.DEFAULT_BOARD.
        return {
            "ENEMY_AREA": (0, 0, 210, 1280),       # forest band: enemies + player
            "PEG_BOARD": (216, 416, 590, 1011),    # dark-blue peg field
            "PLAYER_HP": (232, 128, 270, 308),     # "100/100" bar, left panel
            "ENEMY_HP": (118, 895, 152, 1075),     # enemy "60/60" bars, top-right
            "ORB_INFO": (300, 90, 520, 310),       # current-orb parchment
            "UPCOMING_ENEMIES": (290, 1045, 440, 1235),
        }
