"""Tests for the pluggable transport (Phase E)."""

import threading
import time

import numpy as np

import serpent.frame_grabber as frame_grabber_module
from serpent.config import config
from serpent.frame_grabber import FrameGrabber
from serpent.transport.in_process_transport import InProcessTransport


def test_list_semantics_match_redis():
    t = InProcessTransport()

    t.lpush("k", b"a")
    t.lpush("k", "b")  # str is encoded to bytes, like redis-py

    assert t.llen("k") == 2
    assert t.lindex("k", 0) == b"b"  # lpush prepends
    assert t.lindex("k", -1) == b"a"
    assert t.rpop("k") == b"a"
    assert t.lpop("k") == b"b"
    assert t.llen("k") == 0
    assert t.lpop("k") is None


def test_ltrim_keeps_inclusive_range():
    t = InProcessTransport()
    t.rpush("buf", "0", "1", "2", "3", "4")
    t.ltrim("buf", 0, 2)
    assert [t.lindex("buf", i) for i in range(t.llen("buf"))] == [b"0", b"1", b"2"]


def test_string_keys_and_delete():
    t = InProcessTransport()
    t.set("SERPENT:GAME", "MyGame")
    assert t.get("SERPENT:GAME") == b"MyGame"
    assert sorted(t.keys()) == [b"SERPENT:GAME"]
    assert t.delete("SERPENT:GAME") == 1
    assert t.get("SERPENT:GAME") is None


def test_brpop_returns_pair_and_times_out():
    t = InProcessTransport()
    t.rpush("q", b"x")
    assert t.brpop("q") == (b"q", b"x")
    assert t.brpop("missing", timeout=0.05) is None


def test_brpop_blocks_until_pushed():
    t = InProcessTransport()

    def producer():
        time.sleep(0.05)
        t.rpush("q", b"ready")

    threading.Thread(target=producer, daemon=True).start()
    assert t.brpop("q", timeout=2) == (b"q", b"ready")


def test_frame_roundtrips_through_get_frames(monkeypatch):
    transport = InProcessTransport()
    monkeypatch.setattr(frame_grabber_module, "transport", transport)

    array = (np.arange(2 * 2 * 3) % 256).astype("uint8").reshape(2, 2, 3)
    shape = str(array.shape).replace("(", "").replace(")", "")
    payload = f"1.0~{shape}~uint8~".encode() + array.tobytes()

    redis_key = config["frame_grabber"]["redis_key"]
    for _ in range(151):  # get_frames waits until the buffer holds > 149 frames
        transport.lpush(redis_key, payload)

    buffer = FrameGrabber.get_frames([0])
    game_frame = buffer.frames[0]

    assert game_frame.frame.shape == (2, 2, 3)
    assert game_frame.frame.dtype == np.uint8
    assert game_frame.timestamp == 1.0
    assert np.array_equal(game_frame.frame, array)
