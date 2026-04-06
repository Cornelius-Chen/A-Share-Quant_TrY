@echo off
setlocal

set "REPO_ROOT=D:\Creativity\A-Share-Quant_TrY"
set "PYTHON_EXE=D:\Tool\Anaconda\python.exe"
set "SCRIPT_PATH=%REPO_ROOT%\scripts\run_a_share_internal_hot_news_runtime_control_panel_v1.py"

if not exist "%PYTHON_EXE%" (
    echo Python not found:
    echo %PYTHON_EXE%
    pause
    exit /b 1
)

if not exist "%SCRIPT_PATH%" (
    echo Control panel script not found:
    echo %SCRIPT_PATH%
    pause
    exit /b 1
)

cd /d "%REPO_ROOT%"
start "" "%PYTHON_EXE%" "%SCRIPT_PATH%"

endlocal
