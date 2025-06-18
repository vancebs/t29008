#! /bin/bash

echo "==========================================================="
echo "= NOTE:                                                   ="
echo "=     Suggest to generate a single binary with build.sh   ="
echo "=     for better user experience!!                        ="
echo "==========================================================="

SCRIPT_PATH=$(readlink -f "${BASH_SOURCE[0]}")
SCRIPT_DIR=$(dirname "${SCRIPT_PATH}")

VENV_DIR="$SCRIPT_DIR/.venv_linux"
PYTHON_FILE="$SCRIPT_DIR/t29008.py"

# enter venv
if [ ! -e "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# install dependence if needed
if ! pip3 show rich > /dev/null 2>&1; then
  echo "Installing dependence..."
  pip install rich
  echo "Installing dependence... Done"
fi

# run
python3 "$PYTHON_FILE" $@

# leave venv
deactivate
