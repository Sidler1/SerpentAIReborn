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
        # (top, left, bottom, right) for a 1280x720 *windowed* game. PEG_BOARD
        # mirrors helpers/vision.DEFAULT_BOARD; the rest are best-guess starting
        # points — calibrate with `serpent capture region Peglin` once running.
        return {
            "ENEMY_AREA": (0, 256, 108, 1024),   # enemies across the top
            "PEG_BOARD": (108, 256, 648, 1024),  # central peg field (agent's board)
            "PLAYER_HP": (650, 0, 720, 320),     # bottom-left HUD
            "ENEMY_HP": (0, 256, 40, 1024),      # enemy health bars
            "ORB_COUNT": (650, 960, 720, 1280),  # bottom-right HUD
        }
