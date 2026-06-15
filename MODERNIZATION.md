# Serpent Modernization Roadmap

Bringing the original Serpent prototype (2017, offshoot + Redis + X11, TF1/Keras) up to a
modern, cross-platform, PyTorch-based game-agent framework.

## Target stack

| Area        | From                                   | To                                                        |
|-------------|----------------------------------------|-----------------------------------------------------------|
| Python      | 3.6-era, unpinned                      | 3.13                                                      |
| Packaging   | `requirements.txt` + `invoke`          | `pyproject.toml` + **uv**, `src/serpent/` package         |
| Lint/format | none                                   | **ruff** (lint + format), type hints + mypy (best-effort) |
| Plugins     | `offshoot` (`Pluggable`/manifest)      | fresh entry-point / pluginbase-style loader               |
| Capture     | `mss` + X11 geometry via `xdotool`     | backend interface; **Wayland first**, X11 fallback, Win/macOS later |
| Input       | `PyUserInput` (`pymouse`/`pykeyboard`) | backend interface (Wayland: libei/ydotool; `pynput` where viable) |
| Frame bus   | Redis list (hard dependency)           | **pluggable transport**: in-process shared-memory (default) or Redis |
| ML / RL     | TensorFlow-GPU 1.1, Keras 2.0, keras-rl | **PyTorch**, device auto-detect (cuda/rocm/mps/cpu)       |
| CLI         | `invoke` tasks + `bin/*` scripts       | `serpent` CLI (typer/click)                               |
| Analytics   | `autobahn` WAMP + Elasticsearch        | optional, modernized (or dropped if unused)               |
| Visual dbg  | Kivy app reading Redis buckets         | modernized against the new transport                      |
| Tests / CI  | none                                   | **pytest** + GitHub Actions                               |

## Guiding decisions (locked)

- Re-architect toward modern SerpentAI **as inspiration only** — clean 2026 design, no dated code copied.
- Core package `src/serpent/` + example game **plugins kept in-repo** under `plugins/`.
- **Port all three** bundled game plugins (Binding of Isaac: Rebirth, Super Hexagon, You Must Build A Boat).
- Cross-platform, but **Linux/Wayland is the priority backend** to build and test first.
- Work proceeds **phase by phase on a branch, one commit/PR per phase**.

## Phases

### Phase 0 — Tooling & scaffolding
- `pyproject.toml` (uv-managed), `src/serpent/` layout, ruff config, `.python-version` (3.13).
- Package skeleton + console-script entry point (`serpent`) that imports and prints version.
- Pre-commit (ruff), editorconfig, baseline GitHub Actions workflow (lint only).
- **Exit:** `uv sync` works, `serpent --help` runs, CI green on lint.

### Phase 1 — Core abstractions & config
- Port config to a typed loader (3-layer YAML merge preserved, or pydantic-settings).
- New plugin system replacing offshoot (`Game` / `GameAgent` base classes, discovery, the `expected`/`forbidden` contract).
- Port `GameFrame`, `GameFrameBuffer`, `GameFrameLimiter`, exceptions.
- Define backend Protocols: `CaptureBackend`, `InputBackend`, `WindowBackend`, `FrameTransport`.
- **Exit:** plugins discoverable; backend interfaces defined with no-op/stub impls; unit tests for config + discovery.

### Phase 2 — Capture / input / window backends (Linux/Wayland first)
- Wayland capture (PipeWire/xdg-desktop-portal or `grim`-style), X11/XWayland fallback (`mss`).
- Wayland input (libei/ydotool/evdev), `pynput` where it works; cross-platform window discovery abstraction.
- **Exit:** capture a real window region + inject keys/mouse on Wayland; manual smoke test documented; unit tests with fakes.

### Phase 3 — Pluggable frame transport
- `InProcessTransport` (multiprocessing shared memory/queues) as default; `RedisTransport` behind the same interface; selected via config.
- **Exit:** grabber→agent frame handoff works on both transports; parametrized tests.

### Phase 4 — Runtime: Game / GameAgent
- Port the launch/play loop (launcher abstraction; Steam launcher modernized), frame-handler dispatch, sprite discovery/identification, `lib/cv.py`, `lib/ocr.py`.
- **Exit:** end-to-end loop runs with a scripted (non-ML) agent against a captured window.

### Phase 5 — ML / RL port to PyTorch
- DQN/DDQN, replay memory, ε-greedy policy, keyboard/mouse action space → PyTorch, device-agnostic.
- Context classifiers (CNN + SVM) ported; training pipelines reworked (replace h5py/Keras flow as needed).
- **Exit:** train + load + run a model on auto-detected device; smoke tests on tiny synthetic data.

### Phase 6 — `serpent` CLI
- Subcommands replacing the invoke tasks / bin scripts: `setup`, `generate plugin`, `launch`, `play`, `capture`, `train`, `visual-debugger`.
- **Exit:** every old `invoke`/`bin` entry point has a CLI equivalent.

### Phase 7 — Port the three game plugins
- Migrate Isaac, Super Hexagon, You Must Build A Boat to the new plugin API + backends.
- **Exit:** each plugin imports/loads cleanly; logic ported; runnable where the game is owned.

### Phase 8 — Visual debugger & analytics
- Visual debugger modernized against the new transport. Analytics (WAMP/Elasticsearch) modernized or made optional/removed pending whether you use it.
- **Exit:** live frame inspection works; analytics decision implemented.

### Phase 9 — Tests, CI, docs
- Broaden pytest coverage; full GitHub Actions matrix; rewrite README + CLAUDE.md; migration notes from the old layout.
- **Exit:** CI green; docs reflect the new architecture.

## Open questions to revisit per phase
- Wayland input often needs elevated permissions / a running ydotoold or compositor portal — we'll confirm the concrete toolchain in Phase 2.
- Whether analytics (WAMP/Elasticsearch) is still wanted at all (Phase 8).
- Whether to keep h5py-based dataset storage or move to a simpler format (Phase 5).
</content>
