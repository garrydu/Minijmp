import tkinter as tk
from tkinter import TOP, BOTH, LEFT, X, ttk
###################################
#  from pandastable_local.dialogs import addListBox
########### Own Modules ###########
from dialog import Dialogs,addListBox
from utilities import number_list, get_number, event_count
from t_test import t_test_1sample, z_test_1sample, t_test_2samples, paired_t_test
from chi_sq import var_1sample, multi_pop_var_test
from proportion_test import prop_test_1sample, prop_2sample


class Mean1SampleDialog(Dialogs):
    def createWidgets(self, m):
        """Create a set of grp-agg-func options together"""
        #  w = tk.Label(
        #      m, anchor="e", justify=LEFT, wraplength=300,
        #      text="Calculated probability of the population where the samples came " +
        #      "from has its mean equal to the hypothesized mean. When hypothesized " +
        #      "standard deviation given, Z-test will be performed, otherwise, " +
        #      "t-test will be performed.")
        #  w.pack(side=TOP, fill=BOTH, padx=2)
        f = tk.LabelFrame(m, text='Sample Values')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        master = tk.LabelFrame(m, text='Summarized Data (Overriding)')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.sample_mean = tk.StringVar(value="")
        self.sample_std = tk.StringVar(value="")
        self.sample_n = tk.StringVar(value="")
        w = tk.Label(master, text="N")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_n,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Stdev")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_std,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Mean")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_mean,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Hypothesis Test')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.u0 = tk.StringVar(value="")
        w = tk.Label(master, text="Mean")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.u0,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        self.add_alpha(m)
        return

    def apply(self):
        if len(self.xvar.get()) > 0:
            x = number_list(self.df[self.xvar.get()],
                            col_name=self.xvar.get(),
                            print_out=True, print_port=self.app.print)
        else:
            x = None

        mean = get_number(self.sample_mean)
        std = get_number(self.sample_std)
        n = get_number(self.sample_n)
        u0 = get_number(self.u0)
        alpha = get_number(self.alpha)

        if mean is None or std is None or n is None:
            if x is None:
                return
            mean = std = n = None
        else:
            x = []
        if u0 is None:
            return
        t_test_1sample(x, u0, print_out=True,
                       sample_mean=mean, sample_n=n,
                       sample_std=std, alpha=alpha,
                       print_port=self.app.print)
        return


class Mean1SampleZDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Sample Values')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        master = tk.LabelFrame(m, text='Summarized Data (Overriding)')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.sample_mean = tk.StringVar(value="")
        self.sample_n = tk.StringVar(value="")
        w = tk.Label(master, text="N")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_n,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Mean")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_mean,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Hypothesis Test')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.u0 = tk.StringVar(value="")
        self.s0 = tk.StringVar(value="")
        w = tk.Label(master, text="Mean")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.u0,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        master = tk.LabelFrame(m, text='Known Value')
        master.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(master, text="Stdev")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.s0,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_alpha(m)
        return

    def apply(self):
        if len(self.xvar.get()) > 0:
            x = number_list(self.df[self.xvar.get()],
                            col_name=self.xvar.get(),
                            print_out=True, print_port=self.app.print)
        else:
            x = None

        mean = get_number(self.sample_mean)
        n = get_number(self.sample_n)
        u0 = get_number(self.u0)
        s0 = get_number(self.s0)

        if mean is None or n is None:
            if x is None:
                return
            mean = n = None
        else:
            x = []
        if u0 is None or s0 is None:
            return
        alpha = get_number(self.alpha)
        z_test_1sample(x, u0, s0, print_out=True,
                       sample_mean=mean, sample_n=n,
                       alpha=alpha,
                       print_port=self.app.print)
        return


class Var1SampleDialog(Dialogs):
    def createWidgets(self, m):
        """Create a set of grp-agg-func options together"""
        f = tk.LabelFrame(m, text='Sample Values')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        master = tk.LabelFrame(m, text='Summarized Data (Overriding)')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.sample_n = tk.StringVar(value="")
        self.sample_std = tk.StringVar(value="")
        w = tk.Label(master, text="N")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_n,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Stdev")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.sample_std,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Hypothesis Test')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.s0 = tk.StringVar(value="")
        w = tk.Label(master, text="Stdev")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.s0,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        self.add_alpha(m)
        return

    def apply(self):
        if len(self.xvar.get()) > 0:
            x = number_list(self.df[self.xvar.get()],
                            col_name=self.xvar.get(),
                            print_out=True, print_port=self.app.print)
        else:
            x = None

        std = get_number(self.sample_std)
        n = get_number(self.sample_n)
        s0 = get_number(self.s0)
        alpha = get_number(self.alpha)

        if std is None or n is None:
            if x is None:
                return
            std = n = None
        else:
            x = []
        if s0 is None:
            return
        var_1sample(data=x, s0=s0, print_out=True,
                    sample_n=n, sample_std=std, alpha=alpha,
                    print_port=self.app.print)
        return


