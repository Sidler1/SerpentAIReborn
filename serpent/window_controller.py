import warnings

from serpent.utilities import is_linux, is_wayland, is_windows, is_x11_available


class WindowControllerError(Exception):
    pass


class WindowController:

    def __init__(self):
        self.adapter = self._load_adapter()()

    def locate_window(self, name):
        return self.adapter.locate_window(name)

    def move_window(self, window_id, x, y):
        self.adapter.move_window(window_id, x, y)

    def resize_window(self, window_id, width, height):
        self.adapter.resize_window(window_id, width, height)

    def focus_window(self, window_id):
        self.adapter.focus_window(window_id)

    def bring_window_to_top(self, window_id):
        self.adapter.bring_window_to_top(window_id)

    def is_window_focused(self, window_id):
        return self.adapter.is_window_focused(window_id)

    def get_focused_window_name(self):
        return self.adapter.get_focused_window_name()

    def get_window_geometry(self, window_id):
        return self.adapter.get_window_geometry(window_id)

    def _load_adapter(self):
        if is_linux():
            # The Linux backend speaks X11; on Wayland it drives XWayland windows
            # (how Steam/Proton games run). It needs an X server ($DISPLAY); a pure
            # Wayland session with no XWayland can't be driven yet — native-Wayland
            # backends (KWin/kdotool, ydotool, PipeWire) are a planned addition.
            if is_wayland() and not is_x11_available():
                raise WindowControllerError(
                    "Running under Wayland with no XWayland ($DISPLAY unset). The current "
                    "window/input/capture backends require X11/XWayland. Start the game as an "
                    "XWayland window, or wait for the native-Wayland backends (MODERNIZATION.md "
                    "Phase F)."
                )

            if is_wayland():
                warnings.warn(
                    "Wayland session detected; using the X11/XWayland backend. Only XWayland "
                    "windows are supported (native-Wayland support is planned).",
                    stacklevel=2,
                )

            from serpent.window_controllers.linux_window_controller import LinuxWindowController
            return LinuxWindowController
        elif is_windows():
            from serpent.window_controllers.win32_window_controller import Win32WindowController
            return Win32WindowController
