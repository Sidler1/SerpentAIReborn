# Serpent Modernization Roadmap (dev-based)

Bringing the **SerpentAI 2020.2.1 framework** (the `dev` branch / this `reborn`
branch) from its mid-2020 state (Python 3.8, Poetry, torch 1.5+cu101,
TensorFlow 2.2, Crossbar/WAMP, cefpython/kivy) up to a modern, cross-platform,
PyTorch-2 framework on Python 3.13+.

> **Strategy pivot.** The original plan rebuilt from the `master` prototype.
> The `dev` branch turned out to be the far more complete official framework, so
> we modernize **it** in place. The earlier from-scratch work lives on the
> `modernization` branch for reference; the clean ideas from it (Protocol-typed
> backends, pluggable transport, typed config) are applied *on top of* dev here.

## Locked decisions

- **Base:** modernize `dev`'s modules in place (max reuse).
- **Plugins:** keep offshoot's model; **vendor it into the repo** and make it run on 3.13.
- **Dashboard + visual debugger:** **keep & modernize** (replace the dead cef/kivy/pony stack).
- **Python/tooling:** 3.13+ (pinned to installed 3.14), **uv** (migrate off Poetry), ruff.
- **ML:** **drop TensorFlow**; PyTorch **2.x**, device auto-detect (cuda/rocm/mps/cpu).
- **Transport:** make the Redis frame/IO bus **pluggable** (in-process default, Redis optional).
- **Platform:** cross-platform, **Linux/Wayland prioritized** (X11 fallback retained).
- **Tests:** pytest + GitHub Actions CI.
- **Branch:** `reborn` (from `dev`); `master` and `modernization` left intact.

## Target dependency changes (from dev's pyproject)

| Dependency | dev (2020) | Target | Action |
|---|---|---|---|
| Python | 3.8 | 3.13+ | bump |
| Build | Poetry | uv + PEP 621 | migrate |
| torch / torchvision | 1.5.0+cu101 (pinned URL) | 2.x, standard wheels | upgrade, device auto-detect |
| tensorflow / keras / protobuf | 2.2 / pinned | — | **remove** (unblocks numpy/torch/CUDA) |
| numpy / scipy / scikit-image / scikit-learn / Pillow / h5py | 1.18 / 1.4 / 0.17 / 0.22 / 7.0 / 2.10 | current | upgrade + fix API breaks |
| crossbar / autobahn / twisted | WAMP stack | — | **remove**, rewire `play()` |
| aioredis | 1.3 | `redis.asyncio` | fold in |
| redis | 3.4 | current, behind transport iface | keep, abstract |
| cefpython3 / kivy / pony | dashboard/UI | modern web stack | **replace** |
| mss | 5.0 | current + **Wayland backend** | upgrade + extend |
| sneakysnek / python-xlib / pyautogui / pywin32 | X11/Win input+window | + **Wayland** backends | extend |
| offshoot | pip dep 0.1.6 | vendored, 3.13-ready | vendor + modernize |
| luminoth / lmdb / comet_ml / vendored win wheels | dead/orphan | — | **remove** |
| click / tqdm | 7.1 / 4.46 | current | upgrade |

## Phases

Each phase = one commit/PR on `reborn`, with an explicit exit criterion.

### Phase A — Tooling & build migration (Poetry → uv)
- PEP 621 `pyproject.toml` for uv, Python `>=3.13`, flat `serpent` package, `serpent = cli:cli` script.
- ruff + pytest config, `.python-version`, `.editorconfig`, pre-commit, GitHub Actions CI.
- New `CLAUDE.md` describing the dev-based architecture (replaces the prototype one).
- Legacy/not-yet-ported modules excluded from lint during transition.
- **Exit:** `uv sync` works on 3.13+; ruff + the importable subset of `tests/unit` run in CI.

