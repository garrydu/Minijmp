from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, X, BOTH
from matplotlib.lines import Line2D
###################################
########### Own Modules ###########
#  from dialog import Dialogs
from cont_plot import cont_dist
from utilities import get_number
from sbplot_dialog import SBDialog


class comboNEntries:
    def __init__(self, combo_name, combo_list,
                 entry_name_list, master_frame):
        f = ttk.Frame(master_frame)
        f.pack(side=TOP, padx=2, pady=2)
        w = tk.Label(f, text=combo_name)
        w.pack(side=LEFT, padx=2)
        self.combo_select = tk.StringVar(value=combo_list[0])
        self.combo = ttk.Combobox(
            f, values=combo_list, textvariable=self.combo_select,
            width=14)
        self.combo.pack(side=LEFT, fill=X, padx=2)
        self.combo.bind("<<ComboboxSelected>>", self.update_entries)
        self.N = max(len(_) for _ in entry_name_list)
        self.entries = []
        for i in range(self.N):
            entry = dict()
            label = entry_name_list[0][i] if i < len(entry_name_list[0]) else "NA"
            entry["input"] = tk.StringVar(value="")
            f = ttk.Frame(master_frame)
            f.pack(side=TOP, padx=2, pady=2)
            w = tk.Label(f, text=label)
            w.pack(side=LEFT, padx=2)
            entry["label"] = w
            w = tk.Entry(f, textvariable=entry["input"],
                         bg='white', width=10)
            w.pack(side=LEFT, padx=2, pady=2)
            entry["entry"] = w
            if label == "NA":
                w.config(state='disabled')
            self.entries.append(entry)
        self.combo_list = combo_list
        self.entry_name_list = entry_name_list
        return

    def update_entries(self, _):
        combo_select = self.combo_select.get()
        idx = self.combo_list.index(combo_select)
        for i in range(self.N):
            label = self.entry_name_list[idx][i] if i < len(self.entry_name_list[idx]) else "NA"
            self.entries[i]["label"].config(text=label)
            self.entries[i]["input"].set("")
            if label == "NA":
                self.entries[i]["entry"].config(state='disabled')
            else:
                self.entries[i]["entry"].config(state='normal')
        return

    def get_values(self):
        res = dict()
        combo_select = self.combo_select.get()
        idx = self.combo_list.index(combo_select)
        for i in range(self.N):
            label = self.entry_name_list[idx][i] if i < len(self.entry_name_list[idx]) else "NA"
            res[label] = get_number(self.entries[i]['input'])
        return res, combo_select


class displayProbDialog(SBDialog):
    def createWidgets(self, m):
        """Create a set of grp-agg-func options together"""
        self.dist_list = ["Normal", "Chi Square", "F", "LogNormal", "t", "Binomial", "Poisson"]
        self.dist_entries = [["Mean", "Standard deviation"],
                             ["Degrees of freedom"],
                             ["Numerator degrees of freedom", "Denominator degrees of freedom"],
                             ["Scale"],
                             ["Degrees of freedom"],
                             ["Number of trials", "Event probability"], ["Mean"]]
        f = tk.LabelFrame(m, text='Distribution')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.dist = comboNEntries("Distribution",
                                  self.dist_list, self.dist_entries, f)

        f = tk.LabelFrame(m, text='Show the area corresponding to the following')
        f.pack(side=TOP, fill=BOTH, padx=2)
        master = ttk.Frame(f)
        master.pack(side=TOP, padx=2, pady=2)
        w = tk.Label(master, text="A specified probability")
        w.pack(side=LEFT, padx=2)
        self.P = tk.StringVar(value="")
        w = tk.Entry(master, textvariable=self.P,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)

        master = ttk.Frame(f)
        master.pack(side=TOP, padx=2, pady=2)
        w = tk.Label(master, text="A specified x value (overriding)")
        w.pack(side=LEFT, padx=2)
        self.X = tk.StringVar(value="")
        w = tk.Entry(master, textvariable=self.X,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)

        self.plot_out = tk.BooleanVar(value=True)
        w = tk.Checkbutton(f, text='Show Plot',
                           variable=self.plot_out)
        w.pack(side=TOP, padx=2, pady=2)
        return

    def apply(self):
        """Apply crosstab"""
        dist_args, dist_select = self.dist.get_values()
        p = get_number(self.P)
        if p is not None:
            if p <= 0 or p >= 1:
                p = None
        x = get_number(self.X)
        if x is not None:
            p = None
        plot_out = self.plot_out.get()

        if plot_out:
            pf = self.app.showPlotViewer()
            ax = pf.ax = pf.fig.add_subplot(111)
        else:
            ax = None

        cont_dist(dist=dist_select, p=p, x=x, print_out=True, plot_out=plot_out,
                  ax=ax, print_port=self.app.print, **dist_args)

        return


class displayProb2xDialog(SBDialog):
    def createWidgets(self, m):
        """Create a set of grp-agg-func options together"""
        self.dist_list = ["Normal", "Chi Square", "F", "LogNormal", "t", "Binomial", "Poisson"]
        self.dist_entries = [["Mean", "Standard deviation"],
                             ["Degrees of freedom"],
                             ["Numerator degrees of freedom", "Denominator degrees of freedom"],
                             ["Scale"],
                             ["Degrees of freedom"],
                             ["Number of trials", "Event probability"], ["Mean"]]
        f = tk.LabelFrame(m, text='Distribution 1')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.dist1 = comboNEntries("Distribution",
                                   self.dist_list, self.dist_entries, f)
        f = tk.LabelFrame(m, text='Distribution 2')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.dist2 = comboNEntries("Distribution",
                                   self.dist_list, self.dist_entries, f)

        return

    def apply(self):
        dist_args1, dist_select1 = self.dist1.get_values()
        dist_args2, dist_select2 = self.dist2.get_values()

        pf = self.app.showPlotViewer()
        ax = pf.ax = pf.fig.add_subplot(111)

        cont_dist(dist=dist_select1, print_out=True, plot_out=True, color='blue',
                  ax=ax, print_port=self.app.print, **dist_args1)
        cont_dist(dist=dist_select2, print_out=True, plot_out=True, color='green',
                  ax=ax, print_port=self.app.print, **dist_args2)
        # Create custom legend handles
        legend_handles = [
            Line2D([0], [0], color='blue', lw=2),  # Blue line for Dist. 1
            Line2D([0], [0], color='green', lw=2)  # Green line for Dist. 2
        ]

        # Add the legend to the axis with custom labels
        ax.legend(handles=legend_handles, labels=['Dist. 1', 'Dist. 2'])

        return
