from tkinter import BOTH, Toplevel, VERTICAL, LEFT, TOP, END, BOTTOM, filedialog
from tkinter import ttk
import tkinter as tk
import os
#####################################
from pandastable_local.plotting import addButton
from pandastable_local import images
from pandastable_local.dialogs import (
    apply_dialog_theme, dialog_style, text_widget_colors)
############# Own Modules ###########
from plots import plot_viewer


class txt_viewer(plot_viewer):
    def __init__(self, table, parent=None):

        self.parent = parent
        self.table = table
        if table is not None:
            self.table.tOut = self  # opaque ref

        if self.parent is not None:
            ttk.Frame.__init__(self, parent)
            self.main = self.master
        else:
            self.main = Toplevel()
            self.master = self.main
            self.main.title('Output')
            self.main.protocol("WM_DELETE_WINDOW", self.close)
            g = '720x700'
            self.main.geometry(g)
        self.orient = VERTICAL
        self.ui_style = dialog_style(self.main)
        self.setupGUI()
        self._apply_theme()
        self.currentdir = os.path.expanduser('~')
        return

    def _apply_theme(self):
        """Match output window to system light/dark appearance."""

        apply_dialog_theme(self.main)
        self.T.configure(**text_widget_colors(self.ui_style))
        return

    def setupGUI(self):
        """Add GUI elements"""

        self.m = ttk.Frame(self.main)
        self.m.pack(fill=BOTH, expand=1)
        self.plotfr = ttk.Frame(self.m)
        self.T = tk.Text(self.plotfr)
        self.vsb = ttk.Scrollbar(
            self.plotfr,
            orient="vertical",
            command=self.T.yview)
        self.T.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.T.pack(side="left", fill="both", expand=True)
        self.plotfr.pack(side=TOP, fill=BOTH, expand=1)

        self.ctrlfr = ttk.Frame(self.main)
        self.ctrlfr.pack(side=BOTTOM, fill=BOTH)

        bf = ttk.Frame(self.ctrlfr, padding=2)
        bf.pack(side=TOP, fill=BOTH)
        side = LEFT
        addButton(bf, 'Clear', self.clear, images.plot_clear(),
                  'clear content', side=side)
        addButton(bf, 'Save', self.save, images.save(),
                  'save content', side=side)

        return

    def add_txt(self, txt):
        self.T.insert(END, txt)
        return

    def save(self, filename=None):
        """Save the current plot"""

        ftypes = [('txt', '*.txt')]
        if filename is None:
            filename = filedialog.asksaveasfilename(parent=self.master,
                                                    initialdir=self.currentdir,
                                                    filetypes=ftypes)
        if filename:
            self.currentdir = os.path.dirname(os.path.abspath(filename))
            try:
                with open(filename, 'w') as file:
                    text_content = self.T.get("1.0", "end-1c")
                    file.write(text_content)
            except BaseException:
                print("write file", filename, "error")
        return

    def clear(self):
        self.T.delete('1.0', END)
        return

    def close(self):
        print('txt win close')
        try:
            self.table.tOut = None
        except BaseException:
            pass
        self.main.destroy()
        return

    def to_end(self):
        self.T.see("end")
