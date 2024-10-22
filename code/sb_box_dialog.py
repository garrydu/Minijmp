from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, X, BOTH
import ast
########### Own Modules ###########
from dialog import addListBox
from utilities import stack_df_num_cols, is_number
from sbplot_dialog import SBDialog
from sb_boxplot import single_boxplot, multi_boxplot


class singleBoxDialog(SBDialog):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Data in one column')
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

        f = tk.LabelFrame(m, text='Data in its own column')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(f, text="Overriding selections above"
                     + "\nESC to deselect.")  # ,
        w.pack(side=LEFT, fill=X, padx=10)
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='columns')
        w.pack(side=LEFT, fill=X, padx=10)

        self.xlabel = tk.StringVar(value="")
        master = tk.LabelFrame(m, text='X Axis')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Label")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.xlabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_y_plot_settings(m)
        self.add_y_refs(m)
        self.add_misc_plot_settings(m)  # , palette=True)
        self.add_box_settings(m)
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
        stat_list = ['Half', 'Full', '1/4']
        self.stat = tk.StringVar(value=stat_list[0])
        w = tk.Label(master, text="Box Width")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            master, values=stat_list, textvariable=self.stat,
            width=5)
        w.pack(side=LEFT, padx=2)
        return

    def get_misc_plot_settings(self):
        self.gap_v = {'Full': 0.1, 'Half': 0.5, '1/4': 0.75}[
            self.stat.get()]
        self.show_legend_v = self.show_legend.get()
        self.grid_v = self.grid.get()
        return

    def add_box_settings(self, m):
        master = tk.LabelFrame(m, text='Extended Features')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.swarm = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Swarm Dots',
                           variable=self.swarm)
        w.pack(side=LEFT, padx=2, pady=2)
        self.swarm_only = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Swarm Only',
                           variable=self.swarm_only)
        w.pack(side=LEFT, padx=2, pady=2)
        self.flier = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Hide Fliers',
                           variable=self.flier)
        w.pack(side=LEFT, padx=2, pady=2)
        self.logY = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Log Y',
                           variable=self.logY)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Professional Settings')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.native = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Native X Scale',
                           variable=self.native)
        w.pack(side=LEFT, padx=2, pady=2)
        self.whis = tk.StringVar(value="1.5")
        w = tk.Label(master, text="Whisker Length or Percentiles")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.whis,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)
        return

    def get_box_settings(self):
        self.swarm_v = self.swarm.get()
        swarm_only = self.swarm_only.get()
        self.hide_boxplot = False
        if swarm_only:
            self.hide_boxplot = True
            self.swarm_v = True
        self.flier_v = self.flier.get()
        self.logY_v = self.logY.get()
        self.native_v = self.native.get()
        self.whis_v = 1.5
        whis_str = self.whis.get()
        if is_number(whis_str):
            whis = float(whis_str)
            if whis >= 0:
                self.whis_v = whis
        else:
            try:
                # Convert the string to an actual tuple of floats
                tuple_of_floats = ast.literal_eval(whis_str)
                self.whis_v = (tuple_of_floats[0], tuple_of_floats[1])
            except BaseException:
                pass
        return

    def add_y_refs(self, m):
        master = tk.LabelFrame(m, text='Horizontal ref lines (optional)')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.yref = tk.StringVar(value="")

        w = tk.Label(master, text="Y positions (sep by ,)")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.yref,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)
        self.yref_label = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Show Label',
                           variable=self.yref_label)
        w.pack(side=LEFT, padx=2, pady=2)

        return

    def preview(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.apply()
        self.no_preview = False
        self.self_to_top()
        return

    def done(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.quit()
        self.apply()
        return

    def apply(self):
        self.get_y_plot_settings()
        self.get_misc_plot_settings()
        self.get_box_settings()

        xvar = self.xvar.get()
        if len(self.grpcols) > 0:
            self.working_df = stack_df_num_cols(df=self.df, cols=self.grpcols)
            xvar = "Values"
            grp = "Labels"
        else:
            if xvar == "":
                self.error("Missing input data.")
                return
            grp = self.grouping.get()
            if grp != "":
                self.make_working_df(cols=[xvar, grp])
            else:
                self.make_working_df(cols=[xvar])
                grp = None

        pf = self.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        self.xlabel_v = self.xlabel.get()
        if self.xlabel_v == "":
            self.xlabel_v = "Groups" if grp == "" else grp
        if self.ylabel_v == "":
            self.ylabel_v = "Values" if xvar == "" else xvar

        single_boxplot(
            data=self.working_df, x=grp, y=xvar,
            xlabel=self.xlabel_v, ylabel=self.ylabel_v,
            y_max=self.y_max_v, y_min=self.y_min_v,
            ax=pf.ax, y_ref=self.yref.get(),
            show_y_ref_label=self.yref_label.get(),
            legend='auto' if self.show_legend_v else False,
            grid=self.grid_v,
            fliersize=0 if self.flier_v else None,
            add_swarm=self.swarm_v, hide_box=self.hide_boxplot,
            whis=self.whis_v, log_scale=self.logY_v,
            native_scale=self.native_v, gap=self.gap_v
        )
        return


class multiBoxDialog(singleBoxDialog):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Data have to be stacked')
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

        f = tk.LabelFrame(m, text='Subgrouping')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.hue = tk.StringVar(value="")
        w = tk.Label(f, text="Subgrouping Col. (Hue)")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.hue,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.xlabel = tk.StringVar(value="")
        master = tk.LabelFrame(m, text='X Axis')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Label")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.xlabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_y_plot_settings(m)
        self.add_y_refs(m)
        self.add_misc_plot_settings(m)  # , palette=True)
        self.add_box_settings(m)
        self.add_palette_selection(m)
        return

    def preview(self):
        self.apply()
        self.no_preview = False
        self.self_to_top()
        return

    def add_box_settings(self, m):
        master = tk.LabelFrame(m, text='Extended Features')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.swarm = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Swarm Dots',
                           variable=self.swarm)
        w.pack(side=LEFT, padx=2, pady=2)
        self.flier = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Hide Fliers',
                           variable=self.flier)
        w.pack(side=LEFT, padx=2, pady=2)
        self.logY = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Log Y Scale',
                           variable=self.logY)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Swarm Dots Setting')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.swarm_only = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Swarm Only',
                           variable=self.swarm_only)
        w.pack(side=LEFT, padx=2, pady=2)
        self.swarm_dodge = tk.BooleanVar(value=True)
        w = tk.Checkbutton(master, text='Seperate',
                           variable=self.swarm_dodge)
        w.pack(side=LEFT, padx=2, pady=2)
        self.swarm_size = tk.DoubleVar(value=5)
        w = tk.Label(master, text="Size")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.swarm_size,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Professional Settings')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.native = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Native X Scale',
                           variable=self.native)
        w.pack(side=LEFT, padx=2, pady=2)
        self.whis = tk.StringVar(value="1.5")
        w = tk.Label(master, text="Whisker Length or Percentiles")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.whis,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)
        return

    def get_box_settings(self):
        self.swarm_v = self.swarm.get()
        swarm_only = self.swarm_only.get()
        self.hide_boxplot = False
        if swarm_only:
            self.hide_boxplot = True
            self.swarm_v = True
        self.swarm_dodge_v = self.swarm_dodge.get()
        swarm_size = self.swarm_size.get()
        self.swarm_size_v = 5
        if is_number(swarm_size):
            ss = float(swarm_size)
            if ss > 0:
                self.swarm_size_v = ss
        self.flier_v = self.flier.get()
        self.logY_v = self.logY.get()
        self.native_v = self.native.get()
        self.whis_v = 1.5
        whis_str = self.whis.get()
        if is_number(whis_str):
            whis = float(whis_str)
            if whis >= 0:
                self.whis_v = whis
        else:
            try:
                # Convert the string to an actual tuple of floats
                tuple_of_floats = ast.literal_eval(whis_str)
                self.whis_v = (tuple_of_floats[0], tuple_of_floats[1])
            except BaseException:
                pass
        return

    def apply(self):
        self.get_y_plot_settings()
        self.get_misc_plot_settings()
        self.get_box_settings()

        xvar = self.xvar.get()
        if xvar == "":
            self.error("Missing input data.")
            return
        grp = self.grouping.get()
        hue = self.hue.get()
        cols = [xvar]
        if grp != "":
            cols.append(grp)
        else:
            grp = None
        if hue != "":
            cols.append(hue)
        else:
            hue = None
        self.make_working_df(cols=cols)

        pf = self.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        self.xlabel_v = self.xlabel.get()
        if self.xlabel_v == "":
            self.xlabel_v = "Groups" if grp == "" else grp
        if self.ylabel_v == "":
            self.ylabel_v = "Values" if xvar == "" else xvar

        multi_boxplot(
            data=self.working_df, x=grp, y=xvar, hue=hue,
            palette=self.palette.get(),
            swarm_size=self.swarm_size_v,
            swarm_dodge=self.swarm_dodge_v,
            xlabel=self.xlabel_v, ylabel=self.ylabel_v,
            y_max=self.y_max_v, y_min=self.y_min_v,
            ax=pf.ax, y_ref=self.yref.get(),
            show_y_ref_label=self.yref_label.get(),
            legend='auto' if self.show_legend_v else False,
            grid=self.grid_v,
            fliersize=0 if self.flier_v else None,
            add_swarm=self.swarm_v, hide_box=self.hide_boxplot,
            whis=self.whis_v, log_scale=self.logY_v,
            native_scale=self.native_v, gap=self.gap_v
        )
        return
