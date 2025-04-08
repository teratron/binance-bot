@echo off
echo Installing dependencies with UV package manager...

REM Check if UV is installed
uv --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo UV package manager is not installed.
    echo Please install UV using: pip install uv
    exit /b 1
)

echo Creating virtual environment with UV...
uv venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies directly with UV...
echo This may take a few minutes...

REM Install packages
uv add binance-connector
uv add ta-lib
uv add numpy
uv add pandas
uv add python-dotenv-vault
uv add ruff
uv add mypy

echo.
echo Installation complete!
echo.
echo You can now run the bot using: python main.py
echo Make sure to update your .env file with your Binance API credentials.

pause