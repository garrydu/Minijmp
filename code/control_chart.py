import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
####### Own modules ##########
try: 
    from .ctrl_chart_const import d2 as cc_d2, d3 as cc_d3
    from .utilities import add_Y_refs, gen_table, c4_values
except ImportError:
    from ctrl_chart_const import d2 as cc_d2, d3 as cc_d3
    from utilities import add_Y_refs, gen_table, c4_values

NAN = float('nan')


def _finite(values):
    return [v for v in values if v == v]  # v == v is False only for NaN


def x_mR(x, mr, k=3, sigma=None, mean=None):  # , print_out=True, xLabels=None,max_xlabels=25):

    # Define list variable for moving ranges
    MR = [np.nan] * (mr - 1)
    for i in range(mr - 1, len(x)):
        l = x[i - mr + 1:i + 1]
        MR.append(max(l) - min(l))

    x_bar = stat.mean(x) if mean is None else mean
    #  xbar_bar = stat.mean([j for l in data for j in l]) if mean is None else mean
    R_bar = stat.mean(MR[(mr - 1):])
    if sigma is None:
        sigma = R_bar / cc_d2(mr)
    x_UCL = x_bar + k * sigma
    x_LCL = x_bar - k * sigma

    R_UCL = cc_d2(mr) * sigma + k * sigma * cc_d3(mr)
    R_LCL = max(0, cc_d2(mr) * sigma - k * sigma * cc_d3(mr))
    #  R_UCL = D4 * R_bar
    #  R_LCL = 0
    x1 = list(range(len(x)))
    #  x2 = x1  # list(range(1, len(x)))
    return {"Y1": x, "Y2": MR, "bar1": x_bar, "ucl1": x_UCL,
            "ucl2": R_UCL, "lcl1": x_LCL, "lcl2": R_LCL,
            "bar2": R_bar, "n": 2, "X": x1,  # "X2": x2,
            "ylabel1": "Individual Values",
            "ylabel2": "Moving Range (n=%d)" % mr}


# the number of samples each day need be consistent over time
# It's a sampling process not all the products each day.
# otherwise can't estimate an A2 value for UCL and LCL

def xBar_R(data,
           k=3, mean=None, sigma=None, pooled=False):  # , print_out=True, max_xlabels=25,xLabels=None):

    # Subgroups keep their position even when they hold fewer valid values.
    # As in Minitab: the X-bar point uses whatever values exist; a subgroup
    # with fewer than 2 values has no range, so its R point and R limits are
    # left blank (NaN) and it is not used to estimate sigma.
    n = [len(l) for l in data]
    xbar = [stat.mean(l) if ni > 0 else NAN for l, ni in zip(data, n)]
    R = [max(l) - min(l) if ni >= 2 else NAN for l, ni in zip(data, n)]
    ok = [i for i, ni in enumerate(n) if ni >= 2]
    #  A2 = Ctrl_Cht_Const["A2"][n]
    if sigma is None:
        if not ok:
            raise ValueError("Need at least one subgroup with 2 or more"
                             " valid values to estimate sigma.")
        if pooled:
            sp = (sum(sum((x - stat.mean(data[i]))**2 for x in data[i]) for i in ok) / sum(n[i] - 1 for i in ok))**.5
            sigma = sp / c4_values(sum(n[i] - 1 for i in ok))
        else:
            sigma = sum(cc_d2(n[i]) * R[i] / cc_d3(n[i])**2 for i in ok) / sum((cc_d2(n[i]) / cc_d3(n[i]))**2 for i in ok)

    #  R_bar = stat.mean(R)
    xbar_bar = stat.mean([j for l in data for j in l]) if mean is None else mean
    xbar_ucl = [xbar_bar + k * sigma / (_)**.5 if _ > 0 else NAN for _ in n]
    xbar_lcl = [xbar_bar - k * sigma / (_)**.5 if _ > 0 else NAN for _ in n]
    #  xbar_lcl = xbar_bar - A2 * R_bar
    #  D4 = Ctrl_Cht_Const["D4"][n]
    #  D3 = Ctrl_Cht_Const["D3"][n]
    #  R_UCL = D4 * R_bar
    #  R_LCL = D3 * R_bar
    R_bar = [cc_d2(ni) * sigma if ni >= 2 else NAN for ni in n]
    R_UCL = [cc_d2(mr) * sigma + k * sigma * cc_d3(mr) if mr >= 2 else NAN for mr in n]
    R_LCL = [max(0, cc_d2(mr) * sigma - k * sigma * cc_d3(mr)) if mr >= 2 else NAN for mr in n]

    return {"Y1": xbar, "Y2": R, "bar1": xbar_bar, "ucl1": xbar_ucl,
            "ucl2": R_UCL, "lcl1": xbar_lcl, "lcl2": R_LCL, "n": n,
            "bar2": R_bar, "ylabel1": "X Bar", "ylabel2": "Range",
            "X": list(range(len(data)))}