class Mean2SampleDialog(Dialogs):
    def createWidgets(self, m):
        """Create a set of grp-agg-func options together"""
        master = tk.LabelFrame(m, text='Sample Values')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(master, text="Sample 1")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            master, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        w = tk.Label(master, text="Sample 2")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            master, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        f = tk.LabelFrame(m, text='Summarized Data (Overriding)')
        f.pack(side=TOP, fill=BOTH, padx=2)
        master = tk.LabelFrame(f, text='Sample 1')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.u1 = tk.StringVar(value="")
        self.s1 = tk.StringVar(value="")
        self.n1 = tk.StringVar(value="")
        w = tk.Label(master, text="N")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.n1,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Stdev")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.s1,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Mean (u1)")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.u1,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        master = tk.LabelFrame(f, text='Sample 2')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.u2 = tk.StringVar(value="")
        self.s2 = tk.StringVar(value="")
        self.n2 = tk.StringVar(value="")
        w = tk.Label(master, text="N")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.n2,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Stdev")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.s2,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Mean (u2)")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.u2,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Hypothesis Test')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.d0 = tk.StringVar(value="0")
        w = tk.Label(master, text="u2 - u1 = ")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.d0,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        self.pooled = tk.BooleanVar(value=False)
        w = tk.Checkbutton(master, text=' Assume Equal Variances',
                           variable=self.pooled)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_alpha(m)
        return

    def apply(self):
        if len(self.xvar.get()) > 0:
            x = number_list(self.df[self.xvar.get()],
                            col_name=self.xvar.get(),
                            print_out=True, print_port=self.app.print)
        else:
            x = None

        if len(self.yvar.get()) > 0:
            y = number_list(self.df[self.yvar.get()],
                            col_name=self.yvar.get(),
                            print_out=True, print_port=self.app.print)
        else:
            y = None

        u1 = get_number(self.u1)
        s1 = get_number(self.s1)
        n1 = get_number(self.n1)
        u2 = get_number(self.u2)
        s2 = get_number(self.s2)
        n2 = get_number(self.n2)

        alpha = get_number(self.alpha)
        pooled = self.pooled.get()

        t_test_2samples(l1=x, l2=y, print_out=True,
                        u1=u1, u2=u2, s1=s1, s2=s2,
                        n1=n1, n2=n2,
                        alpha=alpha, pooled=pooled,
                        print_port=self.app.print)
        return


class PairedTDialog(Dialogs):
    def createWidgets(self, m):
        master = tk.LabelFrame(m, text='Sample Values')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        self.yvar = tk.StringVar(value="")
        w = tk.Label(master, text="Sample 1")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            master, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        w = tk.Label(master, text="Sample 2")
        w.pack(side=LEFT, fill=X, padx=2)
        w = ttk.Combobox(
            master, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2)

        master = tk.LabelFrame(
            m, text='Hypothesized population mean of the differences')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.d0 = tk.StringVar(value="0")
        w = tk.Label(master, text="Sample 1 - Sample 2")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.d0,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_alpha(m)
        return

    def apply(self):
        if len(self.xvar.get()) > 0:
            x = number_list(self.df[self.xvar.get()],
                            col_name=self.xvar.get(),
                            print_out=True, print_port=self.app.print)
        else:
            x = None

        if len(self.yvar.get()) > 0:
            y = number_list(self.df[self.yvar.get()],
                            col_name=self.yvar.get(),
                            print_out=True, print_port=self.app.print)
        else:
            y = None

        alpha = get_number(self.alpha)
        u0 = get_number(self.d0)

        paired_t_test(l1=x, l2=y, print_out=True,
                      alpha=alpha, u0=u0,
                      print_port=self.app.print)
        return


class MultiVarDialog(Dialogs):
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

        multi_pop_var_test(data, self.grpcols, print_out=True,
                           print_port=self.app.print,
                           alpha=alpha)
        return


