# Serpent.AI Reborn — Game Agent Framework (Python)

[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)
[![Built with uv](https://img.shields.io/badge/built%20with-uv-de5fe9.svg)](https://github.com/astral-sh/uv)

Serpent.AI turns **any video game you own** into a sandbox environment for AI / ML
experimentation — capture the game's frames, run a *game agent* that analyzes them
(computer vision, OCR, sprites, reinforcement learning), and synthesize keyboard /
mouse input back into the game. It's plugin-based (separate plugins for game support
and for game agents) so experiments are portable.

**Reborn** is a 2026 modernization of the original [SerpentAI](https://github.com/SerpentAI/SerpentAI)
framework (last released 2020.2.1, Python 3.8): now Python 3.13+, [uv](https://github.com/astral-sh/uv),
PyTorch 2.x, a pluggable transport, Wayland-aware, and free of the dead 2020
dependency stack. See [`MODERNIZATION.md`](MODERNIZATION.md) for the full
journey and [`CLAUDE.md`](CLAUDE.md) for an architecture orientation.

> Core tenets (unchanged from the original): **(1)** run natively — no Docker or VNC;
> **(2)** bring your own games — no licensing deals or special APIs; **(3)** encourage
> diverse approaches — RL, classical CV, or just mashing buttons. All allowed.

## Requirements

- **Python 3.13+** and **[uv](https://docs.astral.sh/uv/getting-started/installation/)**
- **Linux** (primary) or **Windows**. On a **Wayland** session the capture/input/window
  backends run via **XWayland** (`$DISPLAY` must be set — the default on KDE/GNOME), which
  covers Steam/Proton games. Native-Wayland backends are scaffolded but not yet implemented.
- Optional: **Redis** (only for the `redis` transport — the in-process transport needs nothing),
  **Tesseract** (OCR), a **GPU** (CUDA/ROCm/MPS auto-detected for training), and **Steam** to run
  the bundled example games.

## Install

```bash
git clone https://github.com/Sidler1/SerpentAIReborn.git
cd SerpentAIReborn
uv sync            # creates .venv on Python 3.13 and installs everything
uv run serpent --help
```

## Quickstart

```bash
uv run serpent --help                 # CLI surface
uv run serpent dashboard              # analytics dashboard  -> http://127.0.0.1:8500
uv run serpent visual-debugger        # live frame viewer    -> http://127.0.0.1:8501
```

Three example game plugins live under [`plugins/`](plugins/):

- **Super Hexagon** — a complete worked reference: a modern `Game` + `GameAPI` + a real
  `PLAY` agent showing the frame → decision → input loop end to end.
- **Binding of Isaac: Rebirth** and **You Must Build A Boat** — modern-API scaffolds that
  load and validate; their original game-specific AI is preserved in git history on the
  `master` branch and is a work-in-progress port.

## Architecture (at a glance)

A `Game` plugin describes a title (window, Steam launcher, screen regions, a `GameAPI`);
a `GameAgent` plugin decides what to do each frame via *frame handlers*. The play loop
captures frames (mss) onto a **pluggable transport** (in-process or Redis), an agent
consumes them, and input is applied through a cross-platform input controller. Plugins are
discovered by the vendored **offshoot** framework. Reinforcement learning (Rainbow DQN, PPO)
is **PyTorch 2.x**, device-agnostic. Full detail is in [`CLAUDE.md`](CLAUDE.md).

## What changed from SerpentAI 2020.2.1

| Area | Before (2020) | Now (Reborn) |
|---|---|---|
| Python / build | 3.8 / Poetry | 3.13+ / uv |
| ML | TensorFlow + torch 1.5+cu101 | **PyTorch 2.x**, device auto-detect; TF removed |
| Messaging | Crossbar/WAMP (autobahn/twisted) | removed; input over a Redis/in-process bridge |
| Frame/IO bus | hard-wired Redis | **pluggable transport** (redis \| in_process) |
| Plugin system | pip `offshoot` | **vendored** offshoot, 3.13-clean |
| Dashboard / debugger | cefpython3 + Kivy + Pony | **FastAPI** web apps |
| Wayland | none | XWayland-first support |
| Tooling | — | ruff, pytest, GitHub Actions CI |

Dropped entirely: TensorFlow, crossbar/autobahn/twisted, cefpython3, kivy, pony, aioredis,
comet_ml, lmdb, luminoth, vendored Windows wheels.

## Development

```bash
uv run pytest                 # test suite
uv run ruff check .           # lint
uv run ruff format .          # format
```

CI (GitHub Actions) runs lint + format-check + tests on Python 3.13 / Linux.

## License & credits

MIT. Original framework by Nicholas Brochu and the SerpentAI contributors;
Reborn is a community modernization fork.
