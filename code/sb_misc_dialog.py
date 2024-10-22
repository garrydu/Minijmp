from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, X, BOTH
########### Own Modules ###########
from dialog import addListBox
from utilities import stack_df_num_cols
from sb_misc import count_plot, line_plot, dot_plot
from sb_box_dialog import singleBoxDialog
from sbplot_dialog import SBDialog


class countPlotDialog(singleBoxDialog):
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
        w = tk.Label(f, text="Group Col.(optional)")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.grouping,
            width=14)
        w.pack(side=LEFT, padx=2)

        f = tk.LabelFrame(m, text='Data in its own column')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(f, text="Overriding selections above"
                     + "\nESC to deselect.")  # ,
        #  anchor="e", justify=LEFT, wraplength=100)
        w.pack(side=LEFT, fill=X, padx=10)
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='columns')
        w.pack(side=LEFT, fill=X, padx=10)

        self.xlabel = tk.StringVar(value="")
        master = tk.LabelFrame(m, text='Plot Settings')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Label")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.xlabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)
        stat_list = ['count', 'probability', 'proportion', 'percent']
        self.stat = tk.StringVar(value=stat_list[0])
        w = tk.Label(master, text="Stats.")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            master, values=stat_list, textvariable=self.stat,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.add_y_plot_settings(m)
        self.add_y_refs(m)
        self.add_misc_plot_settings(m)  # , palette=True)
        self.add_palette_selection(m)
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
        return

    def get_misc_plot_settings(self):
        self.show_legend_v = self.show_legend.get()
        self.grid_v = self.grid.get()
        return

    def preview(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.apply()
        self.no_preview = False
        self.self_to_top()
        return

    def apply(self):
        self.get_y_plot_settings()
        self.get_misc_plot_settings()

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
            self.xlabel_v = "Groups" if xvar == "" else xvar

        count_plot(
            data=self.working_df,
            hue=grp,
            x=xvar,
            xlabel=self.xlabel_v if self.xlabel_v != "" else xvar,
            ylabel=self.ylabel_v,
            y_max=self.y_max_v,
            y_min=self.y_min_v,
            stat=self.stat.get(),
            ax=pf.ax, y_ref=self.yref.get(),
            show_y_ref_label=self.yref_label.get(),
            legend='auto' if self.show_legend_v else False,
            grid=self.grid_v,
            #  ax_margin=self.ax_margin_v,
            palette=self.palette.get())
        return


class linePlotDialog(SBDialog):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Y Data in one column')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = tk.Label(f, text="Y Data Col.")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.grouping = tk.StringVar(value="")
        w = tk.Label(f, text="Group Col.(optional)")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.grouping,
            width=14)
        w.pack(side=LEFT, padx=2)

        f = tk.LabelFrame(m, text='Y Data in its own column')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(f, text="Overriding selections above"
                     + "\nESC to deselect.")  # ,
        #  anchor="e", justify=LEFT, wraplength=100)
        w.pack(side=LEFT, fill=X, padx=10)
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='columns')
        w.pack(side=LEFT, fill=X, padx=10)

        f = tk.LabelFrame(m, text='X Data')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="X Data Col.")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.add_xy_plot_settings(m)
        self.add_y_refs(m)
        self.add_palette_selection(m)
        return

    def preview(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.apply()
        self.no_preview = False
        self.self_to_top()
        return

    def apply(self):
        self.get_plot_settings()

        xvar = self.xvar.get()
        yvar = self.yvar.get()
        if yvar == "":
            self.error("Missing input X data.")
            return
        if len(self.grpcols) > 0:
            cols = self.grpcols
            #  cols.append(yvar)
            self.working_df = stack_df_num_cols(df=self.df, cols=cols, x=yvar)
            xvar = "Values"
            grp = "Labels"
        else:
            if xvar == "":
                self.error("Missing input Y data.")
                return
            grp = self.grouping.get()
            if grp != "":
                cols = [xvar, grp, yvar]
            else:
                cols = [xvar, yvar]
                grp = None
            self.make_working_df(cols=cols)

        pf = self.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        #  self.xlabel_v = self.xlabel.get()
        if self.xlabel_v is None:
            self.xlabel_v = yvar

        line_plot(
            data=self.working_df,
            hue=grp,
            y=xvar,
            x=yvar if yvar != "" else None,
            xlabel=self.xlabel_v if self.xlabel_v != "" else xvar,
            ylabel=self.ylabel_v,
            y_max=self.y_max_v,
            y_min=self.y_min_v,
            ax=pf.ax, y_ref=self.yref.get(),
            show_y_ref_label=self.yref_label.get(),
            legend='auto' if self.show_legend_v else False,
            grid=self.grid_v,
            ax_margin=self.ax_margin_v,
            palette=self.palette.get())
        return


class dotPlotDialog(SBDialog):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Y Data in one column')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = tk.Label(f, text="Y Data Col.")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.grouping = tk.StringVar(value="")
        w = tk.Label(f, text="Group Col.(optional)")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.grouping,
            width=14)
        w.pack(side=LEFT, padx=2)

        f = tk.LabelFrame(m, text='Y Data in its own column')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(f, text="Overriding selections above"
                     + "\nESC to deselect.")  # ,
        #  anchor="e", justify=LEFT, wraplength=100)
        w.pack(side=LEFT, fill=X, padx=10)
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='columns')
        w.pack(side=LEFT, fill=X, padx=10)

        f = tk.LabelFrame(m, text='X Data')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="X Data Col.")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.add_xy_plot_settings(m)
        self.add_y_refs(m)
        self.add_palette_selection(m)
        return

    def preview(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.apply()
        self.no_preview = False
        self.self_to_top()
        return

    def apply(self):
        self.get_plot_settings()

        xvar = self.xvar.get()
        yvar = self.yvar.get()
        if yvar == "":
            self.error("Missing input X data.")
            return
        if len(self.grpcols) > 0:
            cols = self.grpcols
            #  cols.append(yvar)
            self.working_df = stack_df_num_cols(df=self.df, cols=cols, x=yvar)
            xvar = "Values"
            grp = "Labels"
        else:
            if xvar == "":
                self.error("Missing input Y data.")
                return
            grp = self.grouping.get()
            if grp != "":
                cols = [xvar, grp, yvar]
            else:
                cols = [xvar, yvar]
                grp = None
            self.make_working_df(cols=cols)

        pf = self.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        #  self.xlabel_v = self.xlabel.get()
        if self.xlabel_v is None:
            self.xlabel_v = yvar

        dot_plot(
            data=self.working_df,
            hue=grp,
            y=xvar,
            x=yvar if yvar != "" else None,
            xlabel=self.xlabel_v if self.xlabel_v != "" else xvar,
            ylabel=self.ylabel_v,
            y_max=self.y_max_v,
            y_min=self.y_min_v,
            ax=pf.ax, y_ref=self.yref.get(),
            show_y_ref_label=self.yref_label.get(),
            legend='auto' if self.show_legend_v else False,
            grid=self.grid_v,
            ax_margin=self.ax_margin_v,
            palette=self.palette.get())
        return
