"""The Redis input bridge: ClientInputController -> redis_input_controller_worker.

These lock the wire contract that replaced WAMP/crossbar in Phase D. The client
pickles ``(func_name, *args, kwargs)`` onto a Redis list; the worker unpacks with
``func_name, *args, kwargs = pickle.loads(payload)`` and dispatches to a real
InputController. We verify a client call survives that round-trip as the same
method call.
"""

import pickle
from unittest.mock import MagicMock

from serpent.input_controllers.client_input_controller import ClientInputController


class _CapturingRedis:
    def __init__(self):
        self.items = []

    def lpush(self, key, value):
        self.items.append(value)


def _dispatch(call):
    """Run a ClientInputController call, then replay its payload onto a mock."""
    client = ClientInputController(game=None)
    client.redis_client = _CapturingRedis()

    call(client)

    func_name, *args, kwargs = pickle.loads(client.redis_client.items[0])

    target = MagicMock()
    getattr(target, func_name)(*args, **kwargs)
    return target


def test_press_key_roundtrips():
    target = _dispatch(lambda c: c.press_key("a", duration=0.1))
    target.press_key.assert_called_once_with("a", duration=0.1)


def test_move_roundtrips():
    target = _dispatch(lambda c: c.move(10, 20))
    target.move.assert_called_once_with(10, 20, 0.25, True)


def test_tap_keys_roundtrips():
    target = _dispatch(lambda c: c.tap_keys(["a", "b"], duration=0.2))
    target.tap_keys.assert_called_once_with(["a", "b"], 0.2)
