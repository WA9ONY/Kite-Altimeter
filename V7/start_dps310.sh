#!/usr/bin/env bash
set -euo pipefail

# --- Configuration -----------------------------------------------------------
DEFAULT_TARGET="Pressure.py"
REQUIRED_PKGS=("adafruit-blinka" "adafruit-circuitpython-dps310")
PYPI_HOST="pypi.org"
# ----------------------------------------------------------------------------

# Resolve to this script's directory and enter it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "[INFO] Working directory: $SCRIPT_DIR"

# Helper: detect basic internet connectivity
has_net() {
  if command -v curl >/dev/null 2>&1; then
    curl -s --head "https://${PYPI_HOST}" >/dev/null 2>&1 && return 0
  fi
  if command -v ping >/dev/null 2>&1; then
    ping -c1 -W1 "${PYPI_HOST}" >/dev/null 2>&1 && return 0
  fi
  return 1
}

ONLINE=0
if has_net; then
  ONLINE=1
  echo "[INFO] Internet: online"
else
  echo "[WARN] Internet: offline (will skip package installs/upgrades)"
fi

# Create venv if missing
if [[ ! -f ".venv/bin/activate" ]]; then
  echo "[INFO] No .venv found. Creating one..."
  python3 -m venv .venv
fi

# Activate venv
# (Requested) Ensure this line exists so running the .sh sets up env
source ".venv/bin/activate"
echo "[INFO] Using Python: $(command -v python)"

# Upgrade pip toolchain ONLY if online (non-fatal if it fails)
if [[ "$ONLINE" -eq 1 ]]; then
  echo "[INFO] Upgrading pip/setuptools/wheel (online)..."
  python -m pip install --upgrade pip setuptools wheel || echo "[WARN] pip upgrade failed; continuing."
else
  echo "[INFO] Skipping pip upgrades (offline)."
fi

# Check which required packages are missing
MISSING=$(python - <<'PYCHECK'
import importlib, sys
pkgs = ["adafruit-blinka", "adafruit-circuitpython-dps310"]
missing = []
for p in pkgs:
    try:
        importlib.import_module(p.replace("-", "_"))
    except Exception:
        missing.append(p)
if missing:
    print(" ".join(missing))
PYCHECK
)

if [[ -n "${MISSING:-}" ]]; then
  if [[ "$ONLINE" -eq 1 ]]; then
    echo "[INFO] Installing missing packages: ${MISSING}"
    python -m pip install ${MISSING}
  else
    echo "[ERROR] Missing required packages but no internet: ${MISSING}"
    echo "        Connect to the internet once and re-run this script to auto-install."
    echo "        Or pre-install offline by copying wheels into this venv."
    exit 1
  fi
else
  echo "[INFO] Required packages already installed."
fi

# Choose target script
TARGET="${1:-$DEFAULT_TARGET}"
if [[ ! -f "$TARGET" ]]; then
  echo "[ERROR] Can't find Python script '$TARGET' in $SCRIPT_DIR"
  echo "Usage: $0 [python_script.py]"
  exit 1
fi

echo "[INFO] Launching: $TARGET"
exec python "$TARGET"