def xBar_S(data,  # , print_out=True, max_xlabels=25,xLabels=None):
           k=3, mean=None, sigma=None, pooled=False):  # , print_out=True, max_xlabels=25,xLabels=None):

    # Same handling as xBar_R: a subgroup with fewer than 2 values keeps its
    # X-bar point but has no S point or S limits (NaN).
    n = [len(l) for l in data]
    xbar = [stat.mean(l) if ni > 0 else NAN for l, ni in zip(data, n)]
    S = [stat.stdev(l) if ni >= 2 else NAN for l, ni in zip(data, n)]
    #  S_bar = stat.mean(S)
    ok = [i for i, ni in enumerate(n) if ni >= 2]
    #  A2 = Ctrl_Cht_Const["A2"][n]

    unbiased = True
    if sigma is None:
        if not ok:
            raise ValueError("Need at least one subgroup with 2 or more"
                             " valid values to estimate sigma.")
        if pooled:
            sp = (sum(sum((x - stat.mean(data[i]))**2 for x in data[i]) for i in ok) / sum(n[i] - 1 for i in ok))**.5
            sigma = sp / c4_values(sum(n[i] - 1 for i in ok))
        else:
            h = {i: c4_values(n[i])**2 / (1 - c4_values(n[i])**2) for i in ok}
            sigma = sum(h[i] * S[i] / c4_values(n[i]) for i in ok) / sum(h.values())
    else:
        unbiased = False

    #  xbar_bar = stat.mean(xbar) if mean is None else mean
    xbar_bar = stat.mean([j for l in data for j in l]) if mean is None else mean
    xbar_ucl = [xbar_bar + k * sigma / (_)**.5 if _ > 0 else NAN for _ in n]
    xbar_lcl = [xbar_bar - k * sigma / (_)**.5 if _ > 0 else NAN for _ in n]
    #  A3 = Ctrl_Cht_Const["A3"][n]
    #  xbar_bar = stat.mean(xbar)
    #  xbar_ucl = xbar_bar + A3 * S_bar
    #  xbar_lcl = xbar_bar - A3 * S_bar
    #  B4 = Ctrl_Cht_Const["B4"][n]
    #  B3 = Ctrl_Cht_Const["B3"][n]
    #  S_UCL = B4 * S_bar
    #  S_LCL = B3 * S_bar

    def c5(n):
        return (1 - c4_values(n)**2)**.5

    if unbiased:
        S_bar = [c4_values(ni) * sigma if ni >= 2 else NAN for ni in n]
        S_LCL = [max(0, c4_values(ni) * sigma - k * sigma * c5(ni)) if ni >= 2 else NAN for ni in n]
        S_UCL = [c4_values(ni) * sigma + k * sigma * c5(ni) if ni >= 2 else NAN for ni in n]
    else:
        S_bar = sigma
        S_LCL = [max(0, sigma * (1 - k * c5(ni) / c4_values(ni))) if ni >= 2 else NAN for ni in n]
        S_UCL = [sigma * (1 + k * c5(ni) / c4_values(ni)) if ni >= 2 else NAN for ni in n]

    return {"Y1": xbar, "Y2": S, "bar1": xbar_bar, "ucl1": xbar_ucl,
            "ucl2": S_UCL, "lcl1": xbar_lcl, "lcl2": S_LCL, "n": n,
            "bar2": S_bar, "ylabel1": "X Bar", "ylabel2": "Std Dev",
            "X": list(range(len(data)))}