class Prop1SDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Sample Values')
        f.pack(side=TOP, fill=BOTH, padx=2)
        w = tk.Label(f, text="Sample")
        w.pack(side=LEFT, fill=X, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        w = tk.Label(f, text="Name of Event")
        w.pack(side=LEFT, fill=X, padx=2)
        self.event_name = tk.StringVar(value="")
        w = tk.Entry(f, textvariable=self.event_name,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Summarized Data (Overriding)')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.ttl_cnt = tk.StringVar(value="")
        self.event_cnt = tk.StringVar(value="")
        w = tk.Label(master, text="Number of events")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.event_cnt,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Number of trials")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.ttl_cnt,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Hypothesis Test')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.p0 = tk.DoubleVar(value=0.5)
        w = tk.Label(master, text="Hypothesized proportion")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.p0,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        self.add_alpha(m)
        return

    def apply(self):
        if len(self.xvar.get()) > 0:
            x = list(self.df[self.xvar.get()])
        else:
            x = None

        p0 = get_number(self.p0)
        event_cnt = get_number(self.event_cnt)
        ttl_cnt = get_number(self.ttl_cnt)
        event_name = self.event_name.get()
        alpha = get_number(self.alpha)

        if event_cnt is None or ttl_cnt is None:
            if x is None:
                return
            ttl_cnt, event_cnt = event_count(x, event_name)

        if p0 is None:
            return

        prop_test_1sample(N=int(ttl_cnt), events=int(event_cnt),
                          p0=p0, alpha=alpha, print_out=True,
                          print_port=self.app.print)
        return


class Prop2SDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='Sample 1')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.xvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.xvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.event_name = tk.StringVar(value="")
        w = tk.Entry(f, textvariable=self.event_name,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)

        f = tk.LabelFrame(m, text='Sample 2')
        f.pack(side=TOP, fill=BOTH, padx=2)
        self.yvar = tk.StringVar(value="")
        w = ttk.Combobox(
            f, values=self.cols, textvariable=self.yvar,
            width=14)
        w.pack(side=LEFT, padx=2)
        self.event_name2 = tk.StringVar(value="")
        w = tk.Entry(f, textvariable=self.event_name2,
                     bg='white', width=15)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Summarized Sample 1 (Overriding)')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.ttl_cnt = tk.StringVar(value="")
        self.event_cnt = tk.StringVar(value="")
        w = tk.Label(master, text="Number of events")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.event_cnt,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Number of trials")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.ttl_cnt,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        master = tk.LabelFrame(m, text='Summarized Sample 2 (Overriding)')
        master.pack(side=TOP, fill=BOTH, padx=2)
        self.ttl_cnt2 = tk.StringVar(value="")
        self.event_cnt2 = tk.StringVar(value="")
        w = tk.Label(master, text="Number of events")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.event_cnt2,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)
        w = tk.Label(master, text="Number of trials")
        w.pack(side=LEFT, fill=X, padx=2)
        w = tk.Entry(master, textvariable=self.ttl_cnt2,
                     bg='white', width=5)
        w.pack(side=LEFT, padx=2, pady=2)

        self.add_alpha(m)
        return

    def apply(self):
        if len(self.xvar.get()) > 0:
            x = list(self.df[self.xvar.get()])
        else:
            x = None
        if len(self.xvar.get()) > 0:
            y = list(self.df[self.yvar.get()])
        else:
            y = None
        event_cnt = get_number(self.event_cnt)
        ttl_cnt = get_number(self.ttl_cnt)
        event_cnt2 = get_number(self.event_cnt2)
        ttl_cnt2 = get_number(self.ttl_cnt2)
        event_name = self.event_name.get()
        event_name2 = self.event_name2.get()
        alpha = get_number(self.alpha)

        if event_cnt is None or ttl_cnt is None:
            if x is None:
                return
            ttl_cnt, event_cnt = event_count(x, event_name)

        if event_cnt2 is None or ttl_cnt2 is None:
            if y is None:
                return
            ttl_cnt2, event_cnt2 = event_count(y, event_name2)

        prop_2sample(n1=int(ttl_cnt), e1=int(event_cnt),
                     n2=int(ttl_cnt2), e2=int(event_cnt2),
                     alpha=alpha, print_out=True,
                     print_port=self.app.print)
        return
