import os
import sys
import subprocess

import enum


class SerpentError(Exception):
    pass


class OperatingSystem(enum.Enum):
    LINUX = 0
    WINDOWS = 1


def operating_system():
    if sys.platform in ["linux", "linux2"]:
        return OperatingSystem.LINUX
    elif sys.platform == "win32":
        return OperatingSystem.WINDOWS


def is_linux():
    return operating_system().name == "LINUX"


def is_windows():
    return operating_system().name == "WINDOWS"


def is_wayland():
    """True when running under a Wayland session (regardless of XWayland)."""
    return os.environ.get("XDG_SESSION_TYPE") == "wayland" or bool(os.environ.get("WAYLAND_DISPLAY"))


def is_x11_available():
    """True when an X server is reachable — native X11 or XWayland (``$DISPLAY`` set).

    The current Linux capture/input/window backends speak X11, so on a Wayland
    session they require XWayland (which exposes ``$DISPLAY``). Native-Wayland
    backends (PipeWire capture, ydotool input, KWin window control) are a planned
    addition; see MODERNIZATION.md Phase F.
    """
    return bool(os.environ.get("DISPLAY"))


def clear_terminal():
    if is_linux():
        print("\033c")
    elif is_windows():
        subprocess.call(["cls"], shell=True)


def display_serpent_logo():
    print("""
                         ▄▄▄▄█████▄▄▄
                     ▄█████████▀▀`  ,
                  ▄██████████",▄▄▄██  █ L
                ╓██████████▀╓█████▀  ██ ▌ j
               ▄██████████▀▄███▀▀ ▄███ █▌ ▐▌
              ▐██████████   ▄▄▄█████▀╓██  ██
              █████████▀▄▄███████▀`▄███` ██▌▐U
              ███████▀,███▀▀▀` ▄▄████▀ ,███ █`╒
              ▀▀▐▄▄   `     ╓██████▀  ▄███ ██ █
                          ▄████▀▀-  ▄███▀╓██-▐█
                      ^▀▀▀▀▀- ,▄██  ██▀,███`╒██
                            ▐████" ▀▀▄████ ▄██▌
                            ▐███▀ ,▄████▀ ▄██▌
                            ███▀ ╓████" ▄███▀
                           ▐██  ▄██▀ ,▄████▀
                          ▄█▀ ,▀▀ ▄▄█████▀
                        .▀   ,▄▄███████▀          ,    ,
                       ,▄▄▄█████████▀-           ███  ▐█
                 ,▄▄████████████▀▀              ██ █▌ ▐█
             ▄▄███████████▀▀▀                  ▄█▀▀▀█▄▐█
          ▄███████▀▀▀                          ``      `
       ,▄███▀▀'
      ▄██▀
     █▀`
    ▐▀
    `
    """)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
