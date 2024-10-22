from pandastable_local.dialogs import BaseDialog, EasyListbox, FindReplaceDialog
from tkinter import Frame, TOP, LEFT, X, BOTH, Listbox, Label, Scrollbar, VERTICAL, N, S, E, W, END, EXTENDED
import tkinter as tk
import numpy as np
from prettytable import PrettyTable as PT
#  import pandas as pd
############### Own Modules ############
from utilities import is_void, get_number


class findRepDialog(FindReplaceDialog):

    def find(self):
        """Do string search. Creates a masked dataframe for results and then stores each cell
        coordinate in a list."""

        table = self.table
        df = table.model.df
        df = df.astype('object').astype('str')
        s = self.searchvar.get()
        case = self.casevar.get()
        self.search_changed = False
        self.clear()
        if s == '':
            return
        s = s if case else s.upper()
        found = df.copy()
        for y in range(df.shape[0]):
            for x in range(df.shape[1]):
                found.iloc[y, x] = False
                if is_void(df.iloc[y, x]):
                    continue
                a = str(df.iloc[y, x]) if case else str(df.iloc[y, x]).upper()
                found.iloc[y, x] = (a == s)

        table.highlighted = found
        self.coords = [(x, y) for y in range(df.shape[0])
                       for x in range(df.shape[1]) if found.iloc[y, x]]
        self.current = 0
        return

    def replace(self):
        """Replace all instances of search text"""

        table = self.table
        table.storeCurrent()
        df = table.model.df
        self.find()
        r = self.replacevar.get()
        for x, y in self.coords:
            df.iloc[y, x] = r
        table.redraw()
        self.search_changed = True
        return

    def findNext(self):
        return


class Dialogs(BaseDialog):
    def __init__(self, parent=None, df=None, title='', app=None):

        BaseDialog.__init__(self, parent, df, title)
        self.app = app
        m = Frame(self.main)
        m.pack(side=TOP)

        self.cols = list(self.df.columns)
        self.valcols = list(
            self.df.select_dtypes(
                include=[
                    np.float64,
                    np.int32,
                    np.int64]))
        #  self.vars = OrderedDict()
        self.title = title
        self.add_window_help(m)
        self.createWidgets(m)
        self.buttonsFrame()
        print("Gen new dialog", self.title)
        return

    def add_window_help(self, m):
        f = tk.LabelFrame(m, text='')
        f.pack(side=TOP, fill=BOTH, padx=2)
        txt = self.app.dialog_help_msg(key=self.title)
        #  print("Receive txt", txt)
        if len(txt) == 0:
            return
        txt = txt + " [Click HELP for more info.]"
        w = tk.Label(
            f,
            anchor="w",
            justify=LEFT,
            wraplength=400,
            text=txt)
        w.pack(side=TOP, fill=BOTH, padx=3, pady=3)
        return

    def help(self):
        self.app.online_documentation(key=self.title)
        return

    def buttonsFrame(self):
        bf = Frame(self.main)
        bf.pack(side=TOP, fill=BOTH)
        b = tk.Button(bf, text="OK", command=self.ok)
        b.pack(side=LEFT, fill=X, expand=1, pady=2)
        b = tk.Button(bf, text="Cancel", command=self.quit)
        b.pack(side=LEFT, fill=X, expand=1, pady=2)
        b = tk.Button(bf, text="Help", command=self.help)
        b.pack(side=LEFT, fill=X, expand=1, pady=2)
        return

    def ok(self):
        self.quit()
        self.apply()
        return

    def add_xy_plot_settings(self, m):
        self.add_x_plot_settings(m)
        self.add_y_plot_settings(m)
        self.add_misc_plot_settings(m)
        return

    def add_x_plot_settings(self, m):
        self.xlabel = tk.StringVar(value="")
        self.x_min = tk.StringVar(value="Auto")
        self.x_max = tk.StringVar(value="Auto")

        master = tk.LabelFrame(m, text='X Axis')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Label")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.xlabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Min")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.x_min,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Max")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.x_max,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        return

    def add_y_plot_settings(self, m):
        self.ylabel = tk.StringVar(value="")
        self.y_min = tk.StringVar(value="Auto")
        self.y_max = tk.StringVar(value="Auto")

        master = tk.LabelFrame(m, text='Y Axis')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Label")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.ylabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Min")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.y_min,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Max")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.y_max,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        return

    def add_misc_plot_settings(self, m):
        self.grid = tk.BooleanVar(value=False)
        self.show_legend = tk.BooleanVar(value=False)
        self.ax_margin = tk.DoubleVar(value=0.1)

        master = tk.LabelFrame(m, text='Plot Setting')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Checkbutton(master, text='Show Grid',
                           variable=self.grid)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='Show Legend',
                           variable=self.show_legend)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Margin")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.ax_margin,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        return

    def add_alpha(self, m):
        self.alpha = tk.DoubleVar(value=0.05)
        master = tk.LabelFrame(m, text='Alpha for CI and etc.')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Alpha")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.alpha,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        return

    def get_plot_settings(self):
        self.get_x_plot_settings()
        self.get_y_plot_settings()
        self.get_misc_plot_settings()
        return

    def get_x_plot_settings(self):
        self.x_max = get_number(self.x_max)
        self.x_min = get_number(self.x_min)
        self.xlabel = None if self.xlabel.get() == "" else self.xlabel.get()
        return

    def get_y_plot_settings(self):
        self.y_max = get_number(self.y_max)
        self.y_min = get_number(self.y_min)
        self.ylabel = None if self.ylabel.get() == "" else self.ylabel.get()
        return

    def get_misc_plot_settings(self):
        self.ax_margin = self.ax_margin.get()
        self.show_legend = self.show_legend.get()
        self.grid = self.grid.get()
        return

    def update_vars(self):
        """ Do nothing, can be updated """
        return

    def error(self, msg=None):
        if msg is None:
            return
        t = PT()
        t.field_names = ["ERROR"]
        t.add_row([msg])
        self.app.print("\n" + str(t))
        return


class superEasyListbox(EasyListbox):
    def __init__(
            self,
            parent,
            width,
            height,
            yscrollcommand,
            listItemSelected):
        self._listItemSelected = listItemSelected
        Listbox.__init__(self, parent,
                         width=width, height=height,
                         yscrollcommand=yscrollcommand,
                         selectmode=EXTENDED, exportselection=0)
        self.bind("<<ListboxSelect>>", self.triggerListItemSelected)
        self.configure(background='white', foreground='black',
                       selectbackground='#0174DF', selectforeground='white')
        return


def addListBox(parent, values=[], width=10, height=6, label=''):
    """Add an EasyListBox"""

    frame = Frame(parent)
    Label(frame, text=label).grid(row=0)
    yScroll = Scrollbar(frame, orient=VERTICAL)
    yScroll.grid(row=1, column=1, sticky=N + S)

    def listItemSelected(index):
        return index
    lbx = superEasyListbox(frame, width, height, yScroll.set, listItemSelected)
    lbx.grid(row=1, column=0, sticky=N + S + E + W)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    yScroll["command"] = lbx.yview
    for i in values:
        lbx.insert(END, i)
    return frame, lbx
