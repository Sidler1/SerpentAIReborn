# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An early (pre-alpha, ~2017) prototype of **Serpent** — a Python Game Agent Development Kit. It captures frames from a live game window, runs a "game agent" that analyzes each frame (computer vision, OCR, sprite matching, ML), and synthesizes keyboard/mouse input back into the game. **Linux/X11 only** — it shells out to `xdotool`/`xwininfo` and grabs the screen with `mss`. This is the original monorepo-style layout (a `lib/` core + checked-in `plugins/`), predating the later pip-installable `SerpentAI` framework.

Note: this repo is a public archive. Modernization (Python version, dependency upgrades) is the active goal — expect to touch `requirements.txt`, the X11/input layer, and the ML stack heavily.

## Runtime prerequisites (non-obvious, required to run anything)

- **Redis** must be running on `localhost:6379` — it is the IPC bus between the frame grabber and the agent loop (frames are pushed as raw bytes to the list key `SERPENT:FRAMES`). Importing `lib.config` connects to Redis indirectly via modules that construct `StrictRedis` at import time.
- **X11 desktop** with `xdotool` and `xwininfo` on PATH — used for window discovery, focus, geometry, and input injection.
- **`config/config.private.yml` must exist** — `lib/config.py` raises if it's missing (even if empty). It is git-ignored. Create an empty one before running.
- **Steam** — the only implemented game launcher (`lib/game_launchers/steam_game_launcher.py`) launches games by Steam app id.
- For the ML training tasks: a GPU + the pinned TensorFlow 1.x / Keras 2.0 stack (see `requirements.txt`).

## Commands

There is no build step and **no test suite**. Everything is driven by `invoke` tasks (`tasks.py` → `lib/invoke_tasks.py`) and the scripts in `bin/`.

```bash
# Run a game agent end-to-end (launch game, grab frames, play)
invoke isaac          # Binding of Isaac: Rebirth
invoke hexagon        # Super Hexagon
invoke boat_play      # You Must Build A Boat (launch happens via boat_launch)

# Launch only / play against an already-running window
invoke isaac_launch
invoke isaac_play     # launches with dry_run=True, then plays

# The frame grabber as a standalone process (normally spawned by Game.play)
invoke start_frame_grabber -w 640 -h 480 -x 0 -y 0

# ML training pipelines
invoke boat_context_train   # train Inception-v3 context classifier from datasets/
invoke boat_train_model     # train sklearn SGDRegressor over datasets/ymbab/*.h5

# Support processes (each is a long-running daemon; run in separate terminals)
bin/visual_debugger                          # Kivy app showing pipeline frame buckets
bin/analytics_consumer                       # tails Redis analytics events
bin/analytics_wamp_component                 # WAMP/autobahn analytics router component
bin/analytics_elasticsearch_wamp_component   # ships analytics to Elasticsearch
```

To run a single agent flow, pick the matching `invoke` task above; there is no finer-grained test runner.

## Architecture

The system is built on the **offshoot** plugin framework. Two abstract "pluggables" defined in `lib/` are subclassed by checked-in plugins under `plugins/`:

- `lib/game.py` → `Game(offshoot.Pluggable)` — owns the game window lifecycle.
- `lib/game_agent.py` → `GameAgent(offshoot.Pluggable)` — owns per-frame decision logic.

`offshoot.yml` declares which modules are pluggable (`lib.game`, `lib.game_agent`) and where plugins, their config, and their extra requirements live. `offshoot.manifest.json` is the installed-plugin registry. `@offshoot.forbidden` / `@offshoot.expected` decorators mark methods plugins must not override vs. must implement (e.g. `Game.screen_regions`).

### The frame pipeline (the core loop)

1. `Game.launch()` → `SteamGameLauncher` starts the game; `after_launch()` uses `xdotool` to find the window, move it to `(0,0)`, and read its geometry via `xwininfo`.
2. `Game.play()` spawns the frame grabber as a **separate process** (`invoke start_frame_grabber ...` via `subprocess.Popen`).
3. `lib/frame_grabber.py` `FrameGrabber.start()` loops: grab the window region with `mss`, push raw `uint8` BGRA→RGB bytes onto Redis list `SERPENT:FRAMES`, trimmed to a rolling buffer.
4. Back in `Game.play()`, a loop rate-limited by `lib/game_frame_limiter.py` reads the latest frame (`FrameGrabber.get_frames` → `GameFrame` / `GameFrameBuffer`) and, only while the window is focused, calls `game_agent.on_game_frame(frame)`.
5. `GameAgent.on_game_frame` dispatches to a **frame handler** selected by the plugin's `frame_handler` config key.

