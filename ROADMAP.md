# Serpent.AI Reborn — Roadmap

What's shipped, and what's planned but **not yet in the code**. This supersedes
the old migration log; for *how* the 2020.2.1 framework was modernized, see the
git history and the "What changed" table in the [README](README.md).

---

## v0.1.0 — Current

The 2020.2.1 framework, modernized and importing cleanly on Linux / Python 3.13:

- **Tooling:** Python 3.13+, uv, ruff, pytest, GitHub Actions CI.
- **ML:** PyTorch 2.x Rainbow DQN / PPO, device auto-detect (CUDA/ROCm/MPS/CPU). TensorFlow removed.
- **Plumbing:** WAMP/crossbar removed; pluggable frame/IO **transport** (in-process | Redis); vendored, 3.13-clean **offshoot** plugin system.
- **Platform:** Wayland support via XWayland (Steam/Proton games); X11 + Win32 controllers.
- **UI:** FastAPI **dashboard** + **visual debugger** (replaced cefpython3/kivy/pony).
- **Plugins:** Super Hexagon (full worked reference) + Isaac & YMBAB (modern-API scaffolds).
- **Single CLI** (`serpent`) over the implementation library.

The dead 2020 stack is gone (TensorFlow, crossbar/autobahn/twisted, cefpython3, kivy, pony, aioredis, comet_ml, lmdb, luminoth).

---

## → v0.2.0 — Complete the modernization

Finish the work that 0.1.0 deliberately deferred or scaffolded. These are
*planned and tracked but not yet implemented in the code*.

### Native Wayland backends
Today capture/input/window only work via **XWayland**; `serpent/window_controllers/wayland_window_controller.py` is a stub.
- **Capture:** `xdg-desktop-portal` ScreenCast → PipeWire stream.
- **Input:** `ydotool`/libei over `uinput` (with the `ydotoold` setup documented).
- **Window control:** KWin D-Bus / `kdotool` (KDE) and the wlroots foreign-toplevel protocol; wire into the `WindowController` dispatch.

### Re-home the context classifiers onto torchvision
The TF/Keras Inception-V3 / Xception classifiers currently raise on import. Reimplement on **torchvision** (pretrained backbones + a small head), restoring `serpent train context`.

### Port the bundled game-agent AI
Isaac and YMBAB are modern-API scaffolds with no-op `PLAY` handlers. Port their real logic from `master` onto the modern `Agent` / PyTorch:
- **Isaac:** minimap/room/floor parsing + navigation + the RL policy.
- **YMBAB:** board parsing, tile sprite identification, OCR, match scoring.

### Finish the CLI
Several `cli.py` commands are still `# TODO: Implement`:
- `games`, `game-agents`, `rl-agents`, `game-instructions`, `show-plugins`, `download-plugin`.
- End-to-end **plugin lifecycle**: `generate` → `activate`/`deactivate` → `install` from a path/URL, with an offshoot manifest written automatically (so `serpent play <Game> <Agent>` works without manual setup).

### Windows support, validated
Exercise the win32 capture/input/window controllers on real hardware; add a `dxcam` capture path; add **Windows to the CI matrix**.

### End-to-end verification
A documented smoke-test harness that runs **capture + input + play** against a real game (Super Hexagon) and a short **GPU training** run; plus capture/transport timing benchmarks. (Untestable in the dev sandbox today.)

### Dashboard live updates
Replace the dashboard's polling with **websockets/SSE** push; reconnect handling; richer per-event/metric views and a frame-rate readout.

### Quality gates
- Progressively bring `serpent/` into **ruff** scope (currently excluded) and add **mypy** + type hints to the core.
- Broaden tests: frame transformation pipeline, input controller, `GameAPI.combine_game_inputs`, cv/ocr, sprite identification.
- Resolve the remaining in-code `# TODO`s (GameFrame fraction-resolution refactor, sprite-locator speedups, analytics tagging).

### Packaging
Build + publish to **PyPI**; commit `uv.lock` reproducibility; optional `[ml]` / `[dashboard]` extras to slim the base install; a release GitHub Action.

---

## → v0.3.0 — Beyond parity

New capabilities once the framework is fully restored and solid.

### Reinforcement learning, modernized
- **Gymnasium-compatible** `Environment` wrapper so Serpent games plug into the standard RL ecosystem.
- Newer algorithms (SAC, IMPALA, **DreamerV3** / world-models) alongside Rainbow/PPO.
- **Vectorized / multi-env** training; `torch.compile` + automatic mixed precision.

### Performance
- **Zero-copy** shared-memory frames (drop the byte-serialization round-trip); a GPU-resident frame-transformation pipeline.
- Fastest-per-platform capture: `dxcam` (Windows), PipeWire **DMA-BUF** (Wayland).

### Plugin ecosystem
- A plugin **hub/registry** with `serpent install <plugin>` from a remote index; **versioned, typed** plugin manifest; improved scaffolding and a sample-plugin gallery.

### Experiment tracking & data
- Pluggable loggers: **TensorBoard / Weights & Biases / MLflow** (replacing the dropped comet_ml).
- **Record → replay** datasets; Hugging Face dataset/model hub integration; reproducible, resumable runs.

### Dashboard 2.0
- A full SPA: **live frame stream** with agent action/reward overlays, run comparison, multi-run history, optional auth.

### Optional pretrained vision helpers (local only)
- An **opt-in** helper that runs a user-supplied object detector locally (e.g. a torchvision/ONNX model the user trained or downloaded) to find on-screen elements, as an alternative to hand-authored sprite templates. Strictly local inference on the existing torch stack — **no external/cloud services, no API costs, no new heavy runtime dependency** (ONNX Runtime would be an optional extra only). Hand-authored sprites/OCR remain the default; this is purely a convenience for users who already have a model.

### Cross-platform parity & DX
- Full **macOS (MPS)** capture/input/window backends; Wayland parity across GNOME/KDE/wlroots; headless/containerized capture for CI.
- A docs site (mkdocs-material) migrating the old wiki; **typed public API**; `serpent doctor` environment diagnostics.
- **pydantic-settings** typed config; plugin hot-reload; resilient play-loop recovery; structured logging.
