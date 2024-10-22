from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, X, BOTH
########### Own Modules ###########
from dialog import addListBox
from utilities import number_list, get_number, stack_df_num_cols
from dist_fit import compare_dist
from sb_histo import histo_n_fit, histo_full, histo_xy
from sbplot_dialog import SBDialog


class singleHistoDialog(SBDialog):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Data')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = tk.Label(f, text="Data Column")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        ####### extension #######
        self.update_vars()

        self.add_histo_setting(m)
        master = tk.LabelFrame(m, text='Distribution Fit')
        master.pack(side=TOP, fill=BOTH, padx=2)
        dist_list = [
            "Normal",
            "Student's t",
            "Gamma",
            "Lognormal",
            "Exponential",
            "Weibull"]
        self.dist = tk.StringVar(value=dist_list[0])
        w = tk.Label(master, text="Distribution")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            master, values=dist_list, textvariable=self.dist,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.fit_dist = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='Show Fit',
                           variable=self.fit_dist)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_x_plot_settings(m)
        self.add_misc_plot_settings(m)
        return

    def add_histo_setting(self, m):
        master = tk.LabelFrame(m, text='Histogram Setting')
        master.pack(side=TOP, fill=BOTH, padx=2)
        stat_list = ['count', 'frequency', 'proportion', 'percent', 'density']
        self.stat = tk.StringVar(value=stat_list[0])
        w = tk.Label(master, text="Stats.")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            master, values=stat_list, textvariable=self.stat,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.bins = tk.StringVar(value="Auto")
        w = tk.Label(master, text="Bins")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.bins,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        self.binwidth = tk.StringVar(value="Auto")
        w = tk.Label(master, text="Bin Width")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.binwidth,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

    def apply(self):
        self.get_x_plot_settings()
        self.get_misc_plot_settings()
        self.get_histo_setting()

        xvar = self.xvar.get()
        if xvar == "":
            return
        data = number_list(
            self.df[xvar],
            col_name=xvar,
            print_out=True,
            print_port=self.app.print)
        fit_dist = self.fit_dist.get()
        rv = None
        if fit_dist:
            res = compare_dist(data, print_out=True,
                               print_port=self.app.print,
                               selected=[self.dist.get()])
            if len(res) > 0:
                rv = res[0][2]['rv']
            else:
                self.error("Can't perform fit with the dist..")
                #  fit_dist = False
        cols = [xvar]
        self.make_working_df(cols=cols)

        pf = self.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        histo_n_fit(df=self.working_df, xkey=xvar, fig=pf.fig,
                    xlabel=self.xlabel_v if self.xlabel_v != "" else xvar,
                    x_max=self.x_max_v, x_min=self.x_min_v,
                    bins=self.bins_v, binwidth=self.binwidth_v,
                    stat=self.stat.get(), rv=rv, ax=pf.ax,
                    ax_margin=self.ax_margin_v,
                    legend=self.show_legend_v,
                    grid=self.grid_v)
        return

    def get_histo_setting(self):
        def none_neg(x):
            return -1 if x is None else x
        bins = none_neg(get_number(self.bins))
        binwidth = none_neg(get_number(self.binwidth))
        self.bins_v = int(bins) if bins > 0 else 'auto'
        self.binwidth_v = binwidth if binwidth > 0 else None
        return