def _max0(v):
    # max(0, v) that keeps NaN (a blank subgroup) blank instead of making it 0
    return v if v != v else max(0, v)


def limit_line(ax, y, color='black', **kwargs):
    if isinstance(y, (list)):
        finite = _finite(y)
        if not finite:
            return
        if len(set(finite)) == 1 and len(finite) == len(y):
            y = y[0]
    if isinstance(y, (int, float)):
        ax.axhline(y, color=color, **kwargs)
        add_Y_refs(ax, "%.2f" % y, color=color, label=True, draw_line=False)
    elif isinstance(y, (list)):
        xs = [-.5]
        for _ in range(len(y)):
            xs.append(xs[-1] + 1)
            xs.append(xs[-1])
        xs = xs[:-1]
        xs[0] += 0.5
        xs[-1] -= 0.5

        ys = []
        for _ in y:
            ys.append(_)
            ys.append(_)
        ax.plot(xs, ys, color=color, **kwargs)
        # label with the last subgroup that has a limit (skip blank ones)
        add_Y_refs(ax, "%.2f" % _finite(ys)[-1], color=color, label=True, draw_line=False)
    return


def additional_SD(ax, sd, cl, ucl=None):
    if ucl is None:
        if isinstance(sd, (int, float)) and isinstance(cl, (int, float)):
            limit_line(ax, cl + (sd - cl) / 3 * 2, color='red', linestyle='dashed')
            limit_line(ax, cl + (sd - cl) / 3, color='red', linestyle='dashed')
        else:
            if isinstance(sd, list):
                n = len(sd)
            else:
                n = len(cl)
            if not isinstance(sd, list):
                sd = [sd] * n
            if not isinstance(cl, list):
                cl = [cl] * n
            limit_line(ax, [cli + (sdi - cli) / 3 * 2 for cli, sdi in zip(cl, sd)], color='red', linestyle='dashed')
            limit_line(ax, [cli + (sdi - cli) / 3 for cli, sdi in zip(cl, sd)], color='red', linestyle='dashed')
    else:
        if isinstance(ucl, (int, float)) and isinstance(cl, (int, float)):
            limit_line(ax, max(0, cl - (ucl - cl) / 3 * 2), color='red', linestyle='dashed')
            limit_line(ax, max(0, cl - (ucl - cl) / 3), color='red', linestyle='dashed')
        else:
            if isinstance(ucl, list):
                n = len(ucl)
            else:
                n = len(cl)
            if not isinstance(ucl, list):
                ucl = [ucl] * n
            if not isinstance(cl, list):
                cl = [cl] * n
            limit_line(ax, [_max0(cli - (sdi - cli) / 3 * 2) for cli, sdi in zip(cl, ucl)], color='red', linestyle='dashed')
            limit_line(ax, [_max0(cli - (sdi - cli) / 3) for cli, sdi in zip(cl, ucl)], color='red', linestyle='dashed')

    return


