from tkinter import Toplevel, Label, CENTER, PhotoImage, LEFT
import tkinter as tk
import pandas as pd
import matplotlib
import scipy
import statsmodels
import prettytable
import seaborn
import platform
##############
from pandastable_local.app import DataExplore
from pandastable_local.dialogs import getParentGeometry


def get_tkver():
    # Create a root window
    root = tk.Tk()

    # Get the Tcl/Tk version
    tcl_version = root.tk.call("info", "patchlevel")
    tk_version = root.tk.call("info", "patchlevel")

    print(f"Tcl version: {tcl_version}")
    print(f"Tk version: {tk_version}")

    # Destroy the root window
    root.destroy()
    return tk_version


class Minijmp_pre(DataExplore):
    def about(self):
        """About dialog"""

        abwin = Toplevel()
        x, y, w, h = getParentGeometry(self.main)
        abwin.geometry('+%d+%d' % (x + w / 2 - 200, y + h / 2 - 200))
        abwin.title('About')
        abwin.transient(self)
        abwin.grab_set()
        abwin.resizable(width=False, height=False)
        abwin.configure(background=self.bg)
        logo = PhotoImage(file="icon.png")
        label = Label(abwin, image=logo, anchor=CENTER)
        label.image = logo
        label.grid(row=0, column=0, sticky='ew', padx=4, pady=4)
        pandasver = pd.__version__
        pythonver = platform.python_version()
        mplver = matplotlib.__version__
        scipyver = scipy.__version__
        smver = statsmodels.__version__
        ptver = prettytable.__version__
        sbver = seaborn.__version__
        tkver = get_tkver()

        text = 'Minijmp\n'\
            + 'version 0.1\n'\
            + 'Copyright (C) G.Du 2024-\n'
        tmp = Label(abwin, text=text, anchor=CENTER, justify=CENTER)
        tmp.grid(row=1, column=0, sticky='news', pady=2, padx=4)
        text = 'This program is free software; you can redistribute it and/or\n'\
            + 'modify it under the terms of the GNU General Public License\n'\
            + 'as published by the Free Software Foundation; either version 3\n'\
            + 'of the License, or (at your option) any later version.\n'\
            + """
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied 
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public 
License along with this program. If not, write to

   The Free Software Foundation, Inc.
   51 Franklin Street, Fifth Floor
   Boston, MA 02110-1335  USA
""" \
            + '\nUsing: \n'\
            + 'DataExplore 0.13 D. Farrell\n' \
            + 'Python v%s, Tk v%s\n' % (pythonver, tkver)\
            + 'pandas v%s, matplotlib v%s\n' % (pandasver, mplver) \
            + 'Scipy v%s, Statsmodels v%s\n' % (scipyver, smver)\
            + 'PrettyTable v%s, Seaborn v%s\n' % (ptver, sbver)\
+"""
Calibration:
All stats calucaltion give either same results to JMP 17, Minitab
20, or both. (Correct, they do not always agree with each other.)
"""

        # for line in text:
        tmp = Label(abwin, text=text, anchor='w', justify=LEFT)
        tmp.grid(row=2, column=0, sticky='w', pady=2, padx=4)

        return
