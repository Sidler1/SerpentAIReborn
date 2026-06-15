"""Screen capture with a Wayland-aware backend.

``mss`` (XGetImage) is unreliable under Wayland/XWayland — on KDE it raises an X11
BadMatch — so on a Wayland session we capture via a compositor tool instead:

- **spectacle** (KDE): grab the full desktop to a PNG, then crop to the region.
- **mss** (native X11): fast in-process region grab.

Regions are root/virtual-screen absolute ``(top, left, width, height)`` — the same
coordinate space xdotool reports for window geometry, so cropping the full-desktop
screenshot lines up with the window.

A native PipeWire/portal backend (continuous, faster) is the longer-term path; see
ROADMAP.md.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image

from serpent.utilities import is_wayland


class ScreenCaptureError(Exception):
    pass


def _spectacle_available():
    return shutil.which("spectacle") is not None


class ScreenCapture:
    def __init__(self):
        self.backend = "spectacle" if (is_wayland() and _spectacle_available()) else "mss"
        self._mss = None
        self._spectacle_path = os.path.join(
            tempfile.gettempdir(), f"serpent_capture_{os.getpid()}.png"
        )

    def grab(self, top, left, width, height):
        """Return an ``(height, width, 3)`` uint8 RGB array of the region."""
        if self.backend == "spectacle":
            return self._grab_spectacle(top, left, width, height)

        try:
            return self._grab_mss(top, left, width, height)
        except Exception as error:
            # mss can fail under XWayland; fall back to spectacle if we can.
            if _spectacle_available():
                self.backend = "spectacle"
                return self._grab_spectacle(top, left, width, height)
            raise ScreenCaptureError(f"Screen capture failed: {error}") from error

    def _grab_mss(self, top, left, width, height):
        import mss

        if self._mss is None:
            self._mss = mss.mss()

        raw = np.array(
            self._mss.grab({"top": top, "left": left, "width": width, "height": height}),
            dtype="uint8",
        )
        return raw[..., [2, 1, 0, 3]][..., :3]  # BGRA -> RGB

    def _grab_spectacle(self, top, left, width, height):
        subprocess.run(
            ["spectacle", "-b", "-n", "-f", "-o", self._spectacle_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        full = np.asarray(Image.open(self._spectacle_path).convert("RGB"), dtype="uint8")
        return full[top : top + height, left : left + width]


__all__ = ["ScreenCapture", "ScreenCaptureError"]
