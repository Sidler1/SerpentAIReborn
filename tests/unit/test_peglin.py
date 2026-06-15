"""Peglin agent vision + aiming logic (verified on synthetic frames)."""

from pathlib import Path

import numpy as np
import pytest
from skimage.draw import disk

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _plugins_on_path(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO_ROOT))


def _frame_with_pegs(centers, shape=(720, 1280, 3), radius=7, color=(255, 255, 255)):
    frame = np.zeros(shape, dtype="uint8")
    for x, y in centers:
        rr, cc = disk((y, x), radius, shape=shape[:2])
        frame[rr, cc] = color
    return frame


def test_detect_pegs_finds_drawn_pegs():
    from plugins.PeglinGameAgentPlugin.files.helpers import vision

    centers = [(500, 280), (560, 300), (620, 280), (800, 460)]
    pegs = vision.detect_pegs(_frame_with_pegs(centers))

    assert len(pegs) >= 3
    top, left, bottom, right = vision.board_box((720, 1280, 3))
    for x, y, kind in pegs:
        assert left <= x <= right
        assert top <= y <= bottom
        assert kind in {"normal", "special", "crit"}


def test_detect_pegs_classifies_green_as_special():
    from plugins.PeglinGameAgentPlugin.files.helpers import vision

    frame = _frame_with_pegs([(560, 300)], color=(60, 200, 80))
    pegs = vision.detect_pegs(frame)

    assert pegs and pegs[0][2] == "special"


def test_detect_pegs_empty_on_blank_frame():
    from plugins.PeglinGameAgentPlugin.files.helpers import vision

    assert vision.detect_pegs(np.zeros((720, 1280, 3), dtype="uint8")) == []


def test_choose_aim_targets_densest_band():
    from plugins.PeglinGameAgentPlugin.files.helpers import strategy

    pegs = [(490, 300, "normal"), (500, 320, "normal"), (510, 300, "normal"), (900, 500, "normal")]
    aim_x, aim_y = strategy.choose_aim(pegs, (720, 1280, 3))

    assert 470 <= aim_x <= 530
    assert aim_y <= 320


def test_choose_aim_prioritizes_special_pegs():
    from plugins.PeglinGameAgentPlugin.files.helpers import strategy

    # Many normal pegs on the left, a single special peg far right -> aim right.
    pegs = [(450, 300, "normal"), (460, 320, "normal"), (470, 300, "normal"), (900, 480, "special")]
    aim_x, _ = strategy.choose_aim(pegs, (720, 1280, 3))

    assert aim_x >= 850  # targets the special peg's column, not the normal cluster


def test_choose_aim_without_pegs_returns_board_center():
    from plugins.PeglinGameAgentPlugin.files.helpers import strategy, vision

    aim_x, aim_y = strategy.choose_aim([], (720, 1280, 3))
    top, left, bottom, right = vision.board_box((720, 1280, 3))

    assert left < aim_x < right
    assert top <= aim_y <= bottom
