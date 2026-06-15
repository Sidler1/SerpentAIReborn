"""Device selection for the PyTorch agents.

Auto-detects the best available device so the RL agents run unchanged on NVIDIA
(CUDA), AMD (ROCm — exposed by torch as ``cuda``), Apple Silicon (``mps``), or
CPU. The 2020 code hard-coded ``cuda`` or ``cpu``; this replaces that.
"""

from __future__ import annotations

import torch


def get_device() -> torch.device:
    if torch.cuda.is_available():
        # Covers NVIDIA CUDA and AMD ROCm (both report as the "cuda" backend).
        return torch.device("cuda")

    mps = getattr(torch.backends, "mps", None)
    if mps is not None and mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


__all__ = ["get_device"]
