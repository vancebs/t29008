#! /bin/bash

SCRIPT_PATH=$(readlink -f "${BASH_SOURCE[0]}")
SCRIPT_DIR=$(dirname "${SCRIPT_PATH}")

VENV_DIR="$SCRIPT_DIR/.venv_linux"
DIST_DIR="$SCRIPT_DIR/dist_linux"

echo "### Preparing virtualenv..."
if [ ! -e "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
echo "### Preparing virtualenv... Done"

echo "### Installing pyinstaller..."
pip install pyinstaller
echo "### Installing pyinstaller... Done"

echo "### Installing packages..."
pip install rich
echo "### Installing packages... Done"

echo "### Building exe..."
python -m PyInstaller --distpath $DIST_DIR --add-data "$SCRIPT_DIR/misc/vip_download_tool/fh_loader:misc/vip_download_tool" --add-data "$SCRIPT_DIR/misc/vip_download_tool/QSaharaServer:misc/vip_download_tool" -F t29008.py
echo "### Building exe... Done"

echo "### Copying misc..."
echo "### Copying misc... Done"

echo "### Leaving virtualenv..."
deactivate
echo "### Leaving virtualenv... Done"

echo
echo
echo ">>> exe at [$DIST_DIR/t29008]"
