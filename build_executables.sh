#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-$ROOT_DIR/env/bin/python}"

if [[ ! -x "$PYTHON" ]]; then
    if command -v python3 >/dev/null 2>&1; then
        PYTHON="$(command -v python3)"
    elif command -v python >/dev/null 2>&1; then
        PYTHON="$(command -v python)"
    else
        echo "Python executable not found. Set PYTHON=/path/to/python before running this script." >&2
        exit 1
    fi
fi

if [[ ! -d "$ROOT_DIR/env" && "$PYTHON" == "$ROOT_DIR/env/bin/python" ]]; then
    python3 -m venv "$ROOT_DIR/env"
    PYTHON="$ROOT_DIR/env/bin/python"
fi

"$PYTHON" -m pip install --upgrade pip >/dev/null
"$PYTHON" -m pip install -r "$ROOT_DIR/requirements.txt" >/dev/null

cd "$ROOT_DIR"

COMMON_ARGS=(
    --noconfirm
    --clean
    --onefile
    --add-data "shopname_category_mapping.json:."
    --paths "$ROOT_DIR"
)

"$PYTHON" -m PyInstaller "${COMMON_ARGS[@]}" \
    --windowed \
    --name statement-studio \
    src/gui.py

"$PYTHON" -m PyInstaller "${COMMON_ARGS[@]}" \
    --name statement-pipeline \
    src/sm.py

echo
echo "Executables created:"
echo "  $ROOT_DIR/dist/statement-studio"
echo "  $ROOT_DIR/dist/statement-pipeline"
