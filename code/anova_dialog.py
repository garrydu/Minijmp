from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, X, BOTH
from numpy import nan
###################################
#  from pandastable_local.dialogs import addListBox
########### Own Modules ###########
from dialog import Dialogs,addListBox
from utilities import number_list
from one_way_ANOVA import one_way_anova, JMP_ANOVA_t_test
from two_way_anova import two_way_anova


class Anova2WayDialog(Dialogs):
    def createWidgets(self, m):

        f = tk.LabelFrame(m, text='Factors')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(f, text="A")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        w = tk.Label(f, text="B")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        f = tk.LabelFrame(m, text='Response')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.zvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.zvar,
            width=14)
        w.pack(side=LEFT, padx=2)

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


class Anova1WayDialog(Dialogs):
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
