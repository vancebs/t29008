@echo off

SET SCRIPT_DIR=%~dp0
SET VENV_DIR=%~dp0.venv_windows
SET DIST_DIR=%~dp0dist_windows

echo ### Preparing virtualenv...
IF NOT EXIST %VENV_DIR% (
    python -m venv %VENV_DIR%
)
call %VENV_DIR%\Scripts\activate.bat
echo ### Preparing virtualenv... Done

echo ### Installing pyinstaller...
pip install pyinstaller
pip install pypiwin32
echo ### Installing pyinstaller... Done

echo ### Installing packages...
pip install rich
echo ### Installing packages... Done

echo ### Building exe...
python -m PyInstaller --distpath %DIST_DIR% --add-data "%SCRIPT_DIR%\misc\vip_download_tool\*.exe;misc\vip_download_tool" -F t29008.py
echo ### Building exe... Done

echo ### Copying misc...
echo ### Copying misc... Done

echo ### Leaving virtualenv...
call %VENV_DIR%\Scripts\deactivate.bat
echo ### Leaving virtualenv... Done

echo=
echo=
echo ">>> exe at [%DIST_DIR%/t29008.exe]"

@echo on
