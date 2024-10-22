from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, BOTH, X
from scipy.stats import probplot
from prettytable import PrettyTable as PT
########### Own Modules ###########
from dialog import Dialogs, addListBox
from describe import describe
from utilities import norm_test, number_list, mean_std_CIs
from dist_fit import compare_dist


class FitDistDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Data')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.dists = [
            "Normal",
            "Student's t",
            "Gamma",
            "Lognormal",
            "Exponential",
            "Weibull"]
        self.picks = dict()

        f = tk.LabelFrame(m, text='Models')
        f.pack(side=TOP, fill=BOTH, padx=2)
        for i, name in enumerate(self.dists):
            self.picks[name] = tk.BooleanVar(value=False)
            w = tk.Checkbutton(f, text=name,
                               variable=self.picks[name])
            w.pack(side=LEFT)
        return

    def apply(self):
        col = self.xvar.get()
        data = number_list(
            self.df[col],
            col_name=col,
            print_out=True,
            print_port=self.app.print)
        selected = []
        for key in self.dists:
            if self.picks[key].get():
                selected.append(key)
        compare_dist(data, print_out=True, print_port=self.app.print,
                     selected=selected)
        return


class MultiDescribeDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Data')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='columns')
        w.pack(side=LEFT, fill=X, padx=10)

        self.picks = dict()
        self.names = ["N", "Mean", "Standard Deviation", "Variance",
                      "Minimum",
                      "First Quartile", "Median", "Third Quartile", "Maximum",
                      "SE of Mean", "Coefficient of Variation", "Sum",
                      "Range", "Interquartile Range",
                      "Skewness", "Kurtosis", "Mode", "N of Mode"]

        f = tk.LabelFrame(m, text='Statistics')
        f.pack(side=TOP, fill=BOTH, padx=2)
        for i, name in enumerate(self.names):
            self.picks[name] = tk.BooleanVar(value=True)
            if i % 6 == 0:
                master = ttk.Frame(f)
                master.pack(side=LEFT, padx=2)
            slave = ttk.Frame(master)
            slave.pack(side=TOP, fill=BOTH, padx=2, pady=2)
            w = tk.Checkbutton(slave, text=name,
                               variable=self.picks[name])
            w.pack(side=LEFT)
        return

    def ok(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.quit()
        self.apply()
        return

    def apply(self):
        res = dict()
        for col in self.grpcols:
            res[col] = describe(
                number_list(
                    self.df[col],
                    col_name=col,
                    print_out=True,
                    print_port=self.app.print),
                print_out=False)
        self.app.print("\n---- Statitstics ----")
        t = PT()
        t.field_names = [""] + self.grpcols
        for name in self.names:
            if self.picks[name].get():
                row = [name]
                for col in self.grpcols:
                    if "N" in name:
                        row.append("%d" % res[col][name])
                    else:
                        row.append("%.3f" % res[col][name])
                t.add_row(row)
        self.app.print(str(t))
        return


class DescribeDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Stats Summary')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.pct = tk.StringVar(
            value="100, 99.5, 97.5, 90, 75, 50,25, 10, 2.5, 0.5, 0")
        f = tk.LabelFrame(m, text='Percentiles for Quantiles')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Entry(f, textvariable=self.pct,
                     bg='white', width=35)
        w.pack(side=LEFT, padx=2)
        return

    def apply(self):

        x = number_list(self.df[self.xvar.get()],
                        col_name=self.xvar.get(),
                        print_out=True, print_port=self.app.print)
        print(x)
        pct = self.pct.get()
        try:
            pct = [float(i) for i in pct.split(",") if 0 <= float(i) <= 100]
        except BaseException:
            pct = [100, 99.5, 97.5, 90, 75, 50, 25, 10, 2.5, 0.5, 0]
        describe(x, print_out=True, print_port=self.app.print,
                 percentiles=pct)
        return


class NormTestDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Normality Test')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        f = tk.LabelFrame(m, text='Plot')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.qq = tk.BooleanVar(value=False)
        w = tk.Checkbutton(f, text='Show QQ Plot',
                           variable=self.qq)
        w.pack(side=LEFT, padx=2, pady=2)
        return

    def apply(self):
        x = number_list(self.df[self.xvar.get()],
                        col_name=self.xvar.get(),
                        print_out=True, print_port=self.app.print)
        qq = self.qq.get()

        norm_test(x, print_out=True, print_port=self.app.print)
        if qq:
            pf = self.app.showPlotViewer()
            pf.ax = pf.fig.add_subplot(111)
            #  fit_plot(x, y, ax=pf.ax, print_port=self.app.print,
            probplot(x, dist="norm", plot=pf.ax)
            pf.ax.set_xlabel('Theoretical quantiles')
            pf.ax.set_ylabel('Observed Values')
        return


class CIDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Mean & Std CI')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.add_alpha(m)
        return

    def apply(self):
        x = number_list(self.df[self.xvar.get()],
                        col_name=self.xvar.get(),
                        print_out=True, print_port=self.app.print)
        alpha = self.alpha.get()
        mean_std_CIs(x, alpha=alpha, print_out=True, print_port=self.app.print)
        return