def x_plot(data, bar1=None, pooled=False,
           mean=None, k=3, sigma=None,
           all_SD_lines=True,
           ucl1=None, lcl1=None, bar2=None,
           ucl2=None, lcl2=None, xLabels=None,
           print_out=False, max_label_num=25,
           ylabel1=None, ylabel2=None,
           xlabel=None, ax=None, print_port=print,
           axs=None, fig=None, refY1=None, refY2=None,
           one_chart=False, show_plot=False,
           chart_two_only=False, mr_range=2,
           filename=None, plot_type="x_mR"):

    plot_type = plot_type.upper()
    if "BAR" in plot_type and "R" in plot_type.replace("BAR", ""):
        s = xBar_R(data, pooled=pooled, mean=mean, sigma=sigma, k=k)
    elif "BAR" in plot_type and "S" in plot_type:
        s = xBar_S(data, pooled=pooled, mean=mean, sigma=sigma, k=k)
    else:
        if mr_range > len(data) or mr_range < 2:
            mr_range = 2
        s = x_mR(data, mr_range, mean=mean, sigma=sigma, k=k)

    bar1 = bar1 if bar1 is not None else s["bar1"]
    bar2 = bar2 if bar2 is not None else s["bar2"]
    ucl1 = ucl1 if ucl1 is not None else s["ucl1"]
    ucl2 = ucl2 if ucl2 is not None else s["ucl2"]
    lcl1 = lcl1 if lcl1 is not None else s["lcl1"]
    lcl2 = lcl2 if lcl2 is not None else s["lcl2"]
    ylabel1 = ylabel1 if ylabel1 is not None else s["ylabel1"]
    ylabel2 = ylabel2 if ylabel2 is not None else s["ylabel2"]
    n = s["n"]

    if ax is not None:
        #  one_chart = True
        axs = [ax, ax]
    elif one_chart:
        fig, ax = plt.subplots(1)  # , figsize=(15, 15))
        axs = [ax, ax]
    else:
        if fig is None or axs is None:
            # , figsize=(15, 15), sharex=True)
            fig, axs = plt.subplots(2)
        # Remove vertical space between Axes
        fig.subplots_adjust(hspace=0)

    min_x = min(s["X"]) - (max(s["X"]) - min(s["X"])) * 0.05
    max_x = max(s["X"]) + (max(s["X"]) - min(s["X"])) * 0.05
    if not chart_two_only:
        axs[0].plot(s["X"], s["Y1"], linestyle='-', marker='o', color='black',
                    linewidth=1, markersize=3)
        #  axs[0].axhline(bar1, color='blue')
        #  axs[0].axhline(ucl1, color='red', linestyle='dashed')
        #  axs[0].axhline(lcl1, color='red', linestyle='dashed')
        limit_line(axs[0], bar1, color='blue')
        limit_line(axs[0], ucl1, color='red', linestyle='dashed')
        limit_line(axs[0], lcl1, color='red', linestyle='dashed')
        if all_SD_lines:
            additional_SD(axs[0], ucl1, bar1)
            additional_SD(axs[0], lcl1, bar1)
        add_Y_refs(ax=axs[0], y_values=refY1, label=True)
        axs[0].set(ylabel=ylabel1)
        axs[0].set_xlim(left=min_x, right=max_x)

    if not one_chart:
        axs[1].plot(s["X"], s["Y2"], linestyle='-', marker='o', color='black',
                    linewidth=1, markersize=3)
        #  axs[1].axhline(bar2, color='blue')
        #  axs[1].axhline(ucl2, color='red', linestyle='dashed')
        #  axs[1].axhline(lcl2, color='red', linestyle='dashed')
        limit_line(axs[1], bar2, color='blue')
        limit_line(axs[1], ucl2, color='red', linestyle='dashed')
        limit_line(axs[1], lcl2, color='red', linestyle='dashed')
        if all_SD_lines:
            additional_SD(axs[1], ucl2, bar2)
            additional_SD(axs[1], lcl2, bar2, ucl=ucl2)
        axs[1].set_ylim(bottom=0)
        add_Y_refs(ax=axs[1], y_values=refY2, label=True)
        axs[1].set(ylabel=ylabel2)
        axs[1].set_xlim(left=min_x, right=max_x)

    if xLabels is not None:
        step = 1
        if len(xLabels) > max_label_num:
            step = len(xLabels) / max_label_num
            if step > int(step):
                step = int(step) + 1
            else:
                step = int(step)
        axs[1].set_xticks(range(len(xLabels)), xLabels,
                          rotation='vertical')
        axs[1].set_xticks(axs[1].get_xticks()[::step])

    if xlabel is not None:
        axs[1].set(xlabel=xlabel)

    if show_plot:
        plt.show()

    if filename is not None:
        fname = str(filename) + '.png'
        plt.savefig(
            fname,
            dpi=200,
            format='png')

    if print_out:
        print = print_port
        print("\n---- Control Chart ----")
        if "BAR" in plot_type:
            blank = [i for i, v in enumerate(s["Y2"]) if v != v]
            if blank:
                names = [str(xLabels[i]) if xLabels is not None and i < len(xLabels)
                         else str(i + 1) for i in blank]
                print("Subgroups with fewer than 2 valid values (no %s point): %s"
                      % ("range" if "R" in plot_type.replace("BAR", "") else "SD",
                         ", ".join(names)))
        if not chart_two_only:
            print("\n" + ylabel1)
            t = [["LCL", "Center", "UCL"], []]
            for i in [lcl1, bar1, ucl1]:
                if isinstance(i, (int, float,)):
                    t[1].append("%.2f" % i)
                else:
                    t[1].append("Multiple")
            print(str(gen_table(t)))
            #  print("LCL=%.2f\tmean = %.2f\tUCL=%.2f" % (
            #      lcl1, bar1, ucl1))
        if not one_chart:
            print("\n" + ylabel2)
            #  print("LCL=%.2f\tmean = %.2f\tUCL=%.2f" % (
            #      lcl2, bar2, ucl2))
            t = [["LCL", "Center", "UCL"], []]
            for i in [lcl2, bar2, ucl2]:
                if isinstance(i, (int, float,)):
                    t[1].append("%.2f" % i)
                else:
                    t[1].append("Multiple")
            print(str(gen_table(t)))
        #  print("n = %d" % n)

    res = {"lcl1": lcl1, "bar1": bar1, "ucl1": ucl1,
           "lcl2": lcl2, "bar2": bar2, "ucl2": ucl2,
           "n": n}

    return res


