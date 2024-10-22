# GDu Jun 2024
# The calculation gives same outputs with JMP 17
# However Cpm confidence limits of Overall has 1.5% differences.
# So the Cpm limits are not included here. While the JMP Cpk
# confidence limits (alpha==1) are not that accurate as the Cpk calculated by
# chi2 dist. Using the upper limit of the sampled stdev when alpha==1
# the cpk 95% lower limit is more close to simulation.

from scipy.stats import chi2, norm, nct
from scipy.optimize import root_scalar
import statistics as stat
from prettytable import PrettyTable as PT
############ Own Modules ##############
from utilities import d2_values, scale_factor_f, c4_values, grouping_by_labels, calculate_d3, calculate_d2


def cpl_cpu_95(cpx, n, df, alpha=0.05):
    c = cpx * 3 * (n)**.5

    def equation(x):
        return nct.cdf(c, df, x) - (1 - alpha / 2)

    def equation2(x):
        return nct.cdf(c, df, x) - (alpha / 2)

    try:
        lower = root_scalar(equation,
                            bracket=[-c * 100, c * 100]).root / 3 / (n)**.5
    except BaseException:
        lower = -1
        #  print(equation(-c * 100), equation(c * 100))
    try:
        upper = root_scalar(equation2,
                            bracket=[-c * 100, c * 100]).root / 3 / (n)**.5
    except BaseException:
        #  print(equation2(-c * 100), equation2(c * 100))
        upper = -1

    return lower, upper


def cpk_calc(mean, std, T, usl, lsl, df, N, print_port=print,
             print_out=True, name="", alpha=0.05):
    # https://www.jmp.com/support/help/en/18.0/index.shtml#page/jmp/statistical-details-for-capability-analysis.shtml
    # https://www.jmp.com/support/help/en/17.0/#page/jmp/statistical-details-for-capability-indices-for-normal-distributions.shtml
    cp = (usl - lsl) / 6 / std
    cpl = (mean - lsl) / 3 / std
    cpu = (usl - mean) / 3 / std
    cpk = min(cpl, cpu)
    cpm = min(T - lsl, usl - T) / 3 / std / (1 + ((T - mean) / std)**2)**.5
    #  cpm = (usl - lsl) / 6 / std / (1 + ((T - mean) / std)**2)**.5

    cp_l = cp * (chi2.ppf(alpha / 2, df) / (df))**.5
    cp_u = cp * (chi2.ppf(1 - alpha / 2, df) / (df))**.5
    cpk_delta = norm.ppf(1 - alpha / 2) * (1 / 9 / N /
                                           cpk**2 + 1 / 2 / df)**.5 * cpk
    cpk_l, cpk_u = cpk - cpk_delta, cpk + cpk_delta

    gamma = N * (1 + ((mean - T) / std)**2)**2 / \
        (1 + 2 * ((mean - T) / std)**2)
    cpm_l = cpm * (chi2.ppf(alpha / 2, gamma) / gamma)**.5
    cpm_u = cpm * (chi2.ppf(1 - alpha / 2, gamma) / gamma)**.5

    cpl_l, cpl_u = cpl_cpu_95(cpl, N, df, alpha)
    cpu_l, cpu_u = cpl_cpu_95(cpu, N, df, alpha)

    if print_out:
        print = print_port
        pct = "%.2f%%" % (100 - 100 * alpha)
        print("\n" + name)
        t = PT()
        t.field_names = ["Index", "Estimate", "Lower " + pct, "Upper " + pct]
        t.add_row(['Cpk', "%.3f" % cpk, "%.3f" % cpk_l, "%.3f" % cpk_u])
        t.add_row(['Cpl', "%.3f" % cpl, "%.3f" % cpl_l, "%.3f" % cpl_u])
        t.add_row(['Cpu', "%.3f" % cpu, "%.3f" % cpu_l, "%.3f" % cpu_u])
        t.add_row(['Cp', "%.3f" % cp, "%.3f" % cp_l, "%.3f" % cp_u])
        t.add_row(['Cpm', "%.3f" % cpm, "", ""])
        print(str(t))
        #  print("Cpk\tEst: %.3f\tLower: %.3f\tUpper: %.3f" % (cpk, cpk_l, cpk_u))
        #  print("Cpl\tEst: %.3f\tLower: %.3f\tUpper: %.3f" % (cpl, cpl_l, cpl_u))
        #  print("Cpu\tEst: %.3f\tLower: %.3f\tUpper: %.3f" % (cpu, cpu_l, cpu_u))
        #  print("Cp\tEst: %.3f\tLower: %.3f\tUpper: %.3f" % (cp, cp_l, cp_u))
        #  print("Cpm\tEst: %.3f" % cpm)
        #  print("Cpm\tEst: %.3f\tLower: %.3f\tUpper: %.3f" % (cpm, cpm_l, cpm_u))
    return {"cp": cp, "cpl": cpl, "cpu": cpu, "cpk": cpk, "cpm": cpm,
            "cp_l": cp_l, "cp_u": cp_u, "cpk_u": cpk_u, "cpk_l": cpk_l,
            "cpm_u": cpm_u, "cpm_l": cpm_l, "cpl_l": cpl_l, "cpl_u": cpl_u,
            "cpu_l": cpu_l, "cpu_u": cpu_u}


