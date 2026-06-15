"""ScreenCapture backend selection + spectacle crop (CI-safe, no display)."""

import numpy as np
from PIL import Image

import serpent.screen_capture as sc


def test_backend_selection(monkeypatch):
    monkeypatch.setattr(sc, "_spectacle_available", lambda: True)

    monkeypatch.setattr(sc, "is_wayland", lambda: True)
    assert sc.ScreenCapture().backend == "spectacle"

    monkeypatch.setattr(sc, "is_wayland", lambda: False)
    assert sc.ScreenCapture().backend == "mss"


def test_spectacle_grab_crops_region(monkeypatch):
    monkeypatch.setattr(sc, "is_wayland", lambda: True)
    monkeypatch.setattr(sc, "_spectacle_available", lambda: True)

    capture = sc.ScreenCapture()
    full = (np.arange(200 * 300 * 3) % 256).astype("uint8").reshape(200, 300, 3)

    def fake_run(cmd, **kwargs):
        Image.fromarray(full).save(capture._spectacle_path)

    monkeypatch.setattr(sc.subprocess, "run", fake_run)

    region = capture.grab(top=10, left=20, width=100, height=50)

    assert region.shape == (50, 100, 3)
    assert np.array_equal(region, full[10:60, 20:120])
