@echo off

REM Check if pylint is installed, if not install it
pylint --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pylint could not be found, installing...
    pip install pylint
)

echo Running pylint...
pylint fably tools/*.py servers/stt_server/*.py servers/tts_server/*.py 
