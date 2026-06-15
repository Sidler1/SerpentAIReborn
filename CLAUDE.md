# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**SerpentAI Reborn** — a modernization of the **SerpentAI 2020.2.1** Game Agent Framework. Serpent turns any game you own into a reinforcement-learning environment: it captures the game window, runs a *game agent* that analyzes each frame (CV, OCR, sprites, RL), and synthesizes keyboard/mouse input back into the game. Everything is **plugin-based** (separate plugins for game support and for game agents) so experiments are portable.

This branch (`reborn`, cut from `dev`) is being brought from its mid-2020 state (Python 3.8, Poetry, torch 1.5+cu101, TensorFlow, Crossbar/WAMP, cefpython/kivy) up to **Python 3.13+, uv, PyTorch 2.x, cross-platform incl. Wayland**. The plan and per-phase status live in **`MODERNIZATION.md`** — read it before starting work; it defines what's been modernized and what's still legacy.

Branches: `reborn` (active work) · `dev` (pristine SerpentAI 2020.2.1) · `master` (the original 2017 prototype) · `modernization` (an abandoned from-scratch attempt, kept for reference). PRs target `dev`.

## Commands

Tooling is **uv** (migrated off Poetry). The `serpent` console script maps to `cli:cli` (the click CLI in top-level `cli.py`).

```bash
uv sync --dev                 # create/refresh the environment (.venv, Python 3.13)
uv run pytest                 # run the test suite
uv run pytest tests/unit/test_agent.py::TestAgent::test_... # single test
uv run ruff check .           # lint
uv run ruff format .          # format (ruff format --check in CI)
uv run serpent --help         # the CLI (setup, plugins, games, launch, train, play, record, sdk_*)
```

Most runtime commands assume the **repo root is the working directory** (see config note below).

### Runtime prerequisites (to actually run a game agent, not just tests)
- **Redis** on `localhost:6379` — required only for the **default `redis` transport**. The bus (frames, input, analytics) goes through `serpent/transport` (`transport.backend: redis | in_process` in config). `in_process` needs no Redis but runs the grabber as a thread and drives input directly (single process); `redis` keeps the multi-process model (grabber/input worker as subprocesses).
- **`config/config.yml`** must exist in the CWD — `serpent/config.py` reads it **at import time** and raises if missing. The repo ships a stub `config/config.yml` + `config/config.plugins.yml` "to make unit testing possible."
- **Tesseract** for OCR (`pytesseract`). Capture/input/window currently speak **X11**; on a **Wayland** session they work via **XWayland** (`$DISPLAY` must be set — true on KDE/GNOME by default), which covers Steam/Proton games. `WindowController` raises if Wayland is detected with no XWayland, and warns when falling back to XWayland. Native-Wayland backends (PipeWire capture, ydotool input, KWin/kdotool window control) are scaffolded but not implemented — see `serpent/window_controllers/wayland_window_controller.py` and MODERNIZATION.md Phase F.
- Plugins are discovered from a `plugins/` directory (git-ignored) created by the CLI/SDK.

## Architecture

Built on **offshoot**, a tiny plugin framework **vendored into the repo at `./offshoot`** (no longer a pip dependency; still imported as `import offshoot`). `serpent/game.py::Game` and `serpent/game_agent.py::GameAgent` are `offshoot.Pluggable` subclasses; plugins subclass them. Methods are annotated with `@offshoot.expected` (a plugin must implement) and `@offshoot.forbidden` (must not override); these markers are detected by source inspection (`Pluggable.method_directives`). Discovery is `offshoot.discover(pluggable, scope=None, selection=None)` against `offshoot.manifest.json` (importlib-based). Dev config lives in the root `offshoot.yml` (`modules: [serpent.game, serpent.game_agent]`).

### The frame pipeline (core loop)
1. `Game.launch()` uses a **game launcher** (`serpent/game_launchers/`, e.g. Steam) and a **window controller** to find/focus/size the game window.
2. `serpent/frame_grabber.py` (`FrameGrabber`, the **only** `mss` call site) captures the window region and pushes raw frame bytes onto the transport (`get_transport()`), as `timestamp~shape~dtype~bytes`.
3. The agent loop, rate-limited by `serpent/game_frame_limiter.py`, reads the latest frame (`GameFrame`/`GameFrameBuffer`), optionally runs it through the **frame transformation pipeline** (`serpent/frame_transformation_pipeline.py` + `frame_transformer.py` — resize/grayscale/CROP/etc., configured by a pipeline string), and hands it to the agent.
4. A `GameAgent` dispatches frames to a **frame handler** (PLAY / COLLECT_FRAMES / etc.) selected by plugin config.

