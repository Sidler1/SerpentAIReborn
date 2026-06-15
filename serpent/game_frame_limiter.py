import time


class GameFrameLimiter:

    def __init__(self, fps=30):
        self.frame_time = 1 / fps
        self.started_at = None

    def start(self):
        self.started_at = time.perf_counter()

    def stop_and_delay(self):
        # Monotonic clock; full elapsed seconds (the old timedelta.microseconds
        # silently dropped any whole seconds of frame time).
        duration = time.perf_counter() - self.started_at
        remaining_frame_time = self.frame_time - duration

        if remaining_frame_time > 0:
            time.sleep(remaining_frame_time)

    def benchmark(self):
        pass
