from scipy.stats import f as f_stat
from prettytable import PrettyTable as PT
import statistics as stat
import statsmodels.api as sm
from statsmodels.formula.api import ols
from pandas import DataFrame as DF
######## Own Modules ##########
from utilities import group_by2factors


def SSA_SSB(data):
    # Source: https://www.pythonfordatascience.org/factorial-anova-python/
    # The direct output of the stats model python is different from Minitab
    # and JMP.
    # However, at least the sums of square are correct.
    l = []
    for i, ith_A in enumerate(data):
        for j, ith_A_jth_B in enumerate(ith_A):
            for k in ith_A_jth_B:
                l.append([i, j, k])
    df = DF(l, columns=["A", "B", "Y"])
    # Step 1: Fit the full model
    full_model = ols("Y ~ C(A, Sum) + C(B, Sum) + C(A, Sum):C(B, Sum)",
                     data=df).fit()

    # To get the complete ANOVA table with Type 3 SS
    anova_table = sm.stats.anova_lm(full_model, typ=3)
    # sample output, the Intercept is the [0] element
    #  Intercept              1812.640170
    #  C(A, Sum)                73.870879
    #  C(B, Sum)                51.032793
    #  C(A, Sum):C(B, Sum)      30.603340
    #  Residual                157.680773
    #  Name: sum_sq, dtype: float64
    return (anova_table.sum_sq.iloc[1],  # SSA
            anova_table.sum_sq.iloc[2],  # SSB
            anova_table.sum_sq.iloc[3])  # SSAB
    # Both type III


def SSA_SSB_simple(data):
    l = []
    for i, ith_A in enumerate(data):
        for j, ith_A_jth_B in enumerate(ith_A):
            for k in ith_A_jth_B:
                l.append([i, j, k])
    df = DF(l, columns=["A", "B", "Y"])
    full_model = ols("Y ~ C(A, Sum) + C(B, Sum)",  # + C(A, Sum):C(B, Sum)",
                     data=df).fit()

    # To get the complete ANOVA table with Type 3 SS
    anova_table = sm.stats.anova_lm(full_model, typ=3)
    return (anova_table.sum_sq.iloc[1],  # SSA
            anova_table.sum_sq.iloc[2])  # ,  # SSB


def two_way_anova(data, factor_listA=None, print_port=print, interaction=True,
                  factor_listB=None, print_out=False, name_a="A", name_b="B"):
    """
    The data input should be a 3D list, the first two dims are the
    two factors. If the factor_listA and B are inputted, the data should be a
    1D list.
    """
    if factor_listA is not None and factor_listB is not None:
        d = group_by2factors(factor_listA, factor_listB, data)
    else:
        d = data
    flat_list = [k for i in d for j in i for k in j]
    n = len(flat_list)
    a = len(d)
    b = len(d[0])
    y_bar = stat.mean(flat_list)
    SST = sum((x - y_bar)**2 for j in d for k in j for x in k)

#######
# The calculation below is more "traditional"
    #  y_bar_a = [stat.mean([k for j in i for k in j]) for i in d]
    #  y_bar_b = [stat.mean([k for j in range(a) for k in d[j][i]])
    #             for i in range(b)]
    #  n_a = [len([k for j in i for k in j]) for i in d]
    #  n_b = [len([k for j in range(a) for k in d[j][i]])
    #         for i in range(b)]
#     SSA=n*b*sum((i-y_bar)**2 for i in y_bar_a)
# The n here is the replicates in each condition not total N
# So it's only good for balanced data, i.e. identical observation
# numbers in each condition
# The method will give same result with TYPE 3 in the balanced situation

#   SSA=sum(j*(i-y_bar)**2 for i,j in zip(y_bar_a,n_a))
# This formula is good for unbalanced situation, but not same to the
# Minitab / JMP TYPE 3 approach