### Frame handlers (the agent's mode of operation)

`GameAgent` ships base handlers in a `self.frame_handlers` dict: `NOOP`, `COLLECT_FRAMES`, `COLLECT_FRAMES_FOR_CONTEXT`, `COLLECT_CHARACTERS`. Plugins register their own (e.g. the boat agent adds `PLAY`, `PLAY_BOT`, `PLAY_RANDOM`) plus optional one-time `frame_handler_setups`. This is the central extension point: data-collection modes feed `datasets/`, then training tasks turn that data into models, then a `PLAY` handler consumes the models. The collect→train→play progression is the intended workflow.

### Configuration (three-layer merge)

`lib/config.py` loads and merges, in increasing precedence:
1. plugin config (`config/config.plugins.yml`, path from `offshoot.config`)
2. `config/config.private.yml` (git-ignored, **must exist**)
3. `config/config.yml`

So `config.yml` wins over private wins over plugin config. A `Game`/`GameAgent` reads its own slice via `config.get(f"{ClassName}Plugin")`. Global keys like `redis`, `elasticsearch`, `frame_grabber.redis_key`, and `frame_handlers` live in `config.yml`.

### Supporting subsystems

- **Computer vision / sprites**: `lib/cv.py`, `lib/sprite.py`, `lib/sprite_locator.py`, `lib/sprite_identifier.py`. A `Game` auto-discovers PNG sprites from `plugins/<Plugin>/files/data/sprites` and the agent registers them with a `SpriteIdentifier`.
- **OCR**: `lib/ocr.py` (+ per-plugin OCR helpers).
- **Input**: `lib/input_controller.py` wraps `PyUserInput` (`pymouse`/`pykeyboard`) and `pyautogui`; tracks held-key sets for press/release diffing.
- **Machine learning**: `lib/machine_learning/` — `reinforcement_learning/` (Keras `dqn`/`ddqn`, replay memory, ε-greedy policy, keyboard/mouse action space) and `context_classification/` (SVM and Inception-v3 classifiers that label what on-screen "context"/screen a frame belongs to).
- **Analytics / telemetry**: `lib/analytics_client.py` + `lib/wamp_components/` use `autobahn` WAMP over Redis, optionally fanning events into Elasticsearch. Consumed by the `bin/analytics_*` scripts.
- **Visual debugger**: `lib/visual_debugger/` is a Kivy app that reads frame "buckets" from Redis (`SERPENT:VISUAL_DEBUGGER:*`) so you can watch intermediate pipeline images live.

### Plugin layout convention

Each plugin is `plugins/<Name>Plugin/` with `plugin.py` (the `offshoot.Plugin` declaration: `name`, `version`, `files` mapping a file to a pluggable, `config` defaults, install hooks) and `files/` containing the actual `Game`/`GameAgent` subclass plus `files/data/` (sprites) and `files/helpers/` (game-specific CV/OCR/scoring code). Game and GameAgent are separate plugins (e.g. `YouMustBuildABoatGamePlugin` vs `YouMustBuildABoatGameAgentPlugin`).

## Conventions & gotchas

- Tasks/scripts assume the **repo root is the working directory** — config paths and `datasets/` are relative. `bin/*` scripts insert the repo root onto `sys.path` themselves.
- `datasets/` and `ml_models/` are git-ignored and created/consumed at runtime by collect handlers and training tasks.
- Frames cross the process boundary as raw bytes with no shape metadata — the consumer must reconstruct shape from window geometry (`height, width, 3`). Keep grabber and consumer in sync on this.
- Dependencies in `requirements.txt` are hard-pinned to 2017-era versions (NumPy 1.12, scikit-image 0.13, Keras 2.0.5, TensorFlow-GPU 1.1, Kivy 1.10, autobahn 17.6, `redis==2.10`, `aioredis` beta). Several have since-renamed/removed APIs (e.g. `np.fromstring`, `datetime.utcnow`, Keras 1→2, TF 1→2) — account for this when upgrading.
</content>
</invoke>
