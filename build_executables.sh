#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-$ROOT_DIR/env/bin/python}"

if [[ ! -x "$PYTHON" ]]; then
    echo "Python executable not found: $PYTHON" >&2
    echo "Create the virtualenv or set PYTHON=/path/to/python before running this script." >&2
    exit 1
fi

if ! "$PYTHON" -m PyInstaller --version >/dev/null 2>&1; then
    echo "PyInstaller is not installed in $PYTHON" >&2
    echo "Install it with: $PYTHON -m pip install pyinstaller" >&2
    exit 1
fi

cd "$ROOT_DIR"

COMMON_ARGS=(
    --noconfirm
    --clean
    --onefile
    --add-data "shopname_category_mapping.json:."
)

"$PYTHON" -m PyInstaller "${COMMON_ARGS[@]}" \
    --windowed \
    --name statement-studio \
    gui.py

"$PYTHON" -m PyInstaller "${COMMON_ARGS[@]}" \
    --name statement-pipeline \
    sm.py

echo
echo "Executables created:"
echo "  $ROOT_DIR/dist/statement-studio"
echo "  $ROOT_DIR/dist/statement-pipeline"