def p_np_plot(p=None, n=1,
              bar1=None, ucl1=None, lcl1=None, xLabels=None,
              print_out=False, max_label_num=25, print_port=print,
              ylabel="P", NP=False,
              xlabel=None, ax=None, fig=None, refY=None,
              filename=None):

    if not isinstance(n, list):
        nlist = [n] * len(p)
    else:
        nlist = n

    p_bar = sum([i * j for i, j in zip(p, nlist)]) / sum(nlist)
    ucl_list = [p_bar + 3 * (p_bar * (1 - p_bar) / i)**.5 for i in nlist]
    lcl_list = [max(0, p_bar - 3 * (p_bar * (1 - p_bar) / i)**.5)
                for i in nlist]
    if NP:
        p_bar *= nlist[0]
        ucl_list = np.array(ucl_list) * nlist[0]
        lcl_list = np.array(lcl_list) * nlist[0]
        p = np.array(p) * nlist[0]

    xs = [-.5]
    for _ in range(len(p)):
        xs.append(xs[-1] + 1)
        xs.append(xs[-1])
    xs = xs[:-1]

    lcl_ys, ucl_ys = [], []
    for ucl in ucl_list:
        ucl_ys.append(ucl)
        ucl_ys.append(ucl)
    for lcl in lcl_list:
        lcl_ys.append(lcl)
        lcl_ys.append(lcl)

    if None in [ax, fig]:
        fig, ax = plt.subplots(1, figsize=(15, 15))

    ax.plot(p, linestyle='-', marker='o', color='black')

    if bar1 is not None:
        p_bar = bar1
    ax.axhline(p_bar, color='blue')

    if ucl1 is not None:
        ax.axhline(ucl1, color='red', linestyle='dashed')
    else:
        ax.plot(xs, ucl_ys, color='red')
    if lcl1 is not None:
        ax.axhline(lcl1, color='red', linestyle='dashed')
    else:
        ax.plot(xs, lcl_ys, color='red')

    ax.set(ylabel=ylabel)
    add_Y_refs(ax=ax, y_values=refY)

    if xLabels is not None:
        step = 1
        if len(xLabels) > max_label_num:
            step = len(xLabels) / max_label_num
            if step > int(step):
                step = int(step) + 1
            else:
                step = int(step)
        ax.set_xticks(range(len(xLabels)), xLabels,
                      rotation='vertical')
        ax.set_xticks(ax.get_xticks()[::step])
    if xlabel is not None:
        ax.set(xlabel=xlabel)
    plt.show()

    if print_out:
        print = print_port
        print("\n---- Control Chart ----")
        print(ylabel)
        print("mean = %.4f" % (p_bar))
        if NP:
            print("UCL = %.3f   LCL=%.3f" % (ucl_list[0], lcl_list[0]))

    return


