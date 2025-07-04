# MacOS 15 Install

To run the code on MacOS, `brew` needs to be installed first, which is not discussed here. 

### Install tcl-tk
First step is to update the `tcl-tk` to the latest version. The versions older than 8.6 are known incompatible. 

```
brew install tcl-tk
brew install python-tk
```

It's recommended to reinstall python to update all paths that point to the `tk` folders.
```
brew reinstall python
```
Open a new terminal and test the `tk` version:
```
python3 -c "import tkinter; print(tkinter.TkVersion)"
```
The output version is expected to be equal or greater than 8.6.

### Install the software in virtual env
First download the code by zip and decrompress, or clone the repo. By default, the downloaded code is stored in the folder `Minijmp`. 

It's highly recommended to initiate a virtual environment in MacOS, since the system will show errors when install python packages with `pip` to the system directly. To start the virtual environment:
```
cd Minijmp
python3 -m venv venv
source venv/bin/activate
```
When seeing `(venv)` showing ahead of the command prompt, the virtual environment is successfully started.

Now install the required packages:
```
python3 -m pip install -r requirement.txt
```

Now the software is ready to run. To lauch the software, run this command in the `Minijmp` directory:
```
python3 start.py
```

### Known issues
#### 1. _tkinter.TclError: couldn't recognize image data
This should be caused by the version of `tcl-tk`. Run the command `python3 -c "import tkinter; print(tkinter.TkVersion)"` in the virtual environment to make sure the version is not older than 8.6. If not, try to upgrade `tk`, re-download the `Minijmp` to a new folder and initiate a new virtual environment.

#### 2. from scipy._lib._util import _lazywhere ImportError: cannot import name '_lazywhere' 
This error occurs because in newer versions of SciPy (after March 2025, version 1.16.0 and later), `_lazywhere` has been removed and is no longer publicly available. Many dependencies (such as statsmodels) that still try to import `_lazywhere` from `scipy._lib._util` will encounter this error.

To resolve this issue, you can try one of the following approaches:

1. **Downgrade SciPy** (Recommended for immediate fix):
   ```
   pip install "scipy<1.16"
   ```

2. **Update all dependencies** to their latest versions if step 1 didn't do the job:
   ```
   pip install --upgrade scipy statsmodels pandas numpy
   ```

