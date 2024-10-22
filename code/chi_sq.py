import statistics as stat
import numpy as np
from scipy.stats import chi2, norm, kurtosis
from scipy.stats import f as f_dist
from math import log as ln
from prettytable import PrettyTable as PT
########### Own Modules ############
#  from utilities import mean_std_CIs


def chi2_test_stdev(data_list, s0, print_out=False, alpha=0.05,
                    print_port=print):
    df = len(data_list) - 1
    S = stat.variance(data_list) * df
    stdev = stat.stdev(data_list)
    chi_sq = S / s0 / s0
    p = 1 - chi2.cdf(chi_sq, df)

    chi2_low0025 = chi2.ppf(alpha / 2, df)
    chi2_high0975 = chi2.ppf(1 - alpha / 2, df)
    chi2_low005 = chi2.ppf(alpha, df)
    stdev_range_low = (chi2_low0025 * s0 * s0 / df)**.5
    stdev_range_high = (chi2_high0975 * s0 * s0 / df)**.5

    std_range_from_S = ((S / chi2_high0975)**.5, (S / chi2_low0025)**.5)

    std_from_S_high95 = (S / chi2_low005)**.5

    pct = "%.2f%%" % (100 - alpha * 100)

    if print_out:
        print = print_port
        print("Population stdev: %.2f\nSampled stdev: %.2f" % (s0, stdev))
        print("df = %d" % df)
        print("chi square = %.2f" % chi_sq)
        print("Prob of variation is greater than the sample. p = %.2f" % p)
        print(
            "Lower %.2f%% Chi square = %.2f  Top %.2f%% Chi square = %.2f" %
            (alpha * 50, chi2_low0025, alpha * 50, chi2_high0975))
        print(
            pct +
            " confidence range of stdev: (%.2f, %.2f), when sampling %d times from a population with stdev of %.2f." %
            (stdev_range_low,
             stdev_range_high,
             df +
             1,
             s0))
        print(
            pct +
            " confidence range of the population stdev: (%.2f, %.2f), where the samples came from." %
            std_range_from_S)
        print(
            pct +
            " confidence the population stdev lower than %.2f, where the samples came from." %
            std_from_S_high95)

    return {
        "p": p,
        "chi_sq": chi_sq,
        "stdev": stdev,
        "df": df,
        "95_chi2_range": (
            chi2_low0025,
            chi2_high0975),
        "95_range_from_P": (
            stdev_range_low,
            stdev_range_high),
        "n": df + 1,
        "95_range_from_S": std_range_from_S,
        "std_from_S_high95": std_from_S_high95}


def several_tests_stdev_2sided(l1, l2, print_out=True):
    var1 = stat.variance(l1)
    var2 = stat.variance(l2)
    u1 = stat.mean(l1)
    u2 = stat.mean(l2)
    s1 = stat.stdev(l1)
    s2 = stat.stdev(l2)
    n1 = len(l1)
    n2 = len(l2)
    # This replicates Minitab result
    k1 = kurtosis(l1, fisher=True, bias=False)
    k2 = kurtosis(l2, fisher=True, bias=False)
    res = {
        "u1": u1,
        "u2": u2,
        "s1": s1,
        "s2": s2,
        "n1": n1,
        "n2": n2,
        "k1": k1,
        "k2": k2}
#     print(k1,k2)

    f = var1 / var2
    dfn, dfd = n1 - 1, n2 - 1
    p = (1 - f_dist.cdf(f, dfn, dfd)) * 2
    if p > 1:
        f = var2 / var1
        dfn, dfd = n2 - 1, n1 - 1
        p = (1 - f_dist.cdf(f, dfn, dfd)) * 2
    res["F"] = {"f": f, "p": p, "dfn": dfn, "dfd": dfd}

    #  kp = ((n1 - 1) * k1 + (n2 - 1) * k2) / (n1 + n2 - 2)
    #  SE = (kp / 2 / (n1 - 1) + kp / 2 / (n2 - 1))**.5
    z = (ln(var1) - ln(var2)) / (2 / n1 + 2 / n2)**.5
    p2 = 2 * (1 - norm.cdf(abs(z)))
    df = n1 - 1
    res["Bonett"] = {"z": z, "p": p2, "df": df}

    if print_out:
        print("u1 = %.2f\ts1 = %.2f\tn1 = %d" % (u1, s1, n1))
        print("u2 = %.2f\ts2 = %.2f\tn2 = %d" % (u2, s2, n2))
        print("\nTwo-sided F test: (Matches both, but senstive to normality.)")
        print("f ratio = %.2f\tdfn = %d\tdfd = %d" % (f, dfn, dfd))
        print("Two-sided test p=%.2f" % res["F"]["p"])
        print("\nBonett's test (doesn't match Minitab)")
        print("z = %.2f\tp=%.2f" % (z, res["Bonett"]["p"]))

    return res


#####################
#
single_pop_var_test = chi2_test_stdev

# 从一个population取样，测试这个population
# 的波动等于某一波动的可能性
###########################
#
#

