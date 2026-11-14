import os
import subprocess
import sys
from contextlib import contextmanager


@contextmanager
def change_dir(new_dir):
    old_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change to a subdirectory relative to the script's location
new_dir = os.path.join(script_dir, 'code')

def pick_python():
    """Prefer the project's virtualenv (has all requirements and a modern Tk).

    Falls back to the interpreter running this script. On macOS, Apple's
    /usr/bin/python3 ships the deprecated Tk 8.5, which shows a black window.
    """
    if os.name == 'nt':
        venv_py = os.path.join(script_dir, '.venv', 'Scripts', 'python.exe')
    else:
        venv_py = os.path.join(script_dir, '.venv', 'bin', 'python')
    if os.path.exists(venv_py):
        return venv_py
    return sys.executable


with change_dir(new_dir):
    subprocess.run([pick_python(), 'MiniJMP.py'])
