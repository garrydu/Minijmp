from prettytable import PrettyTable as PT
import pandas as pd
import statistics as stats
from scipy.stats import f as f_dist
# ############# Own Modules ############
from utilities import d2_2D as d2
from utilities import gen_table
from two_way_anova import two_way_anova
from one_way_ANOVA import one_way_anova
from utilities import grouping_by_labels


def GRR_xbar(data, op_key="Operator", pt_key="Part", y_key="Y",
             hist_std=None, use_hist=False, spec_gap=None,
             print_out=True, has_op_col=True, print_port=print):

    def EV_stdev(d, op_key="Operator", pt_key="Part", y_key="Y"):
        ranges = []
        n = 0
        for op in d[op_key].unique():
            for part in d[pt_key].unique():
                tmp = d[(d[op_key] == op) & (d[pt_key] == part)]
                n = len(tmp)
                if len(tmp) > 0:
                    ranges.append(max(tmp[y_key] - min(tmp[y_key])))

        rBar = sum(ranges) / len(ranges)
        k = len(ranges)
    #     print(n,k)
    #     print(d2(n,k))
        return rBar / d2(n, k)

    def AV_stdev(d, op_key="Operator", pt_key="Part", y_key="Y"):
        num_of_parts = len(d[pt_key].unique())
        num_of_op = len(d[op_key].unique())
        num_of_tests = len(d) / num_of_parts / num_of_op

        op_avgs = []
        for op in d[op_key].unique():
            tmp = d[d[op_key] == op]
            op_avgs.append(sum(tmp[y_key]) / len(tmp))
        R0 = max(op_avgs) - min(op_avgs)
        return ((R0 / d2(num_of_op, 1))**2 - EV_stdev(d, op_key=op_key,
                                                      pt_key=pt_key, y_key=y_key
                                                      )**2 / num_of_parts / num_of_tests)**.5

    def Part2Part(d, op_key="Operator", pt_key="Part", y_key="Y"):
        part_avgs = []
        for pt in d[pt_key].unique():
            tmp = d[d[pt_key] == pt]
            part_avgs.append(sum(tmp[y_key]) / len(tmp))
        R_part = max(part_avgs) - min(part_avgs)
        return R_part / d2(len(part_avgs), 1)

    if not has_op_col:
        data.insert(1, "Operator", [0] * len(data), True)
        op_key = "Operator"

    EV = EV_stdev(data, op_key=op_key, pt_key=pt_key, y_key=y_key)
    if has_op_col:
        AV = AV_stdev(data, op_key=op_key, pt_key=pt_key, y_key=y_key)
    else:
        AV = 0
    PV = Part2Part(data, op_key=op_key, pt_key=pt_key, y_key=y_key)
    GRR = (EV**2 + AV**2)**.5
    TTL = (GRR**2 + PV**2)**.5

    if print_out:
        print = print_port
        print("\n---- GRR XBar/R ----")
        print("Gage Evaluation")
        t = [
            ["Source", "Std Dev", "6 x SD", "%SV"],
            ["Ttl GRR(EV&AV)", "%.3f" % GRR, "%.3f" % (6 * GRR),
             "%.2f" % (GRR / TTL * 100)],
            ["EV(repeatability)", "%.3f" % EV, "%.3f" % (EV * 6),
             "%.2f" % (EV / TTL * 100)],
            ["AV(reproducibility)", "%.3f" % AV, "%.3f" % (AV * 6),
             "%.2f" % (AV / TTL * 100)],
            ["PV(Part to Part)", "%.3f" % PV, "%.3f" % (PV * 6),
             "%.2f" % (PV / TTL * 100)],
            ["Total Variation", "%.3f" % TTL, "%.3f" % (TTL * 6),
             "%.2f" % (100)]]

        if hist_std is not None:
            t[0] += ["%Process"]
            t[1] += ["%.2f" % (100 * GRR / hist_std)]
            t[2] += ["%.2f" % (100 * EV / hist_std)]
            t[3] += ["%.2f" % (100 * AV / hist_std)]
            t[4] += ["%.2f" % (100 * PV / hist_std)]
            t[5] += ["%.2f" % (100 * TTL / hist_std)]

        if spec_gap is not None:
            t[0] += ["%Tolerance"]
            t[1] += ["%.2f" % (600 * GRR / spec_gap)]
            t[2] += ["%.2f" % (600 * EV / spec_gap)]
            t[3] += ["%.2f" % (600 * AV / spec_gap)]
            t[4] += ["%.2f" % (600 * PV / spec_gap)]
            t[5] += ["%.2f" % (600 * TTL / spec_gap)]

        print(str(gen_table(t)))

        print("Number of Distinct Categories = %d" % (int(PV / GRR * 2**.5)))
        print("\nVariance Components")
        t = PT()
        t.field_names = ["Source", "VarComp", "%Contribution"]
        t.add_row(["Ttl GRR(EV&AV)", "%.3f" % GRR**2,
                   "%.2f" % (GRR**2 / TTL**2 * 100)])
        t.add_row(["EV(repeatability)", "%.3f" % EV**2,
                   "%.2f" % (EV**2 / TTL**2 * 100)])
        t.add_row(["AV(reproducibility)", "%.3f" % AV**2,
                   "%.2f" % (AV**2 / TTL**2 * 100)])
        t.add_row(["PV(Part to Part)", "%.3f" % PV**2,
                   "%.2f" % (PV**2 / TTL**2 * 100)])
        t.add_row(["Total Variation", "%.3f" % TTL**2,
                   "%.2f" % (100)])
        print(str(t))

    res = {"EV": EV**2, "AV": AV**2, "PV": PV**2, "RR": GRR**2, "TV": TTL**2,
           "INT": 0}
    return res