# Pearson Chi square
# Expected frequency = (Row total * Column total) / Grand total
# Calculate the chi-square statistic using the formula:
# χ² = Σ [(O - E)² / E]
# Where O is the observed frequency and E is the expected frequency for each cell.
# Determine the degrees of freedom (df). For a contingency table, df =
# (rows - 1) * (columns - 1).


def chi_square(data, print_out=True, print_port=print,
               print_table=False, rKeys=None, cKeys=None):
    a = np.array(data)  # a stores the observed values
    col_sum = np.sum(a, axis=0)
    row_sum = np.sum(a, axis=1)
    ttl_sum = np.sum(col_sum)
    #  print = print_port
    #  print(str(data))
    #  print(str(rKeys) + " rKeys")
    #  print(str(cKeys))
    chi_sq = 0
    e = np.zeros(a.shape)
    try:
        for y in range(a.shape[0]):
            for x in range(a.shape[1]):
                expected = row_sum[y] * col_sum[x] / ttl_sum
                chi_sq += (a[y][x] - expected)**2 / expected
                e[y][x] = expected

        df = (a.shape[0] - 1) * (a.shape[1] - 1)

        p = 1 - chi2.cdf(chi_sq, df)
    except BaseException:
        chi_sq = p = np.nan
    LR = 0
    try:
        for y in range(a.shape[0]):
            for x in range(a.shape[1]):
                expected = row_sum[y] * col_sum[x] / ttl_sum
                LR += 2 * a[y][x] * ln(a[y][x] / expected)
                e[y][x] = expected

        p_LR = 1 - chi2.cdf(LR, df)
    except BaseException:
        p_LR = LR = np.nan

    if print_out:
        print = print_port
        if print_table and cKeys is not None and rKeys is not None:
            print("\n---- Contingency Table ----")
            t = PT()
            l = ["Count/Expected"] + list(cKeys) + ["Total"]
            t.field_names = l
            for y, rkey in enumerate(rKeys):
                l = [rkey]
                for x in range(len(cKeys)):
                    l.append("%d / %.2f" % (a[y][x], e[y][x]))
                l.append("%d" % row_sum[y])
                t.add_row(l)
            l = ["Total"]
            for x in range(len(cKeys)):
                l.append("%d" % col_sum[x])
            l.append("%d" % ttl_sum)
            t.add_row(l)
            print(str(t))

        print("\n---- Chi square test ----")
        print("df = %d" % df)
        t = PT()
        t.field_names = ["Test", "Chi sq", "P > ChiSq"]
        t.add_row(["Likelihood Ratio", "%.3f" % LR, "%.3f" % p_LR])
        t.add_row(["Pearson", "%.3f" % chi_sq, "%.3f" % p])
        print(str(t))

    return {"p Pearson": p, "chi sq Pearson": chi_sq, "df": df,
            "p LR": p_LR, "chi sq LR": LR}

# Key differences and considerations:
#         Robustness:
#             The Brown-Forsythe and O'Brien tests are generally considered the most robust,
#         followed by Levene's test, with the F-test being the least robust to violations of normality.
#
#         Power:
#             Under normal distributions, the F-test is most powerful, followed by Levene's test,
# then Brown-Forsythe. However, for non-normal distributions, the robust
# tests often outperform the F-test.

#         Underlying distribution:
#             If the data is known to follow a specific distribution, this can guide
#         the choice of test. For example, the Brown-Forsythe test performs well for skewed distributions,
# while Levene's test with squared deviations is better for symmetric,
# moderate-tailed distributions.

#         Sample size:
#             For small samples, the O'Brien and Ramsey conditional tests have shown good Type I
#         error control across different distribution shapes