def cu_plot(c=None, n=1,
            bar1=None, ucl1=None, lcl1=None, xLabels=None,
            print_out=False, max_label_num=25, print_port=print,
            ylabel="P", C=False,
            xlabel=None, ax=None, fig=None, refY=None,
            filename=None):
    p = c
    if not isinstance(n, list):
        nlist = [n] * len(p)
    else:
        nlist = n

    c_bar = sum(c) / sum(nlist)
    ucl_list = [c_bar + 3 * (c_bar / i)**.5 for i in nlist]
    lcl_list = [max(0, c_bar - 3 * (c_bar / i)**.5) for i in nlist]
    c = [float(i) / float(j) for i, j in zip(c, nlist)]
    xs = [-.5]
    for _ in range(len(p)):
        xs.append(xs[-1] + 1)
        xs.append(xs[-1])
    xs = xs[:-1]

    lcl_ys, ucl_ys = [], []
    for ucl in ucl_list:
        ucl_ys.append(ucl)
        ucl_ys.append(ucl)
    for lcl in lcl_list:
        lcl_ys.append(lcl)
        lcl_ys.append(lcl)

    if None in [ax, fig]:
        fig, ax = plt.subplots(1, figsize=(15, 15))

    ax.plot(c, linestyle='-', marker='o', color='black')

    if bar1 is not None:
        c_bar = bar1
    ax.axhline(c_bar, color='blue')

    if ucl1 is not None:
        ax.axhline(ucl1, color='red', linestyle='dashed')
    else:
        ax.plot(xs, ucl_ys, color='red')
    if lcl1 is not None:
        ax.axhline(lcl1, color='red', linestyle='dashed')
    else:
        ax.plot(xs, lcl_ys, color='red')

    ax.set(ylabel=ylabel)
    add_Y_refs(ax=ax, y_values=refY)

    if xLabels is not None:
        step = 1
        if len(xLabels) > max_label_num:
            step = len(xLabels) / max_label_num
            if step > int(step):
                step = int(step) + 1
            else:
                step = int(step)
        ax.set_xticks(range(len(xLabels)), xLabels,
                      rotation='vertical')
        ax.set_xticks(ax.get_xticks()[::step])
    if xlabel is not None:
        ax.set(xlabel=xlabel)

    plt.show()

    if print_out:
        print = print_port
        print("\n---- Control Chart ----")
        print(ylabel)
        print("mean = %.4f" % (c_bar))
        if C:
            print("UCL = %.3f   LCL=%.3f" % (ucl_list[0], lcl_list[0]))

    return
