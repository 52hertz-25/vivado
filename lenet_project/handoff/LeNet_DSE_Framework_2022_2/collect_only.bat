@echo off
cd /d "%~dp0"
py -3 "%~dp0scripts\collect_results.py" "%~dp0"
pause
