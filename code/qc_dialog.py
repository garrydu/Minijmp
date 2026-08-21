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
        ff = tk.LabelFrame(m, text='输入列')
        ff.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        f = tk.Frame(ff)
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="测量值")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(f, text="零件编号")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.Frame(ff)
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.ovar = tk.StringVar(value="")
        w = tk.Label(f, text="操作员")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.ovar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='可选输入')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.hist_std = tk.StringVar(value="")
        w = tk.Label(f, text="历史过程(总体)标准差")
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
            self.error(msg="输入错误或输入项过少。")
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
            self.error(msg="输入错误：数据点过少。")
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
        f = tk.LabelFrame(m, text='输入列')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="测量值")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(f, text="零件编号")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='可选输入')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.ovar = tk.StringVar(value="")
        w = tk.Label(f, text="操作员")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.ovar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='算法设置')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.mvar = tk.StringVar(value="AIAG (ANOVA)")
        w = tk.Label(f, text="方法")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f,
            values=[
                "AIAG (ANOVA)",
                "EMP (ANOVA)",
                "XBAR/R"],
            textvariable=self.mvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        self.inter = tk.StringVar(value="自动")
        w = tk.Label(f, text='操作员×零件交互')
        w.pack(side=LEFT, padx=2, pady=2)
        w = ttk.Combobox(
            f,
            values=["自动", "开", "关"],
            textvariable=self.inter,
            width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='AIAG 与 Xbar/R 设置（可选）')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        slave = tk.Frame(f)
        slave.pack(side=TOP, fill=BOTH, padx=0, pady=2)

        self.spec_gap = tk.StringVar(value="")
        w = tk.Label(slave, text="USL - LSL")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = tk.Entry(slave, textvariable=self.spec_gap,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)

        self.hist_std = tk.StringVar(value="")
        w = tk.Label(slave, text="历史标准差")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = tk.Entry(slave, textvariable=self.hist_std,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)

        #  s1 = "Use historical standard deviation to estimate process variation."
        #  s2 = "Use parts in the study to estimate process variation."
        #  self.hist_std_use = tk.StringVar(value=s1)
        #  w = ttk.Combobox(
        #      f,
        #      values=[s1, s2],
        #      textvariable=self.hist_std_use,
        #      width=50)
        #  w.pack(side=LEFT, padx=10, pady=2)

        self.ylabel = tk.StringVar(value="")
        master = tk.LabelFrame(m, text='图表设置')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Y轴标签")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.ylabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_alpha(m)
        return

    def apply(self):
        alpha = self.alpha.get()
        if alpha > 0.5 or alpha <= 0:
            alpha = 0.05
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

        hist_std = get_number(self.hist_std)
        if hist_std is not None:
            hist_std = hist_std if hist_std >= 0 else None
        spec_gap = get_number(self.spec_gap)
        if spec_gap is not None:
            spec_gap = spec_gap if spec_gap >= 0 else None
        #  use_hist = ("hist" in self.hist_std_use.get())

        grr_master(
            y=r[0], part=r[1],
            op=r[2] if has_op else None,
            mode=self.mvar.get(),
            inter=self.inter.get(),
            hist_std=hist_std,
            spec_gap=spec_gap,
            #  use_hist=use_hist,
            print_out=True,
            alpha=alpha,
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
        f = tk.LabelFrame(m, text='输入列')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = tk.Label(f, text="测量值")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='输入规格限')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.target = tk.DoubleVar(value=0)
        self.lsl = tk.DoubleVar(value=0)
        self.usl = tk.DoubleVar(value=0)
        w = tk.Label(master, text="LSL")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.lsl,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="目标值")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.target,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="USL")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.usl,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)

        self.show_within = tk.BooleanVar(value=False)
        w = tk.Checkbutton(
            m,
            text='显示相邻观测移动平均的组内标准差',
            variable=self.show_within)
        w.pack(side=TOP, fill=BOTH, padx=2, pady=2)

        self.xlabel = tk.StringVar(value="")
        self.show_legend = tk.BooleanVar(value=True)
        self.show_spec = tk.BooleanVar(value=True)
        master = tk.LabelFrame(m, text='图表设置')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="X轴标签")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.xlabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='显示规格限',
                           variable=self.show_spec)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='显示图例',
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
        elif tgt == 0 and lsl < usl:
            self.error("缺少目标规格值，改用 LSL 与 USL 的平均值。")
            tgt = (lsl + usl) / 2
        else:
            self.error("规格限输入错误。")
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
        f = tk.LabelFrame(m, text='输入列')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = tk.Label(f, text="测量值")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='输入规格限')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.target = tk.DoubleVar(value=0)
        self.lsl = tk.DoubleVar(value=0)
        self.usl = tk.DoubleVar(value=0)
        w = tk.Label(master, text="LSL")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.lsl,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="目标值")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.target,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="USL")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.usl,
                     bg='white', width=10)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='子组')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.mvar = tk.StringVar(value="使用子组大小")
        w = tk.Label(f, text="选项")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f,
            values=[
                #  "No Subgroups",
                "使用子组ID列",
                "使用子组大小"],
            textvariable=self.mvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.subid = tk.StringVar(value="")
        w = tk.Label(f, text="ID列")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.subid,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.subsize = tk.DoubleVar(value=2)
        w = tk.Label(f, text="子组大小")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(f, textvariable=self.subsize,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='子组内变异')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.subm = tk.StringVar(value="无偏标准差")
        w = tk.Label(f, text="平均值基于")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f,
            values=[
                "无偏标准差",
                "极差"],
            textvariable=self.subm,
            width=14)
        w.pack(side=LEFT, padx=2)

        self.xlabel = tk.StringVar(value="")
        self.show_legend = tk.BooleanVar(value=True)
        self.show_spec = tk.BooleanVar(value=True)
        self.show_within = tk.BooleanVar(value=True)
        master = tk.LabelFrame(m, text='图表设置')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="X轴标签")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.xlabel,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='显示规格限',
                           variable=self.show_spec)
        w.pack(side=LEFT, padx=2, pady=2)
        #  w = tk.Checkbutton(master, text='Show Within',
        #                     variable=self.show_within)
        #  w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Checkbutton(master, text='显示图例',
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
                "已接收 %d 组有效的（子组ID, 测量值）数据。" %
                len(y_r))
            data = grouping_by_labels(y_r, id_r)
        elif "大小" in m or "ize" in m:
            y = number_list(self.df[self.xvar.get()])
            size = int(self.subsize.get())
            if size < 2:
                self.error("子组大小输入错误。")
                return
            data = [y[i:i + size] for i in range(0, len(y), size)]
            if len(y) % size > 0:
                self.app.print("警告：子组分组成员数不平衡。")
        else:
            data = number_list(self.df[self.xvar.get()])

        alpha = self.alpha.get()
        if alpha > 0.5 or alpha <= 0:
            alpha = 0.05

        use_range = ("极差" in self.subm.get()) or ("ange" in self.subm.get())

        lsl, tgt, usl = self.lsl.get(), self.target.get(), self.usl.get()
        if lsl < tgt < usl:
            pass
        else:
            self.error("规格限输入错误。")
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
        f = tk.LabelFrame(m, text='样本值')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        master = tk.LabelFrame(m, text='汇总数据（覆盖输入）')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.sample_mean = tk.StringVar(value="")
        self.sample_std = tk.StringVar(value="")
        self.sample_n = tk.StringVar(value="")
        w = tk.Label(master, text="样本量 N")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_n,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="标准差 SD")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_std,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="均值")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_mean,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        #  w = tk.Label(
        #      m,
        #      anchor="e",
        #      justify=LEFT,
        #      wraplength=300,
        #      text="Computes an interval that contains at least the specified" +
        #      " proportion of the population with (1-alpha) confidence, assuming" +
        #      " Normal Distribution.")
        #  w.pack(side=TOP, fill=BOTH, padx=2)

        master = tk.LabelFrame(m, text='比例设置')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.prop = tk.DoubleVar(value=0.9)
        w = tk.Label(master, text="指定覆盖比例")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.prop,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_alpha(m)
        return

    def apply(self):
        try:
            data = number_list(self.df[self.xvar.get()])
        except BaseException:
            data = None

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
