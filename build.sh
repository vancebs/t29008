#! /bin/bash

VENV_DIR=".venv_linux"
DIST_DIR="dist_linux"

echo "### Preparing virtualenv..."
if [ ! -e $VENV_DIR ]; then
    python3 -m venv $VENV_DIR
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
python -m PyInstaller --distpath $DIST_DIR --add-data "misc/vip_download_tool/fh_loader:misc/vip_download_tool" --add-data "misc/vip_download_tool/QSaharaServer:misc/vip_download_tool" -F t29008.py
echo "### Building exe... Done"

echo "### Copying misc..."
echo "### Copying misc... Done"

echo "### Leaving virtualenv..."
deactivate
echo "### Leaving virtualenv... Done"