def grr_xbar_r(y=None, op=None, part=None,
               hist_std=None, use_hist=False, spec_gap=None,
               print_out=False, print_port=print):
    """
    input in 1d list, op input is optional
    """

    d = {"Y": y, "Part": part}
    if op is None:
        has_op = False
    else:
        has_op = True
        d["Operator"] = op
    return GRR_xbar(pd.DataFrame(d), has_op_col=has_op,
                    hist_std=hist_std, use_hist=use_hist, spec_gap=spec_gap,
                    print_out=print_out, print_port=print_port)


def grr_inter(y, op, part):
    res = two_way_anova(y, factor_listA=part, factor_listB=op,
                        print_out=False)

    a = len(set(part))  # number of parts
    b = len(set(op))  # number of operators
    n = len(y) / a / b   # number of replicates
    Rept = res["MSE"]  # Repeatibility of equipment
    OP = max((res['MSB'] - res['MSAB']) / a / n, 0)  # operator variance
    OPP = max(0, (res['MSAB'] - Rept) / n)
    PP = max(0, (res['MSA'] - res['MSAB']) / b / n)  # part to part var
    return Rept, OP, OPP, PP


def grr_simple(y, op, part):
    res = two_way_anova(y, factor_listA=part, factor_listB=op,
                        interaction=False, print_out=False)

    a = len(set(part))  # number of parts
    b = len(set(op))  # number of operators
    n = len(y) / a / b   # number of replicates
    Rept = res["MSE"]  # Repeatibility of equipment
    OP = max((res['MSB'] - res['MSE']) / a / n, 0)  # operator variance
    PP = max(0, (res['MSA'] - res['MSE']) / b / n)  # part to part var
    return Rept, OP, 0, PP


def grr_no_op(y, part):
    data = grouping_by_labels(y, part)
    part_list = list(set(part))
    res = one_way_anova(data, part_list, print_out=False)
    a = len(part_list)
    n = len(y) / a
    Rept = res['MSE']
    PP = max(0, (res['MSA'] - Rept) / n)
    return Rept, 0, 0, PP


def grr_anova_EMP(y=None, op=None, part=None, inter=True,
                  print_out=False, print_port=print):
    if op is None:
        inter = False
        Rept, OP, OPP, PP = grr_no_op(y, part)
    else:
        Rept, OP, OPP, PP = grr_inter(y, op, part)
        if OPP == 0 or not inter:
            Rept, OP, OPP, PP = grr_simple(y, op, part)

    # OPP: operator x part variance, e.g. someone is bad at small parts
    Repd = OP   # reproducibility by human
    GRR = Repd + Rept  # total var introduced by human and equipment
    TTL = GRR + PP + OPP

