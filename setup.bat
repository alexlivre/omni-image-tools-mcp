@echo off
echo ====================================
echo omni-image-tools-mcp Setup (Windows)
echo ====================================
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv is not installed or not in PATH
    echo Install from https://docs.astral.sh/uv/
    pause
    exit /b 1
)

echo [1/2] Installing dependencies via uv...
uv sync
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [2/2] Installing dev dependencies...
uv sync --extra dev
if errorlevel 1 (
    echo WARNING: Failed to install dev dependencies
    echo Continuing with base installation...
)

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo To configure your provider, set these environment variables
echo (or via the MCP host config): OMNI_VISION_PROVIDER and OMNI_VISION_API_KEY.
echo See the README "Como configurar cada provedor" section for details.
echo.
echo To test the setup:
echo   uv run python scripts/cli.py analyze --image test.jpg --prompt "Describe this"
echo.
echo To activate the virtual environment:
echo   .venv\Scripts\activate
echo.
pause