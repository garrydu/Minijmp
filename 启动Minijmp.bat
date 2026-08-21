@echo off
REM ============================================
REM  Minijmp 启动脚本（使用虚拟环境 Python 3.10）
REM  双击本文件即可启动，不弹黑色控制台窗口
REM ============================================
cd /d "%~dp0code"
start "" "%~dp0.venv\Scripts\pythonw.exe" "MiniJMP.py"