#  Without the interaction, the analysis uses the following formula:
#  DF = (abn – 1) – (a – 1) – (b – 1)
#  With the interaction, the analysis uses the following formula:
#  DF = (abn – 1) – (a – 1) – (b – 1) – [(a – 1) × (b – 1)]

    a = len(set(part))
    b = 1 if op is None else len(set(op))
    #  n = len(y) / a / b
    DF = (len(y) - 1) - (a - 1) - (b - 1)
    if inter:
        DF = DF - (a - 1) * (b - 1)

#  Intraclass correlation (no bias)
#  Part / (Part + Test re-test error)
#  Intraclass correlation (with bias)
#  Part / (Part + Test re-test error + Operator)
#  Intraclass correlation (with bias and interaction)
#  Part / (Part + Test re-test error + Operator + Part*Operator)
#  Bias impact
#  Intraclass correlation (no bias) – Intraclass correlation (with bias)
#  Bias and interaction impact
#  Intraclass correlation (no bias) – Intraclass correlation (with bias and interaction)

    intraclass_no_bias = PP / (PP + Rept)
    intraclass_w_bias = PP / (PP + Rept + Repd)
    intraclass_bias_inter = PP / (PP + OPP + Rept + Repd)
    bias_impact = intraclass_no_bias - intraclass_w_bias
    bias_inter_impact = intraclass_no_bias - intraclass_bias_inter

    guideline = """Classification Guidelines

Classification    Intraclass     Attenuation of    Probability     Probability of
                 Correlation    Process Signals    of Warning,     Warning, Tests*
                                                   Test 1*
----------------------------------------------------------------------------------
First Class      0.80 - 1.00    Less than 11%     0.99 - 1.00     1.00
Second Class     0.50 - 0.80    11 - 29%          0.88 - 0.99     1.00
Third Class      0.20 - 0.50    29 - 55%          0.40 - 0.88     0.92 - 1.00
Fourth Class     0.00 - 0.20    More than 55%     0.03 - 0.40     0.08 - 0.92

* Probability of detecting a three-standard-deviation shift within 10 subgroups using test 1 or tests 1, 5, 6, and 8 of Nelson's Control Chart Rules. Find more info in HELP."""

    def classification(rho):
        if rho > 0.8:
            return "First"
        if rho > .5:
            return "Second"
        if rho > .2:
            return "Third"
        return "Fourth"

    if print_out:
        print = print_port
        print("\n---- GRR EMP (ANOVA) ----")
        print("Variance Components")
        t = PT()
        t.field_names = ["Source", "Std Dev", "VarComp", "%Contribution"]
        t.add_row(["Ttl GRR", "%.3f" % GRR**.5, "%.3f" % GRR,
                   "%.2f" % (GRR / TTL * 100)])
        t.add_row(["Repeatability", "%.3f" % Rept**.5, "%.3f" % Rept,
                   "%.2f" % (Rept / TTL * 100)])
        if op is not None:
            t.add_row(["Reproducibility", "%.3f" % Repd**.5, "%.3f" % Repd,
                       "%.2f" % (Repd / TTL * 100)])
        t.add_row(["Product Var.", "%.3f" % PP**.5, "%.3f" % PP,
                   "%.2f" % (PP / TTL * 100)])
        if inter:
            t.add_row(["Interaction", "%.3f" % OPP**.5, "%.3f" % OPP,
                       "%.2f" % (OPP / TTL * 100)])
        t.add_row(["Total Variation", "%.3f" % TTL**.5, "%.3f" % TTL,
                   "%.2f" % (100)])
        print(str(t))

        print("\nEMP Statistics")
        t = PT()
        t.field_names = ["Statistic", "Value", "Classification"]
        t.add_row(["Test-retest error", "%.3f" % Rept**.5, ""])
        t.add_row(["Degrees of freedom", "%d" % DF, ""])
        t.add_row(["Probable error", "%.3f" % (.674490 * Rept**.5), ""])
        t.add_row(["Intraclass Correlation (no bias)",
                   "%.3f" % intraclass_no_bias,
                   classification(intraclass_no_bias) + " Class"])
        if op is not None:
            t.add_row(["Intraclass Correlation (with bias)",
                       "%.3f" % intraclass_w_bias,
                       classification(intraclass_w_bias) + " Class"])
        if inter:
            t.add_row(["Intraclass Correlation (with bias and interaction)",
                       "%.3f" % intraclass_bias_inter,
                       classification(intraclass_bias_inter) + " Class"])
        if op is not None:
            t.add_row(["Bias Impact", "%.3f" % bias_impact, " "])
        if inter:
            t.add_row(["Bias and Interaction Impact", "%.3f" % bias_inter_impact, ""])
        t.align["Statistic"] = "l"
        print(str(t))

        print("\n")
        print(guideline)

    res = {"EV": Rept, "AV": Repd, "PV": PP, "RR": GRR, "TV": TTL,
           "INT": OPP}
    return res


