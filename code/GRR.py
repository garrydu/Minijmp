from prettytable import PrettyTable as PT
import pandas as pd
# ############# Own Modules ############
from utilities import d2_2D as d2
from two_way_anova import two_way_anova
from one_way_ANOVA import one_way_anova
from utilities import grouping_by_labels


def GRR_xbar(data, op_key="Operator", pt_key="Part", y_key="Y",
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
        print("\n---- GRR XBar/R (Minitab 20) ----")
        print("Gage Evaluation")
        t = PT()
        t.field_names = ["Source", "Stdev", "6 x Std", "%SV"]
        t.add_row(["Ttl GRR(EV&AV)", "%.3f" % GRR, "%.3f" % (6 * GRR),
                   "%.2f" % (GRR / TTL * 100)])
        t.add_row(["EV(repeatability)", "%.3f" % EV, "%.3f" % (EV * 6),
                   "%.2f" % (EV / TTL * 100)])
        t.add_row(["AV(reproducibility)", "%.3f" % AV, "%.3f" % (AV * 6),
                   "%.2f" % (AV / TTL * 100)])
        t.add_row(["PV(Part to Part)", "%.3f" % PV, "%.3f" % (PV * 6),
                   "%.2f" % (PV / TTL * 100)])
        t.add_row(["Total Variation", "%.3f" % TTL, "%.3f" % (TTL * 6),
                   "%.2f" % (100)])
        print(str(t))
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

    if print_out:
        print = print_port
        print("\n---- GRR EMP (JMP 17) ----")
        print("Variance Components")
        t = PT()
        t.field_names = ["Source", "Stdev", "VarComp", "%Contribution"]
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
    res = {"EV": Rept, "AV": Repd, "PV": PP, "RR": GRR, "TV": TTL,
           "INT": OPP}
    return res


def grr_anova_AIAG(y=None, op=None, part=None, inter=True,
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
        print("\n---- GRR AIAG (JMP 17) ----")
        print("Variance Components")
        t = PT()
        t.field_names = ["Source", "6 x Std", ""]
        t.add_row(["Repeatability", "%.2f" % (6 * Rept**.5),
                   "Equipment Variation"])
        if op is not None:
            t.add_row(["Reproducibility", "%.2f" % (6 * Repd**.5),
                       "Appraiser Variation"])
            t.add_row(["Operator", "%.2f" % (6 * OP**.5), ""])
            if inter:
                t.add_row(["Op. x Part", "%.2f" % (6 * OPP**.5), ""])
        t.add_row(["Gauge R&R", "%.2f" % (6 * GRR**.5), ""])
        t.add_row(["Part Variation", "%.2f" % (6 * PP**.5),
                   "Part Variation"])
        t.add_row(["Total Variation", "%.2f" % (TTL**.5 * 6), ""])
        print(str(t))
        print("Gauge R&R / Total Variation = %.1f%%" % ((GRR / TTL)**.5 * 100))
        print("Number of Distinct Categories = %d" % (int((2 * PP / GRR)**.5)))
        print("\nVariance Components of GRR")
        t = PT()
        t.field_names = ["Source", "Stdev", "VarComp", "%Contribution"]
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


def grr_master(y=None, op=None, part=None, mode="aiag",
               inter=True, print_out=False, print_port=print):
    mode = mode.upper()
    if "XBAR" in mode:
        return grr_xbar_r(y=y, op=op, part=part,
                          print_out=print_out, print_port=print_port)
    if "EMP" in mode:
        return grr_anova_EMP(y=y, op=op, part=part, inter=inter,
                             print_out=print_out, print_port=print_port)
    if "AIAG" in mode:
        return grr_anova_AIAG(y=y, op=op, part=part, inter=inter,
                              print_out=print_out, print_port=print_port)


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