class multiHistoDialog(singleHistoDialog):
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
        #  anchor="e", justify=LEFT, wraplength=100)
        w.pack(side=LEFT, fill=X, padx=10)
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='columns')
        w.pack(side=LEFT, fill=X, padx=10)

        master = tk.LabelFrame(m, text='Extended Features')
        master.pack(side=TOP, fill=BOTH, padx=2)
        multiple_list = ['layer', 'dodge', 'stack', 'fill']
        self.multiple = tk.StringVar(value=multiple_list[0])
        w = tk.Label(master, text="Multiple")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            master, values=multiple_list, textvariable=self.multiple,
            width=5)
        w.pack(side=LEFT, padx=2)
        element_list = ['bars', 'step', 'poly']
        self.element = tk.StringVar(value=element_list[0])
        w = tk.Label(master, text="Element")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            master, values=element_list, textvariable=self.element,
            width=5)
        w.pack(side=LEFT, padx=2)
        self.kde = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='KDE',
                           variable=self.kde)
        w.pack(side=LEFT, padx=2, pady=2)
        self.kde_only = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text='KDE Only',
                           variable=self.kde_only)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_histo_setting(m)
        self.add_x_plot_settings(m)
        self.add_misc_plot_settings(m)  # , palette=True)
        self.add_palette_selection(m)
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
        self.get_x_plot_settings()
        self.get_misc_plot_settings()
        self.get_histo_setting()

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

        if self.xlabel_v == "":
            self.xlabel_v = "Groups" if xvar == "" else xvar

        fill = True
        linewidth = 1
        kde = self.kde.get()
        if self.kde_only.get():
            kde = True
            fill = False
            linewidth = 0

        histo_full(data=self.working_df, hue=grp, x=xvar,
                   xlabel=self.xlabel_v if self.xlabel_v != "" else xvar,
                   x_max=self.x_max_v, x_min=self.x_min_v,
                   bins=self.bins_v, binwidth=self.binwidth_v,
                   stat=self.stat.get(), ax=pf.ax,
                   ax_margin=self.ax_margin_v,
                   legend=self.show_legend_v,
                   grid=self.grid_v,
                   kde=kde, element=self.element.get(),
                   multiple=self.multiple.get(),
                   palette=self.palette.get(), fill=fill,
                   linewidth=linewidth
                   )
        return


class xyHistoDialog(SBDialog):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Data')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = tk.Label(f, text="X Data Column")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="Y Data Column")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        f = tk.LabelFrame(m, text='Grouping Data (Optional)')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.hue = tk.StringVar(value="")
        w = tk.Label(f, text="Hue Data Column")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.hue,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.add_histo_setting(m)
        self.add_x_plot_settings(m)
        self.add_y_plot_settings(m)
        self.add_misc_plot_settings(m)
        self.add_palette_selection(m)
        return

    def add_histo_setting(self, m):
        master = tk.LabelFrame(m, text='Histogram Setting')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.bins = tk.StringVar(value="Auto")
        w = tk.Label(master, text="Bins")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.bins,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        self.binwidth = tk.StringVar(value="Auto")
        w = tk.Label(master, text="Bin Width")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.binwidth,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

    def apply(self):
        self.get_x_plot_settings()
        self.get_y_plot_settings()
        self.get_misc_plot_settings()
        self.get_histo_setting()

        xvar = self.xvar.get()
        yvar = self.yvar.get()
        if xvar == "" or yvar == "":
            self.error("Missing X or Y data col.")
            return
        cols = [xvar, yvar]
        hue = self.hue.get()
        if hue == "":
            hue = None
        else:
            cols.append(hue)

        self.make_working_df(cols=cols)

        pf = self.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        histo_xy(data=self.working_df, x=xvar, y=yvar, hue=hue,
                 xlabel=self.xlabel_v if self.xlabel_v != "" else xvar,
                 ylabel=self.ylabel_v if self.ylabel_v != "" else yvar,
                 x_max=self.x_max_v, x_min=self.x_min_v,
                 y_max=self.y_max_v, y_min=self.y_min_v,
                 bins=self.bins_v, binwidth=self.binwidth_v,
                 ax=pf.ax,
                 palette=self.palette.get(),
                 ax_margin=self.ax_margin_v,
                 legend=self.show_legend_v,
                 grid=self.grid_v)
        return

    def get_histo_setting(self):
        def none_neg(x):
            return -1 if x is None else x
        bins = none_neg(get_number(self.bins))
        binwidth = none_neg(get_number(self.binwidth))
        self.bins_v = int(bins) if bins > 0 else 'auto'
        self.binwidth_v = binwidth if binwidth > 0 else None
        return
