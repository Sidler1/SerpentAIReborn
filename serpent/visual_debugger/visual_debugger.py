"""Visual debugger producer.

Game agents push intermediate pipeline images into named "buckets" on the
transport; the web viewer (``serpent/visual_debugger/server.py``) renders the
latest frame of each bucket. Each frame is stored as raw bytes alongside a small
pickled ``{shape, dtype}`` header so it can be reconstructed without assuming a
dtype (the legacy Kivy viewer hard-coded float64).

Buckets are trimmed to a small ring so memory stays bounded even when nothing is
consuming — the viewer *peeks* the newest frame rather than popping.
"""

import itertools
import pickle

import numpy as np
import skimage.io

from serpent.config import config
from serpent.transport import get_transport

# Frames retained per bucket (the viewer only needs the newest; a few gives slack).
BUCKET_BUFFER = 8


class VisualDebugger:
    def __init__(self, buckets=None, clear=True):
        self.available_buckets = buckets or config["visual_debugger"]["available_buckets"]
        self.bucket_generator = itertools.cycle(self.available_buckets)

        self.transport = get_transport()

        # Producers clear stale frames on startup; the viewer must not (it would
        # wipe the frames it is meant to display).
        if clear:
            self.clear_image_data()

    def _prefix(self):
        return config["visual_debugger"]["redis_key_prefix"]

    def store_image_data(self, image_data, image_shape, bucket="debug"):
        header = pickle.dumps({"shape": image_shape, "dtype": str(image_data.dtype)})

        meta_key = f"{self._prefix()}:{bucket}:META"
        data_key = f"{self._prefix()}:{bucket}"

        self.transport.lpush(meta_key, header)
        self.transport.lpush(data_key, image_data.tobytes())

        self.transport.ltrim(meta_key, 0, BUCKET_BUFFER - 1)
        self.transport.ltrim(data_key, 0, BUCKET_BUFFER - 1)

    def _read_image_at(self, bucket, index):
        meta = self.transport.lindex(f"{self._prefix()}:{bucket}:META", index)
        data = self.transport.lindex(f"{self._prefix()}:{bucket}", index)

        if meta is None or data is None:
            return None

        header = pickle.loads(meta)
        return np.frombuffer(data, dtype=header["dtype"]).reshape(header["shape"])

    def peek_image_data(self, bucket):
        """Return the newest image in ``bucket`` without consuming it."""
        return self._read_image_at(bucket, 0)

    def retrieve_image_data(self):
        """Pop the next bucket's newest frame (round-robin); legacy consumer API."""
        bucket = next(self.bucket_generator)

        meta = self.transport.rpop(f"{self._prefix()}:{bucket}:META")
        data = self.transport.rpop(f"{self._prefix()}:{bucket}")

        if meta is None or data is None:
            return None

        header = pickle.loads(meta)
        image_data = np.frombuffer(data, dtype=header["dtype"]).reshape(header["shape"])

        return bucket, image_data

    def save_image_data(self, bucket, image_data):
        if bucket in self.available_buckets:
            if image_data.dtype == "bool" or (
                image_data.dtype == "uint8" and 1 in np.unique(image_data)
            ):
                image_data = image_data.astype("uint8") * 255

            skimage.io.imsave(f"{bucket}.png", image_data)

    def clear_image_data(self):
        for key in self.transport.keys(f"{self._prefix()}*"):
            self.transport.delete(key.decode("utf-8"))

    def get_bucket_queue_length(self, bucket):
        return self.transport.llen(f"{self._prefix()}:{bucket}")
