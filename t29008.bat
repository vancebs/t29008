@echo off

echo ===========================================================
echo = NOTE:                                                   =
echo =     Suggest to generate a single exe with build.bat     =
echo =     for better user experience!!                        =
echo ===========================================================

SET SCRIPT_DIR=%~dp0

SET VENV_DIR=%~dp0.venv_windows
SET PYTHON_FILE=%~dp0t29008.py

:: Prepare virtualenv...
IF NOT EXIST %VENV_DIR% (
    python -m venv %VENV_DIR%
)
call %VENV_DIR%\Scripts\activate.bat

:: install dependence if needed
pip show rich > nul 2>&1
IF NOT %errorlevel% == 0 (
  echo Installing dependence...
  pip install rich
  echo Installing dependence... Done
)

:: run
python "%PYTHON_FILE%" %1 %2 %3 %4 %5 %6 %7 %8 %9

:: Leave virtualenv...
call %VENV_DIR%\Scripts\deactivate.bat

@echo on
