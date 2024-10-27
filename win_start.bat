@echo off

REM if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit

REM Step 1: Move to the directory where the script is located
cd /d "%~dp0"

REM Step 2: Git pull
git pull
REM %windir%\system32\cmd.exe /c start /b "" cmd /c "git pull"
REM start /b "" cmd /c git pull

REM Step 3: Run Python script
pythonw start.py