def grr_anova_AIAG(y=None, op=None, part=None, inter=True,
                   hist_std=None, use_hist=False, spec_gap=None,
                   print_out=False, print_port=print):
    if op is None:
        inter = False
        Rept, OP, OPP, PP = grr_no_op(y, part)
    else:
        Rept, OP, OPP, PP = grr_inter(y, op, part)
        if OPP == 0 or not inter:
            Rept, OP, OPP, PP = grr_simple(y, op, part)

    # OPP: operator x part variance, e.g. someone is bad at small parts
    Repd = OP + OPP  # reproducibility by human
    GRR = Repd + Rept  # total var introduced by human and equipment
    TTL = GRR + PP

    if print_out:
        print = print_port
        print("\n---- GRR AIAG (ANOVA) ----")
        print("Gage Evaluation")

        def gen_t(GRR, EV, AV, OP, OPP, PV, TTL):

            t = [
                ["Source", "Std Dev", "6 x SD", "%SV"],
                ["Ttl GRR(EV&AV)", "%.3f" % GRR, "%.3f" % (6 * GRR),
                 "%.2f" % (GRR / TTL * 100)],
                ["EV(repeatability)", "%.3f" % EV, "%.3f" % (EV * 6),
                 "%.2f" % (EV / TTL * 100)],
                ["AV(reproducibility)", "%.3f" % AV, "%.3f" % (AV * 6),
                 "%.2f" % (AV / TTL * 100)],
                ["Operator", "%.3f" % OP, "%.3f" % (OP * 6),
                 "%.2f" % (OP / TTL * 100)],
                ["Part x Operator", "%.3f" % OPP, "%.3f" % (OPP * 6),
                 "%.2f" % (OPP / TTL * 100)],
                ["PV(Part to Part)", "%.3f" % PV, "%.3f" % (PV * 6),
                 "%.2f" % (PV / TTL * 100)],
                ["Total Variation", "%.3f" % TTL, "%.3f" % (TTL * 6),
                 "%.2f" % (100)]]

            if hist_std is not None:
                t[0] += ["%Process"]
                t[1] += ["%.2f" % (100 * GRR / hist_std)]
                t[2] += ["%.2f" % (100 * EV / hist_std)]
                t[3] += ["%.2f" % (100 * AV / hist_std)]
                t[4] += ["%.2f" % (100 * OP / hist_std)]
                t[5] += ["%.2f" % (100 * OPP / hist_std)]
                t[6] += ["%.2f" % (100 * PV / hist_std)]
                t[7] += ["%.2f" % (100 * TTL / hist_std)]

            if spec_gap is not None:
                t[0] += ["%Tolerance"]
                t[1] += ["%.2f" % (600 * GRR / spec_gap)]
                t[2] += ["%.2f" % (600 * EV / spec_gap)]
                t[3] += ["%.2f" % (600 * AV / spec_gap)]
                t[4] += ["%.2f" % (100 * OP / spec_gap)]
                t[5] += ["%.2f" % (100 * OPP / spec_gap)]
                t[6] += ["%.2f" % (600 * PV / spec_gap)]
                t[7] += ["%.2f" % (600 * TTL / spec_gap)]
            return t if inter else t[:5] + t[6:]

        print(str(gen_table(
            gen_t(GRR**.5, Rept**.5, Repd**.5, OP**.5, OPP**.5, PP**.5, TTL**.5)
        )))
        #  print("Variance Components")
        #  t = PT()
        #  t.field_names = ["Source", "6 x SD", ""]
        #  t.add_row(["Repeatability", "%.2f" % (6 * Rept**.5),
        #             "Equipment Variation"])
        #  if op is not None:
        #      t.add_row(["Reproducibility", "%.2f" % (6 * Repd**.5),
        #                 "Appraiser Variation"])
        #      t.add_row(["Operator", "%.2f" % (6 * OP**.5), ""])
        #      if inter:
        #          t.add_row(["Op. x Part", "%.2f" % (6 * OPP**.5), ""])
        #  t.add_row(["Gage R&R", "%.2f" % (6 * GRR**.5), ""])
        #  t.add_row(["Part Variation", "%.2f" % (6 * PP**.5),
        #             "Part Variation"])
        #  t.add_row(["Total Variation", "%.2f" % (TTL**.5 * 6), ""])
        #  print(str(t))
        print("Gage R&R / Total Variation = %.1f%%" % ((GRR / TTL)**.5 * 100))
        print("Number of Distinct Categories = %d" % (int((2 * PP / GRR)**.5)))
        print("\nVariance Components of GRR")
        t = PT()
        t.field_names = ["Source", "SD", "VarComp", "%Contribution"]
        t.add_row(["Ttl GRR", "%.3f" % GRR**.5, "%.3f" % GRR,
                   "%.2f" % (GRR / TTL * 100)])
        t.add_row(["Repeatability", "%.3f" % Rept**.5, "%.3f" % Rept,
                   "%.2f" % (Rept / TTL * 100)])
        if op is not None:
            t.add_row(["Reproducibility", "%.3f" % Repd**.5, "%.3f" % Repd,
                       "%.2f" % (Repd / TTL * 100)])
        t.add_row(["Product Var.", "%.3f" % PP**.5, "%.3f" % PP,
                   "%.2f" % (PP / TTL * 100)])
        print(str(t))
    res = {"EV": Rept, "AV": Repd, "PV": PP, "RR": GRR, "TV": TTL,
           "INT": OPP}
    return res


