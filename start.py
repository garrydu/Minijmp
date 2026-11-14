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

# Use the context manager
with change_dir(new_dir):
    # Use the same interpreter that launched this script, so the app gets
    # that Python's Tk (e.g. Homebrew Tk 9) instead of whatever "python3"
    # resolves to on PATH (on macOS often Apple's /usr/bin/python3 with the
    # deprecated Tk 8.5, which renders a blank/black window).
    subprocess.run([sys.executable, 'MiniJMP.py'])
