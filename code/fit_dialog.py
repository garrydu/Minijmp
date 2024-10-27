from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, X, BOTH, W
###################################
#  from pandastable_local.dialogs import addListBox
########### Own Modules ###########
from linear_plot import fit_plot, multi_fit
from dialog import Dialogs, addListBox
from Residual import linear_fit_resid_test
from utilities import number_2lists, number_2Dlist
from nonpara_cor import spearman, kendall, hoeffding


class LinearFitDialog(Dialogs):
    def createWidgets(self, m):
        """Create a set of grp-agg-func options together"""
        master = self.main
        f = tk.LabelFrame(m, text='X Y Values')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="X")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(f, text="Y")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        self.ellipse = tk.BooleanVar(value=False)
        self.red_ellipse = tk.BooleanVar(value=False)
        self.linear = tk.BooleanVar(value=True)
        self.ortho = tk.BooleanVar(value=False)
        self.ortho_ratio = tk.DoubleVar(value=1)
        self.show_CI = tk.BooleanVar(value=False)
        self.show_PI = tk.BooleanVar(value=False)
        self.scatter = tk.BooleanVar(value=True)

        ####### extension #######
        self.update_vars()

        master = tk.LabelFrame(m, text='Scatter Plot')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Checkbutton(master, text='Scatter Dots',
                           variable=self.scatter)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='Correlation Ellipse',
                           variable=self.ellipse)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='Ellipse Outline',
                           variable=self.red_ellipse)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Linear Fit')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Checkbutton(master, text='Show Fit',
                           variable=self.linear)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='Confidence Interval',
                           variable=self.show_CI)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='Prediction Interval',
                           variable=self.show_PI)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Orthogonal Fit')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Checkbutton(master, text='Show Fit',
                           variable=self.ortho)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Ratio")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.ortho_ratio,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_xy_plot_settings(m)
        self.add_alpha(m)
        return

    def apply(self):
        """Apply crosstab"""

        x, y = number_2lists(self.df[self.xvar.get()],
                             self.df[self.yvar.get()],
                             col_name1=self.xvar.get(), col_name2=self.yvar.get(),
                             print_out=True, print_port=self.app.print)
        pf = self.app.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        self.get_plot_settings()
        xlabel = self.xvar.get() if self.xlabel is None else self.xlabel
        ylabel = self.yvar.get() if self.ylabel is None else self.ylabel
        #  xlabel = self.xlabel if self.xlabel != "" or self.xlabel is not None else self.xvar.get()
        #  ylabel = self.ylabel if self.ylabel != "" or self.ylabel is not None else self.yvar.get()
        print("xlabel", xlabel, "y", ylabel)

        fit_plot(
            x,
            y,
            ax=pf.ax,
            print_port=self.app.print,
            alpha=self.alpha.get(),
            ortho_ratio=self.ortho_ratio.get(),
            ellipse=self.ellipse.get(),
            red_ellipse=self.red_ellipse.get(),
            linear=self.linear.get(),
            show_CI=self.show_CI.get(),
            ortho=self.ortho.get(),
            show_PI=self.show_PI.get(),
            xlabel=xlabel,  # self.xlabel if self.xlabel != "" or self.xlabel is None else self.xvar.get(),
            ylabel=ylabel,  # self.ylabel if self.ylabel != "" or self.ylabel is None else self.yvar.get(),
            x_min=self.x_min,
            y_min=self.y_min,
            x_max=self.x_max,
            y_max=self.y_max,
            ax_margin=self.ax_margin,
            show_legend=self.show_legend,
            grid=self.grid,
            scatter=self.scatter.get(),
            print_out=True)
        return