def grr_master(y=None, op=None, part=None, mode="aiag", alpha=0.05,
               hist_std=None, use_hist=False, spec_gap=None,
               inter="auto", print_out=False, print_port=print):
    mode = mode.upper()
    if "XBAR" in mode:
        return grr_xbar_r(y=y, op=op, part=part,
                          hist_std=hist_std, use_hist=use_hist, spec_gap=spec_gap,
                          print_out=print_out, print_port=print_port)

    if op is not None and inter.upper() == "AUTO":
        res = two_way_anova(y, factor_listA=part, factor_listB=op,
                            print_port=print_port, interaction=True,
                            print_out=print_out, name_a="Part",
                            name_b="Operator")
        inter = (res['p AB'] <= alpha)
        if print_out:
            print = print_port
            print("alpha to remove interaction term: %.3f" % alpha)
    elif op is None:
        inter = False
    else:
        inter = (inter.upper() == "ON")

    if "EMP" in mode:
        return grr_anova_EMP(y=y, op=op, part=part, inter=inter,
                             print_out=print_out, print_port=print_port)
    if "AIAG" in mode:
        return grr_anova_AIAG(y=y, op=op, part=part, inter=inter,
                              hist_std=hist_std, use_hist=use_hist, spec_gap=spec_gap,
                              print_out=print_out, print_port=print_port)