### Cross-platform backends (platform dispatch)
- **Input** — `serpent/input_controller.py` defines the canonical key/button vocabulary via **sneakysnek** (`KeyboardKey`, `KeyboardEvent`, `MouseButton`, …) and an `InputControllers` enum; concrete controllers live in `serpent/input_controllers/` (`pyautogui_input_controller`, `native_win32_input_controller`, `client_input_controller`). Live input *capture* uses sneakysnek's `Recorder` in `serpent/input_recorder.py`. **No Wayland backend yet.**
- **Window** — `serpent/window_controller.py` dispatches to `serpent/window_controllers/` (`linux_window_controller` = xdotool/X11+XWayland, `win32_window_controller` = pywin32, `wayland_window_controller` = native stub). `LinuxWindowController.get_window_geometry` uses `xdotool getwindowgeometry --shell` (no `xwininfo` dependency).

### Reinforcement learning (PyTorch)
`serpent/machine_learning/reinforcement_learning/`: `agent.py` is the base `Agent` (handles the `game_inputs` → action-space mapping, the key abstraction — see `tests/unit/test_agent.py`). Concrete agents in `agents/`: `rainbow_dqn_agent`, `ppo_agent`, `random_agent`, `recorder_agent`. The Rainbow DQN and PPO implementations (`rainbow_dqn/`, `ppo/`) are **pure PyTorch (torch 2.x)** and **device-agnostic**: `serpent/machine_learning/device.py::get_device()` auto-selects CUDA/ROCm → MPS → CPU; agents call `.to(device)` (no hard-coded `.cuda()`/`set_default_tensor_type`). Full-model checkpoints load with `weights_only=False`. The TF/Keras context classifiers (`context_classification/`) and object recognition are **deprecated** (raise an informative error; a torchvision port is future work).

### Game API & helpers
`serpent/game_api.py` (`GameAPI`) — per-game input combination logic and helpers (e.g. `combine_game_inputs`, see `tests/unit/test_game_api.py`). Supporting CV/util modules: `cv.py`, `sprite.py`, `sprite_identifier.py`, `sprite_locator.py`, `ocr.py`, `raycasting.py`, `trigonometry.py`, `utilities.py` (defines `SerpentError`).

### Config (import-time, CWD-relative, three-ish layers)
`serpent/config.py` merges `config/config.yml` (CWD) over offshoot's plugin config (`config/config.plugins.yml`) **at import time**, exposing a module-level `config` dict. Many modules import `from serpent.config import config` at top level, so importing them triggers this load — and fails if the CWD lacks `config/`.

## Conventions & gotchas
- **Dependencies are modernized.** `pyproject.toml` carries a modern set incl. torch 2.x and fastapi/uvicorn; the dead 2020 stack — TensorFlow, crossbar/autobahn/twisted, cefpython3, kivy, pony, aioredis, comet_ml, lmdb, luminoth — is removed. Don't reintroduce them; check `MODERNIZATION.md` for what's intentionally absent.
- **Dashboard & visual debugger are local FastAPI web apps** (`serpent/dashboard/app.py`, `serpent/visual_debugger/server.py`), replacing the dead cef/kivy/pony stack. `serpent dashboard` serves analytics from a SQLite `EventStore` (`dashboard/store.py`) fed by a background `AnalyticsConsumer` that drains the transport (the Phase D analytics consumer, now realized). `serpent visual-debugger` renders pipeline buckets as PNGs. Producers (game agents) and the viewer share buckets/events via the **redis** transport (in-process can't cross processes).
- **Lint scope grows per phase.** ruff's `extend-exclude` currently skips the not-yet-modernized tree (`serpent`, `cli.py`, `dashboard`, `vendor`); as a module is modernized, drop it from the exclude list and make it ruff-clean.
- **`cli.py` keeps heavy imports lazy** (torch, requests, ocr inside functions) so `serpent --help` stays fast and import-safe; preserve that pattern.
- **Input is a Redis bridge, not WAMP (as of Phase D).** The default `ClientInputController` pickles `(func_name, *args, kwargs)` onto the `SERPENT:INPUTS` list; `game.play()` spawns `serpent.input_controllers.redis_input_controller_worker`, which `brpop`s that list and dispatches to a real backend. WAMP/crossbar/autobahn and `serpent/wamp_components/` are **removed**; the analytics consumer + dashboard are now FastAPI/SQLite (see the dashboard note above).
</content>
