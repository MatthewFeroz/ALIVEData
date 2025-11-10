@echo off
REM Launcher script for ALIVE Data Floating Toolbar
cd /d "%~dp0\..\.."
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -m src.toolbar
) else (
    python -m src.toolbar
)