def grr_nested(y=None, op=None, part=None, print_out=False, print_port=print,
               hist_std=None):
    a = len(set(part))  # a is number of parts
    b = len(set(op))  # number of operators
    n = len(y) / a
    if int(n) < n:
        raise ValueError("The number of measurements per part should be consistent across all parts. A part should be only measured by one operator.")
    if any(len(set([i for i, j in zip(part, op) if j == o])) != len(y) / n / b for o in set(op)):
        raise ValueError("The experiment design is not balanced.")
    a = len(y) / n / b

    # calc anova table
    # https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/measurement-system-analysis/how-to/gage-study/nested-gage-r-r-study/methods-and-formulas/anova-table/
    # SS operator, the formulation in the webpage is inconsitant with Minitab 22 result, the one below is
    grand_mean = stats.mean(y)
    SSO = sum((stats.mean(i for i, j in zip(y, op) if j == o) - grand_mean)**2 * len([i for i, j in zip(y, op) if j == o]) for o in set(op))
    #  print(a, n, SSO)
    ## SS part by operator
    SSPO = n * sum(sum((stats.mean(i for i, k in zip(y, part) if k == p) -
                        stats.mean(i for i, j in zip(y, op) if j == o))**2 for p in set(
        [i for i, j in zip(part, op) if j == o]
    )) for o in set(op))
    # SS repeatability

    def square_sum(l):
        return sum((i - stats.mean(l))**2 for i in l)

    SSR = sum(sum(square_sum([i for i, j, k in zip(y, op, part) if j == o and k == p]) for p in set(part))
              for o in set(op))
    SST = SSR + SSPO + SSO

    #  print(SSO, SSPO, SSR)
    DFO = b - 1
    DFPO = b * (a - 1)
    DFR = a * b * (n - 1)
    DFTTL = a * b * n - 1

    MSO = SSO / DFO
    MSPO = SSPO / DFPO
    MSR = SSR / DFR

    FO = MSO / MSPO
    FPO = MSPO / MSR

    p_o = 1 - f_dist.cdf(FO, DFO, DFPO)
    p_po = 1 - f_dist.cdf(FPO, DFPO, DFR)

    Repeatability = MSR
    Reproducibility = max(0, (MSO - MSPO) / a / n)
    GRR_var_comp = Repeatability + Reproducibility
    std_grr = GRR_var_comp**.5
    std_repeat = Repeatability**.5
    std_reproduce = Reproducibility**.5

    part_var_comp = (MSPO - MSR) / n
    std_part = part_var_comp**.5
    hist_std_used = False
    if hist_std is not None:
        if hist_std >= std_grr:
            std_part = (hist_std**2 - GRR_var_comp)**.5
            part_var_comp = std_part**2
            hist_std_used = True

    ttl_var_comp = part_var_comp + GRR_var_comp
    std_ttl = ttl_var_comp**.5

    distinct = max(1, int(1.41 * std_part / std_grr))

    if print_out:
        print = print_port
        print("\n---- Gage R&R Nested ANOVA ----\n\nGage R&R Nested for Response")
        t = PT()
        t.field_names = ["Source", "DF", "SS", "MS", "F Ratio", "P Value"]
        t.add_row(["Operator", "%d" % DFO, "%.3f" % SSO, "%.3f" % MSO,
                   "%.3f" % FO, "%.3f" % p_o])
        t.add_row(["Part(Operator)", "%d" % DFPO, "%.3f" % SSPO, "%.3f" % MSPO,
                   "%.3f" % FPO, "%.3f" % p_po])
        t.add_row(["Repeatability", "%d" % DFR, "%.3f" % SSR, "%.3f" % MSR, " ", " "])
        t.add_row(["Total", "%d" % DFTTL, "%.3f" % SST, "", "", ""])
        print(str(t))

        print("\nVariance Components")
        t = PT()
        t.field_names = ["Source", "VarComp", "%Contribution"]
        t.add_row(["Total Gage R&R", "%.3f" % GRR_var_comp, "%.2f" % (100 * GRR_var_comp / ttl_var_comp)])
        t.add_row(["  Repeatability", "%.3f" % Repeatability, "%.2f" % (100 * Repeatability / ttl_var_comp)])
        t.add_row(["  Reproducibility", "%.3f" % Reproducibility, "%.2f" % (100 * Reproducibility / ttl_var_comp)])
        t.add_row(["Part-to-part", "%.3f" % part_var_comp, "%.2f" % (100 * part_var_comp / ttl_var_comp)])
        t.add_row(["Total Variation", "%.3f" % ttl_var_comp, "100.00"])
        t.align["Source"] = "l"
        print(str(t))

        if hist_std is not None:
            print("Historical Standard Deviation = %.3f" % hist_std)
        if hist_std_used:
            print("Total Variance = historical stdDev squared")

        print("\nGage Evaluation")
        t = PT()
        t.field_names = ["Source", "Std Dev(SD)", "6 x SD", "SV%"]
        t.align["Source"] = "l"
        t.add_row(["Total Gage R&R", "%.3f" % std_grr, "%.3f" % (6 * std_grr), "%.2f" % (100 * std_grr / std_ttl)])
        t.add_row(["  Repeatability", "%.3f" % std_repeat, "%.3f" % (6 * std_repeat), "%.2f" % (100 * std_repeat / std_ttl)])
        t.add_row(["  Reproducibility", "%.3f" % std_reproduce, "%.3f" % (6 * std_reproduce), "%.2f" % (100 * std_reproduce / std_ttl)])
        t.add_row(["Part-to-part", "%.3f" % std_part, "%.3f" % (6 * std_part), "%.2f" % (100 * std_part / std_ttl)])
        t.add_row(["Total Variation", "%.3f" % std_ttl, "%.3f" % (6 * std_ttl), "100.00"])
        print(str(t))

        if hist_std_used:
            print("Historical standard deviation is used to calculate values of some sources.")

        print("\nNumber of Distinct Categories = %d" % distinct)

    return {"Distinct Categories": distinct, "P value operator": p_o,
            "P value part": p_po, "GRR%": (100 * std_grr / std_ttl),
            "GRR STD": std_grr, "Repeatability STD": std_repeat,
            "Reproducibility STD": std_reproduce}


