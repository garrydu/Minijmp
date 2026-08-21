from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, X, BOTH
from prettytable import PrettyTable as PT
###################################
from pandastable_local.dialogs import MultipleValDialog
########### Own Modules ###########
from dialog import Dialogs, addListBox
from utilities import count_2factors, number_2Dlist, transpose_2D_list, filter_voids, count_1factor, number_list
from chi_sq import chi_square


class Chi2TableDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='原始数据（分类值）')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="行")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(f, text="列")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='以二维表汇总（覆盖输入）')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w, self.grpvar = addListBox(
            f, values=self.cols, width=20, label='列')
        w.pack(side=LEFT, fill=X, padx=10)
        self.rvar = tk.StringVar(value="")
        w = tk.Label(f, text="行标签（可选列）")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.rvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        return

    def ok(self):
        self.grpcols = self.grpvar.getSelectedItem()
        self.quit()
        self.apply()
        return

    def apply(self):

        if len(self.grpcols) > 0:
            data = number_2Dlist(df=self.df, cols=self.grpcols,
                                 print_out=True, print_port=self.app.print)
            cKeys = self.grpcols
            data = transpose_2D_list(data)
            if len(self.rvar.get()) > 0:
                [rKeys] = filter_voids([list(self.df[self.rvar.get()])])
            else:
                rKeys = [chr(65 + i) for i in range(len(data[0]))]
        else:
            data, rKeys, cKeys = count_2factors(
                self.df[self.xvar.get()],
                self.df[self.yvar.get()])

        chi_square(data, print_out=True,
                   print_port=self.app.print,
                   print_table=True,
                   cKeys=cKeys, rKeys=rKeys)
        return


class Chi2PropDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='原始数据（分类值）')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.xvar = tk.StringVar(value="")
        w = tk.Label(f, text="样本")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='汇总计数（覆盖输入）')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.rvar = tk.StringVar(value="")
        w = tk.Label(f, text="水平")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.rvar,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)
        self.cnt = tk.StringVar(value="")
        w = tk.Label(f, text="计数")
        w.pack(side=LEFT, fill=X, padx=2, pady=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.cnt,
            width=14)
        w.pack(side=LEFT, padx=2, pady=2)

        return

    def apply(self):

        rvar = self.rvar.get()
        cnt = self.cnt.get()
        if len(rvar) > 0 and len(cnt) > 0:
            [rKeys, cnts] = filter_voids([list(self.df[rvar]),
                                          list(self.df[cnt])])
            cnts = number_list(cnts)
        else:
            cnts, rKeys = count_1factor(
                self.df[self.xvar.get()])

        d = MultipleValDialog(title="假设概率（需合计为1）",
                              labels=rKeys,
                              initialvalues=[0] * len(rKeys),
                              types=["float"] * len(rKeys),
                              parent=self.parent)
        if d.result is None:
            return
        #  print(d.results)
        res = number_list(d.results)
        #  print(res, sum(res), cnts)
        if len(res) != len(cnts):
            self.error("Invalid inputs.")
            return
        if any(_ <= 0 for _ in res):
            self.error("The hypothesized probabilities need be greater than zero and less than one.")
            return
        if sum(res) != 1:
            self.error("The hypothesized probabilities did not sum to 1. The probabilities were rescaled.")
            res = [x / sum(res) for x in res]

        ratio = sum(cnts) * 1e9
        pseudo_data = [_ * ratio for _ in res]

        t = PT()
        t.field_names = ["Level", "Est Prob", "Hypoth Prob"]
        for i in range(len(cnts)):
            t.add_row([rKeys[i], "%.3f" % (cnts[i] / sum(cnts)),
                       "%.3f" % res[i]])
        self.app.print("\n---- Test Probabilities ----\n" + str(t))

        chi_square([cnts, pseudo_data], print_out=True,
                   print_port=self.app.print,
                   print_table=False)
        return
