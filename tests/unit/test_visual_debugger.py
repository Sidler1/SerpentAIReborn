"""Phase H: modern visual debugger (transport producer + FastAPI viewer)."""

import numpy as np
import pytest
from fastapi.testclient import TestClient

import serpent.transport as transport_module
from serpent.transport.in_process_transport import InProcessTransport
from serpent.visual_debugger.server import create_app, to_png_bytes
from serpent.visual_debugger.visual_debugger import VisualDebugger


@pytest.fixture
def in_process_transport(monkeypatch):
    transport = InProcessTransport()
    monkeypatch.setattr(transport_module, "_TRANSPORT", transport)
    return transport


def _frame():
    return (np.arange(4 * 4 * 3) % 256).astype("uint8").reshape(4, 4, 3)


def test_producer_store_and_peek_roundtrip(in_process_transport):
    debugger = VisualDebugger(buckets=["0", "1"])
    frame = _frame()

    debugger.store_image_data(frame, frame.shape, bucket="0")
    peeked = debugger.peek_image_data("0")

    assert peeked.shape == (4, 4, 3)
    assert peeked.dtype == np.uint8
    assert np.array_equal(peeked, frame)
    assert debugger.peek_image_data("1") is None  # untouched bucket


def test_to_png_bytes_handles_dtypes():
    assert to_png_bytes(_frame()).startswith(b"\x89PNG")
    assert to_png_bytes(np.zeros((4, 4), dtype=bool)).startswith(b"\x89PNG")
    assert to_png_bytes(np.ones((4, 4, 3), dtype="float64")).startswith(b"\x89PNG")


def test_server_page_and_bucket_image(in_process_transport):
    app = create_app(buckets=["0"])
    client = TestClient(app)

    page = client.get("/")
    assert page.status_code == 200
    assert "Visual Debugger" in page.text

    # Empty bucket -> placeholder PNG
    empty = client.get("/bucket/0.png")
    assert empty.status_code == 200
    assert empty.headers["content-type"] == "image/png"

    # Store a real frame (same in-process transport) -> served as PNG
    VisualDebugger(buckets=["0"], clear=False).store_image_data(
        _frame(), _frame().shape, bucket="0"
    )
    served = client.get("/bucket/0.png")
    assert served.status_code == 200
    assert served.content.startswith(b"\x89PNG")