if __name__ == "__main__":
    c1 = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A',
          'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B',
          'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C']

    c2 = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
          1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
          1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

    c3 = [167, 162, 210, 213, 187, 183, 189, 196, 156, 147,
          155, 157, 206, 199, 182, 179, 184, 178, 143, 142,
          152, 155, 206, 203, 180, 181, 180, 182, 146, 154]
    grr_anova_EMP(y=c3, op=c1, part=c2, print_out=True)
    grr_anova_EMP(y=c3[:-10], op=c1[:-10], part=c2[:-10], print_out=True)
    #  print(c2[:-10])
    grr_anova_AIAG(y=c3, op=c1, part=c2, print_out=True)
    grr_anova_AIAG(y=c3[:-10], op=c1[:-10], part=c2[:-10], print_out=True)
    grr_anova_EMP(y=c3, part=c2, print_out=True)
    grr_master(y=c3, part=c2, print_out=True, mode="xbar")
    grr_master(y=c3, part=c2, print_out=True, mode="aiag")
    grr_xbar_r(y=c3, op=c1, part=c2, print_out=True)
    grr_master(y=c3, part=c2, op=c1, print_out=True, mode="aiag", inter=False)
    Part = [
        5, 4, 7, 7, 2, 3, 6, 10, 1, 1, 10, 6, 8, 2, 8, 3, 9, 9, 5, 4,
        16, 13, 20, 20, 13, 15, 11, 14, 12, 19, 11, 16, 19, 12, 18, 18, 17, 14, 17, 15,
        21, 23, 22, 26, 21, 23, 30, 24, 25, 28, 26, 22, 24, 27, 29, 28, 25, 29, 27, 30
    ]
    Operator = [
        3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
    ]
    Response = [
        120.78, 121.55, 121.33, 121.99, 118.14, 119.35, 122.87, 121.00, 118.03, 117.92, 121.11, 122.87, 119.68, 117.70, 119.90, 119.57, 120.12, 119.68, 120.67, 121.00,
        121.33, 119.68, 120.12, 119.68, 119.24, 115.94, 122.21, 119.90, 119.24, 118.58, 121.88, 121.33, 118.69, 119.46, 119.13, 119.02, 121.33, 120.89, 121.00, 116.49,
        117.92, 121.11, 122.87, 119.68, 117.70, 119.90, 119.57, 120.12, 119.68, 120.67, 121.00, 122.43, 119.68, 117.37, 121.55, 120.56, 119.24, 121.33, 118.03, 118.47
    ]
    #  print([i for i,j,k in zip(Response, Operator, Part) if j==1 and k
    grr_nested(y=Response, op=Operator, part=Part, print_out=True, hist_std=0.5393)
