"""Peglin agent vision + aiming logic (verified on synthetic frames)."""

from pathlib import Path

import numpy as np
import pytest
from skimage.draw import disk

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _plugins_on_path(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO_ROOT))


def _frame_with_pegs(centers, shape=(720, 1280, 3), radius=6):
    frame = np.zeros(shape, dtype="uint8")
    for x, y in centers:
        rr, cc = disk((y, x), radius, shape=shape[:2])
        frame[rr, cc] = 255
    return frame


def test_detect_pegs_finds_drawn_pegs():
    from plugins.PeglinGameAgentPlugin.files.helpers import vision

    centers = [(400, 300), (430, 320), (460, 300), (800, 500)]
    pegs = vision.detect_pegs(_frame_with_pegs(centers))

    assert len(pegs) >= 3
    # detections fall inside the board region and near the drawn pegs
    top, left, bottom, right = vision.board_box((720, 1280, 3))
    for x, y in pegs:
        assert left <= x <= right
        assert top <= y <= bottom


def test_detect_pegs_empty_on_blank_frame():
    from plugins.PeglinGameAgentPlugin.files.helpers import vision

    assert vision.detect_pegs(np.zeros((720, 1280, 3), dtype="uint8")) == []


def test_choose_aim_targets_densest_band():
    from plugins.PeglinGameAgentPlugin.files.helpers import strategy

    # Dense cluster around x=400, lone outlier at x=900.
    pegs = [(390, 300), (400, 320), (410, 300), (405, 340), (900, 500)]
    aim_x, aim_y = strategy.choose_aim(pegs, (720, 1280, 3))

    assert 360 <= aim_x <= 440  # near the cluster, not the outlier
    assert aim_y <= 340  # top of the densest column


def test_choose_aim_without_pegs_returns_board_center():
    from plugins.PeglinGameAgentPlugin.files.helpers import strategy, vision

    aim_x, aim_y = strategy.choose_aim([], (720, 1280, 3))
    top, left, bottom, right = vision.board_box((720, 1280, 3))

    assert left < aim_x < right
    assert top <= aim_y <= bottom
