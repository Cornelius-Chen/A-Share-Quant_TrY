@echo off
setlocal

set "REPO_ROOT=D:\Creativity\A-Share-Quant_TrY"
set "PYTHON_EXE=D:\Tool\Anaconda\python.exe"
set "SCRIPT_PATH=%REPO_ROOT%\src\a_share_quant\info_center\automation\orchestration\materialize_a_share_internal_hot_news_runtime_scheduler_v1.py"

if not exist "%PYTHON_EXE%" (
    exit /b 1
)

if not exist "%SCRIPT_PATH%" (
    exit /b 1
)

cd /d "%REPO_ROOT%"
"%PYTHON_EXE%" "%SCRIPT_PATH%"

endlocal