### Phase B — Drop dead weight + dependency upgrades
- Remove TensorFlow/keras/protobuf, luminoth, lmdb, vendored Windows wheels, comet (optional later).
- Upgrade numpy/scipy/scikit-image/scikit-learn/Pillow/h5py/click/tqdm/mss; fix resulting API breaks
  (numpy 2, skimage renames, h5py `.value`, click 8).
- **Exit:** `import serpent` and core modules import cleanly on 3.13; non-WAMP tests pass.

### Phase C — Modernize & vendor the plugin system (offshoot)
- Vendor offshoot into the repo; make it 3.13-clean; preserve the `Pluggable` / `@expected` /
  `@forbidden` / discovery API so `Game`/`GameAgent` and the templates are unchanged.
- **Exit:** plugin discovery/validation + template generation work on 3.13.

### Phase D — Remove WAMP (crossbar/autobahn/twisted) & rewire
- Excise crossbar/autobahn/twisted; stop `game.play()` from spawning crossbar.
- Re-route the input-controller RPC bridge / analytics / dashboard API off WAMP.
- **Exit:** play loop runs with no crossbar; analytics + dashboard API path replaced.

### Phase E — Pluggable frame/IO transport
- Abstract the Redis bus (frames, input events, analytics) behind a transport interface;
  in-process (shared-memory/queues) default, Redis optional; `aioredis` → `redis.asyncio`.
- **Exit:** end-to-end run on in-process transport, Redis still selectable via config.

### Phase F — Wayland support (XWayland-first), Linux
- **Decision (KDE Plasma Wayland, XWayland active):** target **XWayland first** — the existing
  X11 stack (mss capture, xdotool window control, pyautogui input) already drives XWayland
  windows, which is how Steam/Proton games run. Native-Wayland backends (PipeWire capture,
  ydotool input, KWin/kdotool window control) are scaffolded behind the interface and deferred
  (they need extra system tools + uinput/ydotoold and can't be tested in the agent sandbox).
- Done: removed the `xwininfo` dependency (`xdotool getwindowgeometry --shell`); added
  `is_wayland()`/`is_x11_available()` detection; `WindowController` errors on Wayland-without-
  XWayland and warns when falling back; `WaylandWindowController` stub marks the native seam.
- **Exit:** XWayland path works on a Wayland session (user smoke-test); native seam documented.

### Phase G — ML / RL modernization (PyTorch 2.x)
- Update Rainbow DQN + PPO agents to torch 2.x idioms, device-agnostic.
- Re-home the TF-based context classifiers (InceptionV3/Xception) onto torchvision, or deprecate.
- **Exit:** agents train/infer on the auto-detected device; smoke tests on tiny data.

### Phase H — Dashboard & visual debugger (keep & modernize)
- Replace cefpython3/kivy/pony with a modern stack (web dashboard served over HTTP + a
  modern visual-debugger view); preserve the workflow.
- **Exit:** dashboard + visual debugger run on modern Python.

### Phase I — Port the three game plugins
- Bring Binding of Isaac, Super Hexagon, You Must Build A Boat (from the prototype + dev
  `game_agents`) into the modern plugin format.
- **Exit:** each plugin loads/validates; logic ported; runnable where the game is owned.

### Phase J — Tests, CI matrix, docs
- Broaden pytest coverage; CI matrix; rewrite README + CLAUDE.md; migration notes.
- **Exit:** CI green; docs reflect the modern architecture.

## Risk notes
- **Wayland (Phase F)** is the genuinely novel work — no dev dependency (mss, python-xlib,
  sneakysnek, pyautogui) speaks Wayland. Concrete toolchain confirmed at the start of the phase.
- **Dashboard (Phase H)** is high-effort: cef/kivy/pony are all hard to revive; the realistic
  path is a re-implementation that preserves the experience, not a port.
- **torch 2.x on Python 3.14** — verified during Phase B; drop the `.python-version` pin to 3.13
  if wheels lag.
</content>
