@echo off

SET VENV_DIR=.venv_windows
SET DIST_DIR=dist_windows

echo ### Preparing virtualenv...
IF NOT EXIST %VENV_DIR% (
    python -m venv %VENV_DIR%
)
cd %VENV_DIR%\Scripts
call activate.bat
cd ..\..
echo ### Preparing virtualenv... Done

echo ### Installing pyinstaller...
pip install pyinstaller
pip install pypiwin32
echo ### Installing pyinstaller... Done

echo ### Installing packages...
pip install rich
echo ### Installing packages... Done

echo ### Building exe...
python -m PyInstaller --distpath %DIST_DIR% --add-data "misc\vip_download_tool\*.exe;misc\vip_download_tool" -F t29008.py
echo ### Building exe... Done

echo ### Copying misc...
echo ### Copying misc... Done

echo ### Leaving virtualenv...
cd %VENV_DIR%\Scripts
call deactivate.bat
cd ..\..
echo ### Leaving virtualenv... Done
