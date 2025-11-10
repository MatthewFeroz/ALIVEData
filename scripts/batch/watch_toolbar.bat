@echo off
REM Development script: Watch for changes and auto-rebuild toolbar EXE
cd /d "%~dp0\..\.."
python scripts\watch_and_build.py --run

