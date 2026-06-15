"""Native-Wayland window controller — placeholder seam (not yet implemented).

Wayland deliberately prevents clients from enumerating, moving, or focusing other
windows, so native window control is compositor-specific. On KDE Plasma the path
is KWin scripting over D-Bus (or the `kdotool` helper); wlroots compositors use
the foreign-toplevel protocol; etc.

Until that lands, Serpent drives **XWayland** windows through
:class:`~serpent.window_controllers.linux_window_controller.LinuxWindowController`
(xdotool), which covers the common case of Steam/Proton games. This class exists
to mark the extension point and keep the dispatch contract explicit; see
ROADMAP.md.
"""

from serpent.window_controller import WindowController, WindowControllerError

_NOT_IMPLEMENTED = (
    "Native-Wayland window control is not implemented yet. Run the game as an "
    "XWayland window (LinuxWindowController), or contribute a KWin/kdotool backend "
    "(ROADMAP.md)."
)


class WaylandWindowController(WindowController):
    def __init__(self):
        pass

    def locate_window(self, name):
        raise WindowControllerError(_NOT_IMPLEMENTED)

    def move_window(self, window_id, x, y):
        raise WindowControllerError(_NOT_IMPLEMENTED)

    def resize_window(self, window_id, width, height):
        raise WindowControllerError(_NOT_IMPLEMENTED)

    def focus_window(self, window_id):
        raise WindowControllerError(_NOT_IMPLEMENTED)

    def bring_window_to_top(self, window_id):
        raise WindowControllerError(_NOT_IMPLEMENTED)

    def is_window_focused(self, window_id):
        raise WindowControllerError(_NOT_IMPLEMENTED)

    def get_focused_window_name(self):
        raise WindowControllerError(_NOT_IMPLEMENTED)

    def get_window_geometry(self, window_id):
        raise WindowControllerError(_NOT_IMPLEMENTED)
