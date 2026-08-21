from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, BOTH, X, W
from scipy.stats import probplot
from prettytable import PrettyTable as PT
########### Own Modules ###########
from dialog import Dialogs, addListBox
from describe import describe
from utilities import norm_test, number_list, mean_std_CIs
from dist_fit import compare_dist


class FitDistDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='数据列选择')
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
        self.dists_zh = {
            "Normal": "正态分布",
            "Student's t": "t 分布",
            "Gamma": "伽马分布",
            "Lognormal": "对数正态分布",
            "Exponential": "指数分布",
            "Weibull": "威布尔分布",
        }
        self.picks = dict()

        notes = ["", "",
                 ": 输入值 > 0",
                 ": 输入值 > 0",
                 ": 输入值 ≥ 0",
                 ": 输入值 > 0"]

        f = tk.LabelFrame(m, text='分布模型')
        f.pack(side=TOP, fill=BOTH, padx=2)
        for i, name in enumerate(self.dists):
            self.picks[name] = tk.BooleanVar(value=False)
            w = tk.Checkbutton(f, text=self.dists_zh.get(name, name) + " " + notes[i],
                               variable=self.picks[name])
            w.pack(side=TOP, anchor=W)
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
        f = tk.LabelFrame(m, text='数据')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='列')
        w.pack(side=LEFT, fill=X, padx=10)

        self.picks = dict()
        self.names = ["N", "Mean", "Standard Deviation", "Variance",
                      "Minimum",
                      "First Quartile", "Median", "Third Quartile", "Maximum",
                      "SE of Mean", "Coefficient of Variation", "Sum",
                      "Range", "Interquartile Range",
                      "Skewness", "Kurtosis", "Mode", "N of Mode"]
        self.name_zh = {
            "N": "样本量 N",
            "Mean": "均值",
            "Standard Deviation": "标准差",
            "Variance": "方差",
            "Minimum": "最小值",
            "First Quartile": "第一四分位数 (Q1)",
            "Median": "中位数",
            "Third Quartile": "第三四分位数 (Q3)",
            "Maximum": "最大值",
            "SE of Mean": "均值标准误",
            "Coefficient of Variation": "变异系数 (CV)",
            "Sum": "总和",
            "Range": "极差",
            "Interquartile Range": "四分位距 (IQR)",
            "Skewness": "偏度",
            "Kurtosis": "峰度",
            "Mode": "众数",
            "N of Mode": "众数频数",
        }

        f = tk.LabelFrame(m, text='统计量')
        f.pack(side=TOP, fill=BOTH, padx=2)
        for i, name in enumerate(self.names):
            self.picks[name] = tk.BooleanVar(value=True)
            if i % 6 == 0:
                master = ttk.Frame(f)
                master.pack(side=LEFT, padx=2)
            slave = ttk.Frame(master)
            slave.pack(side=TOP, fill=BOTH, padx=2, pady=2)
            w = tk.Checkbutton(slave, text=self.name_zh.get(name, name),
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
        self.app.print("\n---- 统计量 ----")
        t = PT()
        t.field_names = [""] + self.grpcols
        for name in self.names:
            if self.picks[name].get():
                row = [self.name_zh.get(name, name)]
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

        f = tk.LabelFrame(m, text='统计汇总')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.pct = tk.StringVar(
            value="100, 99.5, 97.5, 90, 75, 50,25, 10, 2.5, 0.5, 0")
        f = tk.LabelFrame(m, text='百分位数')
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
        f = tk.LabelFrame(m, text='数据列选择')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        f = tk.LabelFrame(m, text='图表')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.qq = tk.BooleanVar(value=False)
        w = tk.Checkbutton(f, text='显示QQ图',
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
            pf.ax.set_xlabel('理论分位数')
            pf.ax.set_ylabel('观测值')
        return


class CIDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='数据列选择')
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
