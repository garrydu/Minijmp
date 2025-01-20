from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, X, BOTH
###################################
#  from pandastable_local.dialogs import addListBox
########### Own Modules ###########
from dialog import Dialogs
from GRR import grr_master, grr_nested
from utilities import is_void, is_number, grouping_by_labels, number_list, get_number
from cpk_plot import cpk_plot
from ti import ti_norm
from grr_plot import grr_plot


class GRR_Nested_Dialog(Dialogs):
    def createWidgets(self, m):
        ff = tk.LabelFrame(m, text='Input Columns')
        ff.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        f = tk.Frame(ff)
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="Measurement")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(f, text="Part #")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.Frame(ff)
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.ovar = tk.StringVar(value="")
        w = tk.Label(f, text="Operators")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.ovar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='Optional Input')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.hist_std = tk.StringVar(value="")
        w = tk.Label(f, text="Historical Process(total) StdDev")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = tk.Entry(f, textvariable=self.hist_std,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)

        return

    def apply(self):
        try:
            y = self.df[self.xvar.get()]
            p = self.df[self.yvar.get()]
            o = self.df[self.ovar.get()]
        except BaseException:
            self.error(msg="Input error or too few input items.")
            return

        r = [[], [], []]
        for i, j, k in zip(y, p, o):
            if is_void(j) or is_void(k):
                continue
            if is_number(i):
                r[0].append(float(i))
                r[1].append(j)
                r[2].append(k)

        if len(r[0]) < 4:
            self.error(msg="Input error: too few data points.")
            return

        try:
            grr_nested(
                y=r[0], part=r[1],
                op=r[2],  # if has_op else None,
                hist_std=get_number(self.hist_std),
                print_out=True,
                print_port=self.app.print)
        except ValueError as e:
            self.error(msg=e)
        return


class GRRDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Input Columns')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="Measurement")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(f, text="Part #")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='Optional Input')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.ovar = tk.StringVar(value="")
        w = tk.Label(f, text="Operators")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.ovar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='Algo Setting')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.mvar = tk.StringVar(value="AIAG (JMP17)")
        w = tk.Label(f, text="Method")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f,
            values=[
                "AIAG (JMP17)",
                "EMP (JMP17)",
                "XBAR/R (Minitab)"],
            textvariable=self.mvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)
        self.inter = tk.BooleanVar(value=True)
        w = tk.Checkbutton(f, text='Operator x Part Interaction',
                           variable=self.inter)
        w.pack(side=LEFT, padx=2, pady=2)

        self.ylabel = tk.StringVar(value="")
        #  self.show_legend = tk.BooleanVar(value=True)
        #  self.show_spec = tk.BooleanVar(value=True)
        master = tk.LabelFrame(m, text='Plot Setting')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Y Label")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.ylabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)
        #  w = tk.Checkbutton(master, text='Show Spec Limits',
        #                     variable=self.show_spec)
        #  w.pack(side=LEFT, padx=2, pady=2)
        #  w = tk.Checkbutton(master, text='Show Legend',
        #                     variable=self.show_legend)
        #  w.pack(side=LEFT, padx=2, pady=2)

        return

    def apply(self):
        y = self.df[self.xvar.get()]
        p = self.df[self.yvar.get()]
        try:
            o = self.df[self.ovar.get()]
            has_op = True
        except BaseException:
            o = [1] * len(y)
            has_op = False

        r = [[], [], []]
        for i, j, k in zip(y, p, o):
            if is_void(j) or is_void(k):
                continue
            if is_number(i):
                r[0].append(float(i))
                r[1].append(j)
                r[2].append(k)
        #  print(r)
        grr_master(
            y=r[0], part=r[1],
            op=r[2] if has_op else None,
            mode=self.mvar.get(),
            inter=self.inter.get(),
            print_out=True,
            print_port=self.app.print)

        pf = self.app.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)
        grr_plot(
            y=r[0], part=r[1],
            op=r[2] if has_op else None,
            ax=pf.ax,
            ylabel=self.ylabel.get() if self.ylabel.get() != "" else self.xvar.get())
        return


class CpkDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Input Column')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = tk.Label(f, text="Measurement")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        master = tk.LabelFrame(m, text='Enter Spec Limits')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.target = tk.DoubleVar(value=0)
        self.lsl = tk.DoubleVar(value=0)
        self.usl = tk.DoubleVar(value=0)
        w = tk.Label(master, text="LSL")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.lsl,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Target")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.target,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="USL")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.usl,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)

        self.show_within = tk.BooleanVar(value=True)
        w = tk.Checkbutton(
            m,
            text='Show within sigma of moving average of neighbor observations.',
            variable=self.show_within)
        w.pack(side=TOP, fill=BOTH, padx=2, pady=2)

        self.xlabel = tk.StringVar(value="")
        self.show_legend = tk.BooleanVar(value=True)
        self.show_spec = tk.BooleanVar(value=True)
        master = tk.LabelFrame(m, text='Plot Setting')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="X Label")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.xlabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='Show Spec Limits',
                           variable=self.show_spec)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='Show Legend',
                           variable=self.show_legend)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_alpha(m)
        return

    def apply(self):
        data = number_list(self.df[self.xvar.get()])

        alpha = self.alpha.get()
        if alpha > 0.5 or alpha <= 0:
            alpha = 0.05

        lsl, tgt, usl = self.lsl.get(), self.target.get(), self.usl.get()
        if lsl < tgt < usl:
            pass
        else:
            self.error("Spec limits input error.")
            return

        pf = self.app.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        cpk_plot(
            data,
            lsl,
            tgt,
            usl,
            print_out=True,
            print_port=self.app.print,
            xlabel=self.xlabel.get() if self.xlabel.get() != "" else self.xvar.get(),
            alpha=alpha,
            ax=pf.ax,
            show_legend=self.show_legend.get(),
            show_within=self.show_within.get(),
            show_spec=self.show_spec.get())

        return


class CpkSubDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Input Column')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = tk.Label(f, text="Measurement")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        master = tk.LabelFrame(m, text='Enter Spec Limits')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.target = tk.DoubleVar(value=0)
        self.lsl = tk.DoubleVar(value=0)
        self.usl = tk.DoubleVar(value=0)
        w = tk.Label(master, text="LSL")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.lsl,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Target")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.target,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="USL")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.usl,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='Subgroup')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.mvar = tk.StringVar(value="Use Subgrp Size")
        w = tk.Label(f, text="Option")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f,
            values=[
                #  "No Subgroups",
                "Use Subgrp ID Col.",
                "Use Subgrp Size"],
            textvariable=self.mvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.subid = tk.StringVar(value="")
        w = tk.Label(f, text="ID Col.")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.subid,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.subsize = tk.DoubleVar(value=2)
        w = tk.Label(f, text="Subgroup Size")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(f, textvariable=self.subsize,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='Within-Subgroup Variation')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.subm = tk.StringVar(value="Unbiased Std Dev")
        w = tk.Label(f, text="Average of")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f,
            values=[
                "Unbiased Std Dev",
                "Ranges"],
            textvariable=self.subm,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.xlabel = tk.StringVar(value="")
        self.show_legend = tk.BooleanVar(value=True)
        self.show_spec = tk.BooleanVar(value=True)
        self.show_within = tk.BooleanVar(value=True)
        master = tk.LabelFrame(m, text='Plot Setting')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="X Label")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.xlabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='Show Spec Limits',
                           variable=self.show_spec)
        w.pack(side=LEFT, padx=2, pady=2)
        #  w = tk.Checkbutton(master, text='Show Within',
        #                     variable=self.show_within)
        #  w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='Show Legend',
                           variable=self.show_legend)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_alpha(m)
        return

    def apply(self):
        m = self.mvar.get()
        if "ID" in m:
            ids = self.df[self.subid.get()]
            y = self.df[self.xvar.get()]
            id_r, y_r = [], []
            for i, j in zip(ids, y):
                if is_void(i):
                    continue
                if is_number(j):
                    id_r.append(i)
                    y_r.append(float(j))
            self.app.print(
                "Received %d valid data pairs for group ID and measurement." %
                len(y_r))
            data = grouping_by_labels(y_r, id_r)
        elif "ize" in m:
            y = number_list(self.df[self.xvar.get()])
            size = int(self.subsize.get())
            if size < 2:
                self.error("Subgroup size input error.")
                return
            data = [y[i:i + size] for i in range(0, len(y), size)]
            if len(y) % size > 0:
                self.app.print("WARNING: Unbalanced subgrouping.")
        else:
            data = number_list(self.df[self.xvar.get()])

        alpha = self.alpha.get()
        if alpha > 0.5 or alpha <= 0:
            alpha = 0.05

        use_range = "ange" in self.subm.get()

        lsl, tgt, usl = self.lsl.get(), self.target.get(), self.usl.get()
        if lsl < tgt < usl:
            pass
        else:
            self.error("Spec limits input error.")
            return

        pf = self.app.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        cpk_plot(
            data,
            lsl,
            tgt,
            usl,
            print_out=True,
            print_port=self.app.print,
            xlabel=self.xlabel.get() if self.xlabel.get() != "" else self.xvar.get(),
            use_range=use_range,
            alpha=alpha,
            ax=pf.ax,
            show_legend=self.show_legend.get(),
            show_within=self.show_within.get(),
            show_spec=self.show_spec.get())

        return


class TIDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Sample Values')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        master = tk.LabelFrame(m, text='Summarized Data (Overriding)')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.sample_mean = tk.StringVar(value="")
        self.sample_std = tk.StringVar(value="")
        self.sample_n = tk.StringVar(value="")
        w = tk.Label(master, text="N")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_n,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="SD")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_std,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Mean")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_mean,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        w = tk.Label(
            m,
            anchor="e",
            justify=LEFT,
            wraplength=300,
            text="Computes an interval that contains at least the specified" +
            " proportion of the population with (1-alpha) confidence, assuming" +
            " Normal Distribution.")
        w.pack(side=TOP, fill=BOTH, padx=2)

        master = tk.LabelFrame(m, text='Proportion Setting')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.prop = tk.DoubleVar(value=0.9)
        w = tk.Label(master, text="Specify Proportion to cover")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.prop,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_alpha(m)
        return

    def apply(self):
        data = number_list(self.df[self.xvar.get()])

        alpha = self.alpha.get()
        if alpha > 0.5 or alpha <= 0:
            alpha = 0.05
        std = get_number(self.sample_std)
        n = get_number(self.sample_n)
        mean = get_number(self.sample_mean)
        P = self.prop.get()
        if P > 1 or P <= 0:
            P = 0.9

        ti_norm(data=data, sample_n=n, sample_std=std,
                sample_mean=mean, alpha=alpha,
                P=P, print_out=True, print_port=self.app.print)

        return
