import pickle

from serpent.transport import get_transport

import offshoot

from serpent.config import config
from serpent.input_controller import InputController, InputControllers
from serpent.utilities import is_windows


class RedisInputControllerWorker:
    """Applies input commands queued on Redis with a real input backend.

    Replaces the former WAMP/crossbar ``input_controller_component``. The input
    data path was always a plain Redis list (see ``ClientInputController``, which
    ``lpush``-es pickled ``(func_name, *args, kwargs)`` payloads); WAMP/crossbar
    only wrapped the process and added nothing to the data path. This worker
    ``brpop``-s that list and dispatches to a concrete InputController.
    """

    @classmethod
    def run(cls):
        print(f"Starting {cls.__name__}...")

        transport = get_transport()

        game_class_name = transport.get("SERPENT:GAME").decode("utf-8")
        game_class = offshoot.discover("Game")[game_class_name]

        game = game_class()
        game.launch(dry_run=True)

        backend = InputControllers.NATIVE_WIN32 if is_windows() else InputControllers.PYAUTOGUI

        backend_string = config["input_controller"]["backend"]

        if backend_string != "DEFAULT":
            try:
                backend = InputControllers[backend_string]
            except KeyError:
                pass

        input_controller = InputController(game=game, backend=backend)

        redis_key = config["input_controller"]["redis_key"]

        while True:
            _, payload = transport.brpop(redis_key)
            func_name, *args, kwargs = pickle.loads(payload)

            getattr(input_controller, func_name)(*args, **kwargs)


if __name__ == "__main__":
    RedisInputControllerWorker.run()
