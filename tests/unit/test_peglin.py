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
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import vision

    centers = [(500, 280), (560, 300), (620, 280), (800, 460)]
    pegs = vision.detect_pegs(_frame_with_pegs(centers))

    assert len(pegs) >= 3
    top, left, bottom, right = vision.board_box((720, 1280, 3))
    for x, y, kind in pegs:
        assert left <= x <= right
        assert top <= y <= bottom
        assert kind in {"normal", "refresh", "crit"}


def test_detect_pegs_classifies_green_as_refresh():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import vision

    frame = _frame_with_pegs([(560, 300)], color=(60, 200, 60))
    pegs = vision.detect_pegs(frame)

    assert pegs and pegs[0][2] == "refresh"


def test_detect_pegs_classifies_orange_as_crit():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import vision

    frame = _frame_with_pegs([(560, 300)], color=(255, 150, 20))
    pegs = vision.detect_pegs(frame)

    assert pegs and pegs[0][2] == "crit"


def test_detect_pegs_empty_on_blank_frame():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import vision

    assert vision.detect_pegs(np.zeros((720, 1280, 3), dtype="uint8")) == []


def test_choose_aim_targets_densest_band():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import strategy

    pegs = [(490, 300, "normal"), (500, 320, "normal"), (510, 300, "normal"), (900, 500, "normal")]
    aim_x, aim_y = strategy.choose_aim(pegs, (720, 1280, 3))

    assert 470 <= aim_x <= 530
    assert aim_y <= 320


def test_choose_aim_prioritizes_crit_pegs():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import strategy

    # Many normal pegs on the left, a single crit peg far right -> aim right.
    pegs = [(450, 300, "normal"), (460, 320, "normal"), (470, 300, "normal"), (900, 480, "crit")]
    aim_x, aim_y = strategy.choose_aim(pegs, (720, 1280, 3))

    assert aim_x >= 850  # targets the crit peg, not the normal cluster
    assert aim_y == 480


def test_choose_aim_targets_topmost_crit_peg():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import strategy

    pegs = [(500, 500, "crit"), (520, 300, "crit"), (510, 400, "crit")]
    _, aim_y = strategy.choose_aim(pegs, (720, 1280, 3))

    assert aim_y == 300  # the highest crit peg, so the whole chain crits


def test_choose_aim_targets_refresh_when_board_thin():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import strategy

    # Few pegs left, a refresh peg present -> aim at it to extend the shot.
    pegs = [(450, 400, "normal"), (900, 300, "refresh")]
    aim_x, aim_y = strategy.choose_aim(pegs, (720, 1280, 3))

    assert (aim_x, aim_y) == (900, 300)


def test_choose_aim_ignores_refresh_when_board_full():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import strategy

    # A full board: a lone refresh peg should NOT pull aim off the dense cluster.
    cluster = [(500 + i % 3 * 10, 300 + i * 5, "normal") for i in range(12)]
    pegs = cluster + [(950, 600, "refresh")]
    aim_x, _ = strategy.choose_aim(pegs, (720, 1280, 3))

    assert aim_x < 600


def test_detect_reward_items_finds_item_row():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import vision

    frame = np.zeros((720, 1280, 3), dtype="uint8")
    # three bright item blobs across the reward row (~y=225)
    for cx in (392, 556, 884):
        frame[205:245, cx - 30:cx + 30] = (255, 230, 200)

    items = vision.detect_reward_items(frame)

    assert len(items) == 3
    xs = [x for x, _ in items]
    assert xs == sorted(xs)  # returned left to right


def test_choose_aim_without_pegs_returns_board_center():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import strategy, vision

    aim_x, aim_y = strategy.choose_aim([], (720, 1280, 3))
    top, left, bottom, right = vision.board_box((720, 1280, 3))

    assert left < aim_x < right
    assert top <= aim_y <= bottom


def test_find_continue_button_detects_green_button():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import navigation

    frame = np.zeros((720, 1280, 3), dtype="uint8")
    # large muted-green button in the lower-centre
    frame[600:650, 575:705] = (81, 113, 50)

    button = navigation.find_continue_button(frame)
    assert button is not None
    x, y = button
    assert 575 <= x <= 705
    assert 600 <= y <= 650


def test_find_continue_button_ignores_small_green_pegs():
    from plugins.SerpentPeglinGameAgentPlugin.files.helpers import navigation

    frame = np.zeros((720, 1280, 3), dtype="uint8")
    # a small green peg-sized blob is not a button
    frame[300:312, 560:572] = (60, 200, 80)

    assert navigation.find_continue_button(frame) is None
