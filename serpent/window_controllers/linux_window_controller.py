from serpent.window_controller import WindowController

import subprocess
import shlex


class LinuxWindowController(WindowController):
    """X11 / XWayland window control via xdotool.

    Works for native-X11 windows and, on a Wayland session, for XWayland windows
    (which is how Steam/Proton games typically run). Native-Wayland window control
    (KWin/kdotool) is a planned addition — see ROADMAP.md.
    """

    def __init__(self):
        pass

    def locate_window(self, name):
        # xdotool exits non-zero when nothing matches; return the "not found"
        # sentinel "0" (callers treat 0/"0" as missing) instead of raising, and
        # return only the first match if several windows share the title.
        try:
            output = subprocess.check_output(
                shlex.split(f'xdotool search --onlyvisible --name "^{name}$"'),
                stderr=subprocess.DEVNULL,
            ).decode("utf-8").strip()
        except subprocess.CalledProcessError:
            return "0"

        return output.split("\n")[0].strip() or "0"

    def move_window(self, window_id, x, y):
        subprocess.call(shlex.split(f"xdotool windowmove {window_id} {x} {y}"))

    def resize_window(self, window_id, width, height):
        subprocess.call(shlex.split(f"xdotool windowsize {window_id} {width} {height}"))

    def focus_window(self, window_id):
        subprocess.call(shlex.split(f"xdotool windowactivate {window_id}"))

    def bring_window_to_top(self, window_id):
        subprocess.call(shlex.split(f"xdotool windowactivate {window_id}"))

    def is_window_focused(self, window_id):
        focused_window_id = subprocess.check_output(shlex.split("xdotool getwindowfocus")).decode("utf-8").strip()
        return focused_window_id == window_id

    def get_focused_window_name(self):
        focused_window_id = subprocess.check_output(shlex.split("xdotool getwindowfocus")).decode("utf-8").strip()
        return subprocess.check_output(shlex.split(f"xdotool getwindowname {focused_window_id}")).decode("utf-8").strip()

    def get_window_geometry(self, window_id):
        # `xdotool getwindowgeometry --shell` reports absolute X/Y plus WIDTH/HEIGHT
        # in one call, so we no longer need xwininfo (which isn't always installed,
        # and is absent under a minimal Wayland/KDE setup).
        output = subprocess.check_output(
            shlex.split(f"xdotool getwindowgeometry --shell {window_id}")
        ).decode("utf-8")

        return self._parse_geometry(output)

    @staticmethod
    def _parse_geometry(shell_output):
        values = {}

        for line in shell_output.strip().splitlines():
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()

        return {
            "width": int(values["WIDTH"]),
            "height": int(values["HEIGHT"]),
            "x_offset": int(values["X"]),
            "y_offset": int(values["Y"]),
        }
