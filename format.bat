@echo off

REM Check if black is installed, if not install it
black --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Black is not installed. Installing Black...
    pip install black
)

echo Formatting Python code...
black fably tools
