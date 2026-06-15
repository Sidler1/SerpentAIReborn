"""Phase F: XWayland-first window controller + display detection."""

import pytest

from serpent import utilities
from serpent.window_controller import WindowController, WindowControllerError
from serpent.window_controllers.linux_window_controller import LinuxWindowController
from serpent.window_controllers.wayland_window_controller import WaylandWindowController

SHELL_GEOMETRY = "WINDOW=29360135\nX=120\nY=64\nWIDTH=1280\nHEIGHT=720\nSCREEN=0\n"


def test_parse_geometry_replaces_xwininfo():
    assert LinuxWindowController._parse_geometry(SHELL_GEOMETRY) == {
        "width": 1280,
        "height": 720,
        "x_offset": 120,
        "y_offset": 64,
    }


def test_is_wayland_detection(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    assert utilities.is_wayland() is True

    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    assert utilities.is_wayland() is False


def test_is_x11_available_follows_display(monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    assert utilities.is_x11_available() is True

    monkeypatch.delenv("DISPLAY", raising=False)
    assert utilities.is_x11_available() is False


@pytest.mark.skipif(not utilities.is_linux(), reason="Linux dispatch path")
def test_dispatch_errors_on_wayland_without_xwayland(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)

    with pytest.raises(WindowControllerError, match="XWayland"):
        WindowController()


@pytest.mark.skipif(not utilities.is_linux(), reason="Linux dispatch path")
def test_dispatch_uses_xwayland_backend_with_warning(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("DISPLAY", ":0")

    with pytest.warns(UserWarning, match="XWayland"):
        controller = WindowController()

    assert isinstance(controller.adapter, LinuxWindowController)


def test_native_wayland_controller_is_a_documented_stub():
    controller = WaylandWindowController()
    with pytest.raises(WindowControllerError, match="not implemented"):
        controller.locate_window("Game")
