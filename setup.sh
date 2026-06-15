#!/usr/bin/env bash
#
# Serpent.AI Reborn — one-shot setup.
#
# Installs uv (if missing), creates the project environment, detects your GPU,
# and installs the matching PyTorch build:
#   * NVIDIA  -> CUDA wheels (the default PyPI build on Linux/Windows)
#   * AMD     -> ROCm wheels   (from the PyTorch ROCm index)
#   * none    -> CPU wheels    (from the PyTorch CPU index)
#   * macOS   -> default wheels (Metal/MPS-capable)
#
# Override detection with:  SERPENT_TORCH_BACKEND=cuda|rocm|cpu ./setup.sh
# Override the ROCm index :  SERPENT_ROCM_INDEX=https://download.pytorch.org/whl/rocm6.3 ./setup.sh
#   (default is rocm6.4 — newest cards like RDNA4/RX 9070 need it; older ROCm runtimes may want 6.3)
#
set -euo pipefail

CPU_INDEX="https://download.pytorch.org/whl/cpu"
ROCM_INDEX="${SERPENT_ROCM_INDEX:-https://download.pytorch.org/whl/rocm6.4}"

info() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!  \033[0m %s\n' "$*"; }

# --- 1. Ensure uv ----------------------------------------------------------
if ! command -v uv >/dev/null 2>&1; then
    info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
info "uv $(uv --version | awk '{print $2}')"

# --- 2. Detect the PyTorch backend ----------------------------------------
detect_backend() {
    if [ -n "${SERPENT_TORCH_BACKEND:-}" ]; then
        echo "$SERPENT_TORCH_BACKEND"; return
    fi
    if [ "$(uname -s)" = "Darwin" ]; then
        echo "mps"; return
    fi
    if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then
        echo "cuda"; return
    fi
    if command -v rocminfo >/dev/null 2>&1 && rocminfo 2>/dev/null | grep -q "Device Type:.*GPU"; then
        echo "rocm"; return
    fi
    if command -v lspci >/dev/null 2>&1; then
        local vga; vga="$(lspci 2>/dev/null | grep -Ei 'vga|3d|display' || true)"
        echo "$vga" | grep -Eiq 'nvidia' && { echo "cuda"; return; }
        echo "$vga" | grep -Eiq 'amd|ati|advanced micro devices' && { echo "rocm"; return; }
    fi
    echo "cpu"
}

BACKEND="$(detect_backend)"
info "PyTorch backend: ${BACKEND}"

# --- 3. Install dependencies + the right PyTorch ---------------------------
case "$BACKEND" in
    cuda|mps)
        # Default PyPI wheels are correct: CUDA on Linux/Windows, MPS on macOS.
        info "Installing all dependencies (default PyTorch wheels)..."
        uv sync
        ;;
    rocm|cpu)
        # Install everything except torch first (avoids pulling the large default
        # CUDA build), then install torch/torchvision from the correct index.
        index="$CPU_INDEX"
        [ "$BACKEND" = "rocm" ] && index="$ROCM_INDEX"

        info "Installing dependencies (excluding torch)..."
        uv sync --no-install-package torch --no-install-package torchvision

        info "Installing PyTorch from ${index} ..."
        uv pip install --reinstall torch torchvision --index-url "$index"

        if [ "$BACKEND" = "rocm" ]; then
            warn "ROCm wheels require a matching ROCm runtime + a supported AMD GPU."
            warn "Using index: ${index}"
            warn "If import fails or the GPU isn't detected, try another ROCm version, e.g.:"
            warn "  SERPENT_ROCM_INDEX=https://download.pytorch.org/whl/rocm6.3 ./setup.sh"
        fi
        ;;
    *)
        warn "Unknown backend '$BACKEND'; falling back to a plain 'uv sync'."
        uv sync
        ;;
esac

# --- 4. Optional system tools (informational only) -------------------------
missing=""
for tool in redis-server tesseract xdotool; do
    command -v "$tool" >/dev/null 2>&1 || missing="$missing $tool"
done
if [ -n "$missing" ]; then
    warn "Optional system tools not found:${missing}"
    warn "  Redis (only for the 'redis' transport), Tesseract (OCR), xdotool (X11/XWayland window control)."
    if   command -v pacman >/dev/null 2>&1; then warn "  Arch:   sudo pacman -S redis tesseract xdotool"
    elif command -v apt-get >/dev/null 2>&1; then warn "  Debian: sudo apt install redis-server tesseract-ocr xdotool"
    elif command -v dnf    >/dev/null 2>&1; then warn "  Fedora: sudo dnf install redis tesseract xdotool"
    fi
fi

# --- 5. Verify -------------------------------------------------------------
info "Verifying PyTorch..."
uv run python - <<'PY'
import torch
print(f"  torch {torch.__version__}")
print(f"  CUDA/ROCm available: {torch.cuda.is_available()}")
mps = getattr(torch.backends, "mps", None)
print(f"  MPS available: {bool(mps and mps.is_available())}")
PY

info "Done. Try:  uv run serpent --help"