def multi_pop_var_test(data, labels, print_out=False, print_port=print,
                       alpha=0.05):
    # data in a list of lists

    def one_way_anova(data):
        ns = [len(l) for l in data]
        k, N = len(data), sum(ns)
        means = [stat.mean(l) for l in data]
        mean = np.concatenate(data).mean()
        SSB = sum([n * (x - mean)**2 for n, x in zip(ns, means)])
        SSW = sum([sum([(v - stat.mean(l))**2 for v in l]) for l in data])
        F = (SSB / (k - 1)) / (SSW / (N - k))
        p = 1 - f_dist.cdf(F, k - 1, N - k)
        return {"F": F, "p": p}

    def OBrien(data):
        #      uij = [nj(nj - 1.5)(xij - Mj)^2 - 0.5SSj] / [(nj - 1)(nj - 2)]
        #         Where:
        #         uij is the transformed score
        #         nj is the number of observations in group j
        #         xij is the original score
        #         Mj is the mean of group j
        #         SSj is the sum of squared deviations from the mean for group j
        #     Do one way ANOVA to uij
        Zij = [[((len(l) - 1.5) * len(l) * (v - stat.mean(l))**2 -
                 stat.variance(l) * (len(l) - 1) / 2) / (len(l) - 1) / (len(l) - 2)
                for v in l] for l in data]
        return one_way_anova(Zij)

    def Levene(data):
        #    Calculate the absolute deviation from the group mean for each data point:
        #   Zij=|X_ij - X̄_i|, where X_ij is the jth observation in the ith group,
        # and X̄_i is the mean of the ith group.
        Zij = [[abs(v - stat.mean(l)) for v in l] for l in data]
        return one_way_anova(Zij)

    def Brown_Forsythe(data):
        #   Zij=|X_ij - median of the group |
        Zij = [[abs(v - stat.median(l)) for v in l] for l in data]
        return one_way_anova(Zij)

    res = {"OBrien": OBrien(data)}
    res["Levene"] = Levene(data)
    res["Brown_Forsythe"] = Brown_Forsythe(data)

    if print_out:
        print = print_port
        print("\n---- Multi Sample Standard Deviation Test ----")
        t = PT()
        pct = "%.2f%%" % (100 - 100 * alpha)
        t.field_names = ["Sample", "N", "stdev", pct + " CI of std"]
        for i in range(len(data)):
            chi2_r = chi2_test_stdev(
                data[i],
                1,
                alpha=alpha,
                print_out=False,
                print_port=print_port)
            sr = chi2_r["95_range_from_S"]
            t.add_row([labels[i], len(data[i]),
                       "%.3f" % stat.stdev(data[i]),
                       "(%.3f, %.3f)" % sr])
        print(str(t))
        print("Stdev CI method is same to JMP but different from Minitab.")

        print("p value is the prob of the pops' standard deviations are equal.")
        print("O'Brien[.5]       p = %.3f" % res["OBrien"]["p"])
        print("Levene            p = %.3f" % res["Levene"]["p"])
        print("Brown-Forsythe    p = %.3f" % res["Brown_Forsythe"]["p"])
    if len(data) == 2:
        res2 = several_tests_stdev_2sided(data[0], data[1], print_out=False)
        if print_out:
            print("2 Sided F test    p = %.3f" % res2["F"]["p"])
        res["F"] = res2["F"]

    return res

##############
# 从两个population取样，测试这两个population的
# 波动一致的可能性
#######################


def two_pop_var_test(l1, l2, print_out=True):
    res = multi_pop_var_test([l1, l2], print_out=print_out)
    res2 = several_tests_stdev_2sided(l1, l2, print_out=False)
    if print_out:
        print("2 Sided F test    p = %.3f" % res2["F"]["p"])
    res["F"] = res2["F"]

    return res


def var_1sample(data=None, sample_n=None, sample_std=None,
                print_port=print, print_out=False, alpha=0.05,
                s0=None):
    if s0 is None:
        return
    if sample_n is None or sample_std is None:
        if data is None:
            return
        n = len(data)
        std = stat.stdev(data)
    else:
        n = sample_n
        std = sample_std

    df = n - 1

    CIn = (n - 1)**.5 * std  # CI numerator
    CI_95 = (CIn / chi2.ppf(1 - alpha / 2, df)**.5,
             CIn / chi2.ppf(alpha / 2, df)**.5)
    CI_u = CIn / chi2.ppf(alpha, df)**.5
    CI_l = CIn / chi2.ppf(1 - alpha, df)**.5

    chi_sq = (n - 1) * (std / s0)**2
    p_l = chi2.cdf(chi_sq, df)
    p_u = 1 - p_l
    p = 2 * min(p_l, p_u)

    if print_out:
        print = print_port
        pct = "%.2f%%" % (100 - 100 * alpha)
        print("\n---- 1 Sample Variance ----")
        print("N = %d\tstd = %.3f" % (n, std))
        print("H0 s==s0, H1 s!=s0: p = %.3f" % p)
        print("Chi sq CI " + pct + " (%.3f, %.3f)" % CI_95)
        print("H0 s==s0, H1 s>s0: p = %.3f" % p_l)
        print(pct + " Upper bound chi sq of population std: %.3f" % CI_u)
        print("H0 s==s0, H1 s>s0: p = %.3f" % p_u)
        print(pct + " Lower bound chi sq of population std: %.3f" % CI_l)
    return {
        "p": p, "n": n,
        "df": df,
        "stdev": std,
        "CI 95": CI_95, "p gt": p_u, "p lt": p_l,
        "CI upper": CI_u, "CI lower": CI_l
    }


if __name__ == "__main__":
    print(chi_square([[30, 76, 49], [1, 37, 62], [11, 11, 26]]))
    chi_square([[95, 43], [101, 64]])
    chi2_test_stdev([1, 1, 2, 2, 3, 4, 1], 2, print_out=True)
    var_1sample(data=[1, 2, 3, 1, 1, 2, 2], s0=1, print_out=True)
    multi_pop_var_test([[1, 2, 3, 1, 1, 2, 2], [1, 3, 4, 2, 2, 1, 3]], [
        "a", "b"], print_out=True)
    several_tests_stdev_2sided([1, 2, 3, 1, 1, 2, 2], [
        1, 3, 4, 2, 2, 1, 3], print_out=True)
    chi_square([[2, 1], [0, 2], [1, 0]])
    chi_square([[138, 165], [5e9, 5e9]])