#     SSB=n*a*sum((i-y_bar)**2 for i in y_bar_b)
#    SSB=sum(j*(i-y_bar)**2 for i,j in zip(y_bar_b,n_b))
#    Re_SS_B=sum([(k-y_bar_b[bi])**2 for ai in range(a)
#                for bi in range(b) for k in d[ai][bi]])
#    print(SST-Re_SS_B)
    if interaction:
        SSA, SSB, SSAB = SSA_SSB(d)
        SSE = sum([sum((x - stat.mean(k))**2 for x in k)
                   for j in d for k in j])
    else:
        SSA, SSB = SSA_SSB_simple(d)
        SSAB = 0
        SSE = SST - SSB - SSA - SSAB

    DFA = a - 1
    DFB = b - 1
    DFAB = DFA * DFB if interaction else 0
    DFT = n - 1
    DFE = DFT - DFA - DFB - DFAB

    MSA = SSA / DFA
    MSB = SSB / DFB
    MSE = SSE / DFE
    FA = MSA / MSE
    FB = MSB / MSE
    PA = 1 - f_stat.cdf(FA, DFA, DFE)
    PB = 1 - f_stat.cdf(FB, DFB, DFE)
    if interaction:
        MSAB = SSAB / DFAB
        FAB = MSAB / MSE
        PAB = 1 - f_stat.cdf(FAB, DFAB, DFE)
    else:
        FAB = MSAB = PAB = -1
    #  print(y_bar, y_bar_a, y_bar_b, n_b, n_a)

    if print_out:
        print = print_port
        print(
            "\n---- Two Way ANOVA " +
            "With" if interaction else "Without" +
            " Interaction ----")
        t = PT()
        t.field_names = ["Factor", "Levels"]
        t.add_row([name_a, a])
        t.add_row([name_b, b])
        print(str(t))
        print("\nAnalysis of Variance")
        t = PT()
        t.field_names = ["Source", "DF", "Adj SS", "Adj MS",
                         "F-value", "p-value"]
        t.add_row([name_a, DFA, "%.3f" %
                   SSA, "%.3f" %
                   MSA, "%.3f" %
                   FA, "%.3f" %
                   PA])
        t.add_row([name_b, DFB, "%.3f" %
                   SSB, "%.3f" %
                   MSB, "%.3f" %
                   FB, "%.3f" %
                   PB])
        if interaction:
            t.add_row([name_a +
                       "*" +
                       name_b, DFAB, "%.3f" %
                       SSAB, "%.3f" %
                       MSAB, "%.3f" %
                       FAB, "%.3f" %
                       PAB])
        t.add_row(["Error", DFE, "%.3f" % SSE, "%.3f" % MSE, " ", " "])
        t.add_row(["Total", DFT, "%.3f" % SST, " ", " ", " "])
        print(str(t))
        #  print("Note: The algo is same to Minitab 20, not JMP 17.")

    return {"N": n, "SSE": SSE, "MSE": MSE, "SSA": SSA, "MSA": MSA,
            "SSB": SSB, "SSAB": SSAB, "MSB": MSB, "MSAB": MSAB, "DF A": DFA,
            "DF B": DFB, "DF AB": DFAB, "F A": FA, "F B": FB, "F AB": FAB,
            "p A": PA, "p B": PB, "p AB": PAB}

# The results were tested with Minitab express and JMP 17
# for both balanced and unbalanced data sets


if __name__ == "__main__":
    data = [
        ['male', 'C', 12.40],
        ['female', 'A', 7.69],
        ['male', 'C', 14.01],
        ['female', 'A', 9.69],
        ['male', 'C', 11.65],
        ['female', 'A', 8.89],
        ['female', 'A', 6.94],
        ['female', 'A', 2.13],
        ['female', 'A', 7.26],
        ['female', 'A', 5.87],
        ['male', 'B', 12.93],
        ['female', 'C', 12.19],
        ['female', 'A', 7.20],
        ['male', 'C', 13.88],
        ['male', 'A', 8.18],
        ['male', 'B', 16.64],
        ['female', 'C', 9.41],
        ['male', 'C', 11.21],
        ['female', 'B', 8.35],
        ['male', 'A', 7.24],
        ['female', 'A', 6.81],
        ['male', 'B', 9.81],
        ['female', 'A', 6.67],
        ['female', 'A', 6.98],
        ['female', 'A', 7.07],
        ['female', 'C', 2.40],
        ['male', 'B', 7.84],
        ['female', 'B', 3.84],
        ['male', 'B', 9.42],
        ['male', 'A', 7.00],
        ['male', 'A', 7.00],
        ['female', 'A', 5.00],
        ['male', 'A', 8.00]
    ]
    df = DF(data, columns=['Gender', 'Group', 'Value'])
    d = group_by2factors(df["Gender"], df["Group"], df["Value"])
    two_way_anova(d, print_out=True)
    c1 = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A',
          'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B',
          'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C']

    c2 = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
          1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
          1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

    c3 = [167, 162, 210, 213, 187, 183, 189, 196, 156, 147,
          155, 157, 206, 199, 182, 179, 184, 178, 143, 142,
          152, 155, 206, 203, 180, 181, 180, 182, 146, 154]
    d = group_by2factors(c2, c1, c3)
    #  print(SSA_SSB_simple(d))
    #  two_way_anova_simple(d, print_out=True)
    two_way_anova(d, print_out=True)
    two_way_anova(d, print_out=True, interaction=False)