class CorrelationDialog(LinearFitDialog):
    def createWidgets(self, m):
        master = self.main
        f = tk.LabelFrame(m, text='X Y Values')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="X")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(f, text="Y")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Correlation Select')
        master.pack(side=TOP, fill=BOTH, padx=2)
        #  cor_list=['Pearson',"Hoeffding's D",
        #            "Spearman's rho", "Kendall's tau"]
        #  self.cor=tk.StringVar(value=cor_list[0])
        #  w = tk.Label(master, text="Box Width")
        #  w.pack(side=LEFT, fill=X, padx=2)
        #  w = ttk.Combobox(
        #      master, values=stat_list, textvariable=self.stat,
        #      width=5)
        #  w.pack(side=LEFT, padx=2)
        #  self.cor = tk.IntVar(value=4)
        #  w = tk.Radiobutton(master, text="Pearson: linear relationship", variable=self.cor, value=4)
        #  w.pack(side=TOP, anchor=W)
        #  w = tk.Radiobutton(master, text="Spearman's rho: monotonic relationship", variable=self.cor, value=0)
        #  w.pack(side=TOP, anchor=W)
        #  w = tk.Radiobutton(master, text="Kendall's tau: monotonic relationship", variable=self.cor, value=1)
        #  w.pack(side=TOP, anchor=W)
        #  w = tk.Radiobutton(master, text="Hoeffding's D: independent or not", variable=self.cor, value=2)
        #  w.pack(side=TOP, anchor=W)

        self.cor_p = tk.BooleanVar(value=True)
        self.cor_s = tk.BooleanVar(value=False)
        self.cor_k = tk.BooleanVar(value=False)
        self.cor_h = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text="Pearson: linear relationship", variable=self.cor_p)
        w.pack(side=TOP, anchor=W)
        w = tk.Checkbutton(master, text="Spearman's rho: monotonic relationship", variable=self.cor_s)
        w.pack(side=TOP, anchor=W)
        w = tk.Checkbutton(master, text="Kendall's tau: monotonic relationship", variable=self.cor_k)
        w.pack(side=TOP, anchor=W)
        w = tk.Checkbutton(master, text="Hoeffding's D: independent or not", variable=self.cor_h)
        w.pack(side=TOP, anchor=W)

        master = tk.LabelFrame(m, text='Scatter Plot')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.scatter = tk.BooleanVar(value=True)
        #  w = tk.Checkbutton(master, text='Scatter Dots',
        #                     variable=self.scatter)
        #  w.pack(side=LEFT, padx=2, pady=2)

        slave = tk.LabelFrame(master, text="Pearson's Correlation Only")
        slave.pack(side=TOP, fill=BOTH, padx=2)
        self.ellipse = tk.BooleanVar(value=True)
        self.red_ellipse = tk.BooleanVar(value=False)
        w = tk.Checkbutton(slave, text='Correlation Ellipse',
                           variable=self.ellipse)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(slave, text='Ellipse Outline',
                           variable=self.red_ellipse)
        w.pack(side=LEFT, padx=2, pady=2)
        self.alpha = tk.DoubleVar(value=0.05)
        w = tk.Label(slave, text="Alpha")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(slave, textvariable=self.alpha,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        #  self.add_alpha(slave)
        self.add_xy_plot_settings(master)
        return

    def apply(self):

        x, y = number_2lists(self.df[self.xvar.get()],
                             self.df[self.yvar.get()],
                             col_name1=self.xvar.get(), col_name2=self.yvar.get(),
                             print_out=True, print_port=self.app.print)
        pf = self.app.showPlotViewer()
        pf.ax = pf.fig.add_subplot(111)

        self.get_plot_settings()
        xlabel = self.xvar.get() if self.xlabel is None else self.xlabel
        ylabel = self.yvar.get() if self.ylabel is None else self.ylabel
        #  xlabel = self.xlabel if self.xlabel != "" or self.xlabel is not None else self.xvar.get()
        #  ylabel = self.ylabel if self.ylabel != "" or self.ylabel is not None else self.yvar.get()
        print("xlabel", xlabel, "y", ylabel)

        #  cor = self.cor.get()
        print_out = False
        red_ellipse = False
        ellipse = False
        if self.cor_p.get():
            red_ellipse = self.red_ellipse.get()
            ellipse = self.ellipse.get()
            print_out = True
        if self.cor_s.get():
            spearman(x, y, print_out=True, print_port=self.app.print)
        if self.cor_k.get():
            kendall(x, y, print_out=True, print_port=self.app.print)
        if self.cor_h.get():
            hoeffding(x, y, print_out=True, print_port=self.app.print)
        #  else:
        #      funcs = [spearman, kendall, hoeffding]
        #      funcs[cor](x, y, print_out=True, print_port=self.app.print)

        fit_plot(
            x,
            y,
            ax=pf.ax,
            print_port=self.app.print,
            alpha=self.alpha.get(),
            ellipse=ellipse,  # self.ellipse.get(),
            red_ellipse=red_ellipse,  # eelf.red_ellipse.get(),
            xlabel=xlabel,  # self.xlabel if self.xlabel != "" or self.xlabel is None else self.xvar.get(),
            ylabel=ylabel,  # self.ylabel if self.ylabel != "" or self.ylabel is None else self.yvar.get(),
            x_min=self.x_min,
            y_min=self.y_min,
            x_max=self.x_max,
            y_max=self.y_max,
            ax_margin=self.ax_margin,
            show_legend=self.show_legend,
            grid=self.grid,
            scatter=self.scatter.get(),
            print_out=print_out)
        return


class OrthoFitDialog(LinearFitDialog):
    def update_vars(self):
        self.linear = tk.BooleanVar(value=False)
        self.ortho = tk.BooleanVar(value=True)
        return


class ResidDialog(Dialogs):
    def createWidgets(self, m):
        """Create a set of grp-agg-func options together"""
        w = tk.Label(
            m, text="Residual plots are only available for linear fits.")
        w.pack(side=TOP, fill=BOTH, padx=2)
        f = tk.LabelFrame(m, text='X Y Values')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="X")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        w = tk.Label(f, text="Y")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        return

    def apply(self):

        x, y = number_2lists(self.df[self.xvar.get()],
                             self.df[self.yvar.get()],
                             col_name1=self.xvar.get(), col_name2=self.yvar.get(),
                             print_out=True, print_port=self.app.print)
        pf = self.app.showPlotViewer()
        axs = [[pf.fig.add_subplot(221), pf.fig.add_subplot(222)],
               [pf.fig.add_subplot(223), pf.fig.add_subplot(224)]]
        pf.fig.set_tight_layout(True)
        linear_fit_resid_test(x, y, print_port=self.app.print,
                              axs=axs, print_out=True)
        return


class MCorDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Variables')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(f, text="Will only include rows " +
                     "with valid numbers " +
                     "in all selected columns.",
                     anchor="e", justify=LEFT, wraplength=100)
        w.pack(side=LEFT, fill=X, padx=10)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='columns')
        w.pack(side=LEFT, fill=X, padx=10)

        self.ax_margin = tk.DoubleVar(value=0.1)
        self.red_ellipse = tk.BooleanVar(value=False)
        master = tk.LabelFrame(m, text='Plot Setting')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Margin (0.1=10%% of data range)")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.ax_margin,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='Ellipse Outline',
                           variable=self.red_ellipse)
        w.pack(side=LEFT, padx=2, pady=2)
        self.add_alpha(m)
        return

    def ok(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.quit()
        self.apply()
        return

    def apply(self):

        data = number_2Dlist(df=self.df, cols=self.grpcols,
                             print_out=True, print_port=self.app.print)
        #  axs = []
        #  n = len(data)
        try:
            ax_margin = self.ax_margin.get()
            alpha = self.alpha.get()
        except BaseException:
            ax_margin = 0.1
            alpha = 0.05

        pf = self.app.showPlotViewer(figsize=(7, 7))
        #  for y in range(n - 1):
        #      r = []
        #      for x in range(1, n):
        #          r.append(
        #              pf.fig.add_subplot(n - 1, n - 1, y * (n - 1) + x)
        #          )
        #      axs.append(r)
        # Adjust the spacing between subplots using the Figure object
        #  pf.fig.subplots_adjust(hspace=0)
        master_ax = pf.fig.add_subplot(1, 1, 1)

        multi_fit(
            data,
            self.grpcols,
            print_out=True,
            print_port=self.app.print,
            ax=master_ax,
            fig=pf.fig,
            alpha=alpha,
            ax_margin=ax_margin,
            red_ellipse=self.red_ellipse.get())
        return
