import os
import subprocess
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
    try:
        subprocess.run(['python3', 'MiniJMP.py'])
    except FileNotFoundError:
        subprocess.run(['pythonw', 'MiniJMP.py'])