def nonconformance(data, t, lsl, usl, u, sw, so, print_out=True,
                   print_port=print):
    N = len(data)
    below = len([i for i in data if i < lsl])
    above = len([i for i in data if i > usl])
    wu = 1 - norm.cdf((usl - u) / sw)
    wl = norm.cdf((lsl - u) / sw)
    ou = 1 - norm.cdf((usl - u) / so)
    ol = norm.cdf((lsl - u) / so)
    if print_out:
        print = print_port
        print("\n" + "Nonconformance (Observation and Expected)")
        t = PT()
        t.field_names = [
            'Portion',
            'Observed%',
            "Expected Within%",
            "Expected Overall%"]
        t.add_row(["Below LSL", "%.2f" %
                   (below / N * 100), "%.2f" %
                   (wl * 100), "%.2f" %
                   (ol * 100)])
        t.add_row(["Above USL", "%.2f" %
                   (above / N * 100), "%.2f" %
                   (wu * 100), "%.2f" %
                   (ou * 100)])
        t.add_row(["Total Out", "%.2f" %
                   ((below + above) / N * 100), "%.2f" %
                   ((wl + wu) * 100), "%.2f" %
                   ((ol + ou) * 100)])
        print(str(t))
        #  print(
        #      "Above USL Obs. %.2f%%\tExp. Within %.2f%%\tExp. Overall %.2f%%" %
        #      (above / N * 100, wu * 100, ou * 100))
        #  print(
        #      "Total Out Obs. %.2f%%\tExp. Within %.2f%%\tExp. Overall %.2f%%" %
        #      ((below + above) / N * 100, (wu + wl) * 100, (ou + ol) * 100))

    return {
        "below_s": below / N,
        "above_s": above / N,
        "ttl_s": (
            below + above) / N,
        "below_w": wl,
        "above_w": wu,
        "ttl_w": wl + wu,
        "below_o": ol,
        "above_o": ou,
        "ttl_o": ou + ol}


def cpk(data, target, usl, lsl, print_port=print, within=True,
        print_out=True, use_range=False, alpha=0.05):
    try:
        # if data is a 2D list
        size_subgrp = [len(l) for l in data]
        balanced = (max(size_subgrp) == min(size_subgrp))
        flat_list = [item for sublist in data for item in sublist]
        sub_grps = len(data)

        if use_range:
            within_msg = "Within sigma estimated by averge of ranges over d2."
            std_within = stat.mean(
                [(max(l) - min(l)) / d2_values(len(l)) for l in data])
            if balanced:
                n = len(flat_list) / sub_grps
                A = 2 * calculate_d3(n)**2 / sub_grps / calculate_d2(n)**2
                df_sub = 1 / A - (3 / 16) * A + (3 / 64) * A**2 + 0.25
            else:
                df_sub = len(flat_list) - sub_grps
        else:
            within_msg = "Within sigma estimated by averge of unbiased stdev."
            std_within = stat.mean(
                [stat.stdev(l) / c4_values(len(l)) for l in data])
            df_sub = len(flat_list) - sub_grps
            if balanced:
                n = len(flat_list) / sub_grps
                df_sub = scale_factor_f(n) * df_sub

    except BaseException:
        within_msg = "Within sigma estimated by averge moving range."
        flat_list = data  # 1D for individual MR within
        std_within = stat.mean(
            [abs(i - j) for i, j in zip(data,
                                        data[1:] + [0])][:-1]) / d2_values(2)
        sub_grps = 0
        df_sub = .62 * (len(flat_list) - 1)

    std_overall = stat.stdev(flat_list)
    mean = stat.mean(flat_list)
    stability = std_overall / std_within
    N = len(flat_list)
    lsl, target, usl = sorted([usl, target, lsl])

    res = {"LSL": lsl, "USL": usl, "Target": target, "mean": mean,
           "Within Sigma": std_within, "Overall Sigma": std_overall,
           "N": N, "N Subgroups": sub_grps, "Stability Index": stability}
    if print_out:
        print = print_port
        print("\n---- Process Capabilities ----")
        for key in res:
            if "N" in key:
                print(key + " = %d" % int(res[key]))
            else:
                print(str(key) + " = %.3f" % res[key]
                      if isinstance(res[key], float) else str(res[key]))
        if within:
            print(within_msg)

    if within:
        res["Within"] = cpk_calc(mean, std_within, target,
                                 usl, lsl, df_sub, N, alpha=alpha,
                                 print_port=print_port,
                                 name="Within", print_out=print_out)
    res["Overall"] = cpk_calc(
        mean,
        std_overall,
        target,
        usl,
        lsl,
        N - 1,
        N, print_port=print_port,
        alpha=alpha,
        name="Overall (AKA Ppk in JMP)",
        print_out=print_out)
    res["nonconformance"] = nonconformance(
        flat_list,
        target,
        lsl,
        usl,
        mean,
        std_within,
        std_overall,
        print_port=print_port,
        print_out=print_out)
    res["Flat List"] = flat_list
    return res


if __name__ == "__main__":
    group = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4,
             4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8]
    data = [18.5, 21.2, 19.4, 16.5, 17.9, 19.0, 20.3, 21.2, 19.6, 19.8,
            20.4, 20.5, 22.2, 21.5, 20.8, 20.3, 19.1, 20.6, 20.8, 21.6,
            22.8, 22.2, 23.2, 23.0, 19.0, 20.5, 20.3, 19.2, 20.7, 21.0,
            20.5, 19.1]
    target = 20
    usl = 22
    lsl = 18

    d = grouping_by_labels(data[:-1], group[:-1])
    # d has 3 sample points in the last group, all others are 4

    dd = grouping_by_labels(data, group)
    # dd has consistent 4 samples in each group

    #  cpk(data, target, usl, lsl)
    cpk(data, target, usl, lsl, print_out=True)
    #  cpk(dd, target, usl, lsl, print_out=True)
    #  cpk(d, target, usl, lsl)
    #  cpk(d, target, usl, lsl, use_range=True)
    #  cpk(dd, target, usl, lsl, print_out=True, use_range=True)
    #  cpk(data, 10, 250, 120)
