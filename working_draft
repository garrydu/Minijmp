# Minijmp
![Main Screenshot](docs/images/main.png "Screenshot")


Minijmp is a free, open-source program that works like Minitab Express, but comes with extra tools you'd usually find in JMP or Minitab. As of early 2024, I couldn't find any free programs that could do what JMP and Minitab do, so I decided to build one myself while working on statistics with Python.


## Current Features
The software was developed based on [PandasTable](https://github.com/dmnfarrell/pandastable) (by D. Farrell), utilizing its spreadsheet UI and DataFrame backend. Minijmp replicates approximately 70% of Minitab Express's statistical functions (Ver. 0.1) and includes features like orthogonal regression, GRR, and Cpk calculations. It also has JMP features I like, such as the comparison of means under JMP ANOVA, and Hoeffding's D correlation.

All mathematical calculations have been calibrated against both Minitab and JMP. Since these software packages sometimes produce different results (e.g., in variance tests), Minijmp either:
- Provides options to choose between different algorithms, or
- Follows one software's approach and notes which one it follows

A quick overview of available functions (as of version 0.1) is shown below. More functions will be added after documentation and help files are completed.

![Menu Screenshot](docs/images/menu.png)

## Documentation

For installation instructions, see below. For usage guidelines, please refer to [the manual](https://minijmp.readthedocs.io/en/latest/) (under construction).

Much more information available at [https://minijmp.readthedocs.io](https://minijmp.readthedocs.io)

![Read the docs](docs/images/readthedocs.png)

## Installation

Currently, the only available method is to download the source code and run it using Python 3.8+. This approach works across all major platforms (**Linux, Windows, and MacOS**). Compiled releases will be available in the future.

It is highly recommended to run Minijmp in a **VIRTUAL ENV.**. The software requires specific Numpy versions compatible with Scipy. (Note: Virtual environment activation instructions are not included here.)

Install the required python libraries. 

```
cd Minijmp
pip3 install -r requirements.txt
```

Run the software.

```
cd Minijmp
python start.py
```

### Trouble Shooting

Confirm the python version is not lower  than 3.8.

```
python --version
```

In some system, may try to specify `python3` to boot the program, in case `python` links to old versions.


### Dependencies

The code requires Python 3.8.10 or higher. PandasTable is already included in the source code. Due to significant modifications to the original PandasTable class, it's maintained within the package to avoid code complexity. For all other dependencies, please refer to the requirements.txt file.

