from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, X, BOTH
from numpy import nan
from pandas import DataFrame as DF
###################################
#  from pandastable_local.dialogs import addListBox
########### Own Modules ###########
from dialog import Dialogs, addListBox
from utilities import number_list, stack_df_num_cols, is_void, group_df_to_list, hash_combined
from one_way_ANOVA import one_way_anova, JMP_ANOVA_t_test
from two_way_anova import two_way_anova
from sb_misc import interval_plot
from sbplot_dialog import SBDialog


class Anova2WayDialog(Dialogs):
    def createWidgets(self, m):

        f = tk.LabelFrame(m, text='Factors')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="A")
        w.pack(side=LEFT, fill=X, padx=2,pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2,pady=2)
        w = tk.Label(f, text="B")
        w.pack(side=LEFT, fill=X, padx=2,pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2,pady=2)

        f = tk.LabelFrame(m, text='Response')
        f.pack(side=TOP, fill=BOTH, padx=2,pady=2)
        self.zvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.zvar,
            width=14)
        w.pack(side=LEFT, padx=2,pady=2)

        return

    def apply(self):
        def f(A, Y):
            return [_ for _, __ in zip(A, Y) if not __]
        A = list(self.df[self.xvar.get()])
        B = list(self.df[self.yvar.get()])
        Y = list(self.df[self.zvar.get()])
        V = []
        for a, b, y in zip(A, B, Y):
            V.append(
                nan in [a, b, y])
        two_way_anova(f(Y, V), factor_listA=f(A, V), factor_listB=f(B, V),
                      print_out=True, print_port=self.app.print,
                      name_a=self.xvar.get(), name_b=self.yvar.get())
        return


class Anova1WayDialog_old(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Variables')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='columns')
        w.pack(side=LEFT, fill=X, padx=10)

        self.add_alpha(m)
        return

    def ok(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.quit()
        self.apply()
        return

    def apply(self):

        data = []
        for col in self.grpcols:
            data.append(
                number_list(
                    self.df[col],
                    col_name=col,
                    print_out=True,
                    print_port=self.app.print))
        try:
            alpha = self.alpha.get()
        except BaseException:
            alpha = 0.05

        one_way_anova(data, self.grpcols, print_out=True,
                      print_port=self.app.print,
                      alpha=alpha)
        return


class Anova1WayDialog(Dialogs):

    add_y_refs = SBDialog.add_y_refs
    make_working_df = SBDialog.make_working_df

    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Stacked Data')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = tk.Label(f, text="Data Col.")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.grouping = tk.StringVar(value="")
        w = tk.Label(f, text="Group Col.")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.grouping,
            width=14)
        w.pack(side=LEFT, padx=2)

        f = tk.LabelFrame(m, text='Data in separated columns')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(f, text="Overriding selections above" + "\nESC to deselect.")  # ,
        w.pack(side=LEFT, fill=X, padx=10)
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='columns')
        w.pack(side=LEFT, fill=X, padx=10)

        self.add_alpha(m)

        master = tk.LabelFrame(m, text='Mean Comparison')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.comp_mean = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text="Each Pair, Student's t",
                           variable=self.comp_mean)
        w.pack(side=LEFT, padx=2, pady=2)

        plot_setting = tk.LabelFrame(m, text='Interval Plot Setting')
        plot_setting.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        master = tk.Frame(plot_setting)
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.show_plot = tk.BooleanVar(value=True)
        w = tk.Checkbutton(master, text="Show Plot",
                           variable=self.show_plot)
        w.pack(side=LEFT, padx=2, pady=2)
        self.show_grid = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text="Show Grid",
                           variable=self.show_grid)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(plot_setting, text='X Axis')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Label")
        self.xlabel = tk.StringVar(value="")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.xlabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_y_plot_settings(plot_setting)
        self.add_y_refs(plot_setting)
        return

    def showPlotViewer(self):
        return self.app.showPlotViewer(
            save_last=True)

    def ok(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.quit()
        self.apply()
        return

    def apply(self):
        try:
            alpha = self.alpha.get()
        except BaseException:
            alpha = 0.05

        xvar = self.xvar.get()
        grp = self.grouping.get()
        if len(self.grpcols) > 0:
            self.working_df = stack_df_num_cols(df=self.df, cols=self.grpcols)
            xvar = "Values"
            grp = "Labels"
            data = []
            for col in self.grpcols:
                data.append(
                    number_list(
                        self.df[col],
                        col_name=col,
                        print_out=True,
                        print_port=self.app.print))
            groups = self.grpcols
        else:
            if xvar == "" or grp == "":
                self.error("Missing input data.")
                return
            else:
                self.make_working_df(cols=[grp], numcols=[xvar])
                data = group_df_to_list(self.df, y_key=xvar, grp_key=grp)
                data = [number_list(i) for i in data]
                groups = self.df[grp].unique()

        res = one_way_anova(data, groups, print_out=True,
                            print_port=self.app.print,
                            alpha=alpha)
        if self.comp_mean.get():
            JMP_ANOVA_t_test(data, groups, print_out=True,
                             print_port=self.app.print,
                             alpha=alpha)

        if not self.show_plot.get():
            return

        interval_dict = dict()
        for i, ci in zip(data, res['CI']):
            interval_dict[hash_combined(i)] = ci

        pf = self.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        self.get_y_plot_settings()
        self.xlabel_v = self.xlabel.get()
        self.ylabel_v = self.ylabel
        if self.xlabel_v == "":
            self.xlabel_v = "Groups" if grp == "" else grp
        if self.ylabel_v == "" or self.ylabel_v is None:
            self.ylabel_v = "Values" if xvar == "" else xvar

        interval_plot(
            data=self.working_df, x=grp, y=xvar,
            xlabel=self.xlabel_v, ylabel=self.ylabel_v,
            y_max=self.y_max, y_min=self.y_min,
            ax=pf.ax, y_ref=self.yref.get(),
            show_y_ref_label=self.yref_label.get(),
            grid=self.show_grid.get(),
            CIs=interval_dict,  # customize intervals
            title="Interval plot of %.1f%% CI of mean" % ((1 - alpha) * 100))

        return


class TtestDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Variables')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='columns')
        w.pack(side=LEFT, fill=X, padx=10)

        self.add_alpha(m)
        return

    def ok(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.quit()
        self.apply()
        return

    def apply(self):

        data = []
        for col in self.grpcols:
            data.append(
                number_list(
                    self.df[col],
                    col_name=col,
                    print_out=True,
                    print_port=self.app.print))
        try:
            alpha = self.alpha.get()
        except BaseException:
            alpha = 0.05

        JMP_ANOVA_t_test(data, self.grpcols, print_out=True,
                         print_port=self.app.print,
                         alpha=alpha)
        return
