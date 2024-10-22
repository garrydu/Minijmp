from scipy.stats import norm, binom, hypergeom
from scipy.stats import f as f_dist
#  from functools import lru_cache
from prettytable import PrettyTable as PT
#  import numpy as np
####### Own Modules ########
from binomial import binomial
from chi_sq import chi_square


def prop_2sample(n1=None, n2=None, e1=None,
                 e2=None, alpha=0.05, print_out=False,
                 print_port=print):

    if None in [n1, n2, e1, e2] or n1 * n2 == 0:
        return
    n1 = int(n1)
    n2 = int(n2)
    e1 = int(e1)
    e2 = int(e2)
    p1, p2 = e1 / n1, e2 / n2
    p0 = (e1 + e2) / (n1 + n2)
    SE_pooled = (p0 * (1 - p0) * (1 / n1 + 1 / n2))**.5
    SE_sep = (p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)**.5
    pd = p1 - p2
    CI = (pd + norm.ppf(alpha / 2) * SE_sep,
          pd + norm.ppf(1 - alpha / 2) * SE_sep)
    CI2 = (pd + norm.ppf(alpha) * SE_sep,
           pd + norm.ppf(1 - alpha) * SE_sep)
    pct = "%.2f%%" % (100 - 100 * alpha)
    Zp = pd / SE_pooled
    Zs = pd / SE_sep
    pl = norm.cdf(Zs)
    pu = 1 - pl
    p = 2 * min(pl, pu)

    pl_p = norm.cdf(Zp)
    pu_p = 1 - pl_p
    p_p = 2 * min(pl_p, pu_p)

    rv = hypergeom(n1 + n2, e1 + e2, n1)
    pl_f = rv.cdf(e1)
    pu_f = 1 - rv.cdf(max(e1 - 1, 0))

    mode = int((n1 + 1) * (e1 + e2 + 1) / (n1 + n2 + 2))

    if e1 == mode:
        p_f = 1
    elif e1 < mode:
        y = mode
        while rv.pmf(y) >= rv.pmf(e1):
            y += 1
        p_f = rv.cdf(e1) + 1 - rv.cdf(y - 1)
    else:
        y = mode
        while rv.pmf(y) >= rv.pmf(e1):
            y -= 1
        p_f = 1 - rv.cdf(e1 - 1) + rv.cdf(y)

    if print_out:
        print = print_port
        print("\n---- Two samples proportion test ----")
        t = PT()
        t.field_names = ["Sample", "N", "Events", "P ratio"]
        t.add_row(["1", n1, e1, "%.3f" % p1])
        t.add_row(["2", n2, e2, "%.3f" % p2])
        print(str(t))
        print("\np1 - p2 = %.3f" % pd)
        print(pct + " CI of difference (%.3f, %.3f)" % CI)
        print(pct + " Upper bound for difference %.3f" % CI2[1])
        print(pct + " Lower bound for difference %.3f" % CI2[0])
        print("\nH0: p1 == p2")
        t = PT()
        t.field_names = ["p value", "Z", "p1 != p2", "p1 < p2", "p1 > p2"]
        t.add_row(["Fisher's Excat", " ", "%.3f" % p_f,
                   "%.3f" % pl_f, "%.3f" % pu_f])
        t.add_row(["Normal appx.", "%.3f" % Zs, "%.3f" % p,
                   "%.3f" % pl, "%.3f" % pu])
        t.add_row(["Normal appx. pooled", "%.3f" % Zp, "%.3f" % p_p,
                   "%.3f" % pl_p, "%.3f" % pu_p])
        print(str(t))

    return {"p sep": p, "p p1<p2": pl, "p p1>p2": pu,
            "p Fisher": p_f, "p p1<p2 Fisher": pl_f, "p p1>p2 Fisher": pu_f,
            "p Pooled": p_p, "p p1<p2 Pooled": pl_p, "p p1>p2 Pooled": pu_p}


def p_blaker(n, p, k):
    rv = binom(n, p)
    psl = []
    s = 0
    for i in range(n + 1):
        s += rv.pmf(i)
        psl.append(s)

    def pt_le_k(n, p, k):
        return psl[k] if k >= 0 else 0

    def pt_ge_k(n, p, k):
        return 1 - pt_le_k(n, p, k - 1)

    if pt_ge_k(n, p, k) < pt_le_k(n, p, k):
        k_modified = max([i for i in range(n + 1)
                          if pt_le_k(n, p, i) <= pt_ge_k(n, p, k)])
        return pt_ge_k(n, p, k) + pt_le_k(n, p, k_modified)
    elif pt_ge_k(n, p, k) == pt_le_k(n, p, k):
        return 1
    else:
        k_modified = min([i for i in range(n + 1)
                          if pt_ge_k(n, p, i) <= pt_le_k(n, p, k)])
        return pt_le_k(n, p, k) + pt_ge_k(n, p, k_modified)


def p_sterne(n, p, k):
    rv = binom(n, p)
    PTK = rv.pmf(k)
    return sum([rv.pmf(i) for i in range(n + 1) if rv.pmf(i) <= PTK])


def p_likelihood_ratio(n, p0, x):
    p = x / n
    rv = binom(n, p0)

    def LR(i):
        ii = min(i, n - i)
        return (p / p0)**ii * ((1 - p) / (1 - p0))**(n - ii)

    return sum(rv.pmf(y) for y in range(n + 1)
               if LR(y) >= LR(x))


def prop_test_1sample(events=1, N=1, p0=1, print_port=print,
                      print_out=False, alpha=.05):
    p = events / N
    Z = (p - p0) / (p0 * (1 - p0) / N)**.5
    p_norm = (1 - norm.cdf(abs(Z))) * 2
    p_norm_less = norm.cdf(Z)
    b_res = binomial(N, p0, x=events, print_out=False)
    #  print(b_res)
    p_bi = b_res["left_acc_p"]

    std = (p * (1 - p) / N)**.5
    CI_l, CI_u = (p + norm.ppf(alpha / 2) * std,
                  p + norm.ppf(1 - alpha / 2) * std)
    CI_high = p + norm.ppf(1 - alpha) * std
    CI_low = p + norm.ppf(alpha) * std

# https://support.minitab.com/en-us/minitab/help-and-how-to/statistics/basic-statistics/how-to/1-proportion/methods-and-formulas/methods-and-formulas/
# Clopper-Pearson exact confidence interval method
    dfn = 2 * events
    dfd = 2 * (N - events + 1)
    F = f_dist.ppf(alpha / 2, dfn, dfd)
    p_exct_l = dfn * F / (dfd + dfn * F)
    F = f_dist.ppf(alpha, dfn, dfd)
    p_exct_low = dfn * F / (dfd + dfn * F)

    dfn = 2 * (events + 1)
    dfd = 2 * (N - events)
    F = f_dist.ppf(1 - alpha / 2, dfn, dfd)
    p_exct_u = dfn * F / (dfd + dfn * F)
    F = f_dist.ppf(1 - alpha, dfn, dfd)
    p_exct_high = dfn * F / (dfd + dfn * F)

    p_s = p_sterne(N, p0, events)
    p_b = p_blaker(N, p0, events)

    if print_out:
        print = print_port
        print("\n---- One sample propotion test ----")
        #  print("Z porportion test")
        print("\np-value for H0: p==p0, H1: p!=p0")
        print("Normal Approx.   %.3f" % p_norm)
        print("Strerne's Method %.3f" % p_s)
        print("Blaker's Method  %.3f" % p_b)
        print("\nH0: p==p0, H1: p<p0.")
        print("Normal App. p-value = %.3f\nBinomial Exact p-value = %.3f" %
              (p_norm_less, p_bi))
        #  print("p-value %.3f" % p_norm_less,
        #        "for H0 p==p0, H1 p<p0.")
        pct = "%.2f%%" % (100 - alpha * 100)
        #  "CI (%.3f, %.3f), (0, %.3f), (%.3f, 1)" % (
        #      CI_l, CI_u, CI_high, CI_low))
        #  print("\nBinomial test p-value %.3f" %
        #        p_bi, "for gettig less or equal events if real p equals p0.")
        t = PT()
        t.field_names = ["N", "Event", "Sample P Ratio"]
        t.add_row([str(N), str(events), "%.3f" % (events / N)])
        print("")
        print(str(t))
        t = PT()
        print("P ratio CI of " + pct)
        t.field_names = ["Algo", " CI", "Upper Bound",
                         "Lower Bound"]
        t.add_row(["Normal App.", "(%.3f, %.3f)" % (CI_l, CI_u),
                   "%.3f" % CI_high, "%.3f" % CI_low])
        t.add_row(["Clopper-Pearson\nexact", "(%.3f, %.3f)" %
                   (p_exct_l, p_exct_u), "%.3f" %
                   p_exct_high, "%.3f" %
                   p_exct_low])
        print(str(t))
        #  print("\nJMP Test Probabilities in Distributions")

    chi_res = chi_square([[events, N - events],
                          [10000 * N * p0, 10000 * N * (1 - p0)]],
                         print_out=print_out, print_port=print_port)

    return {"p norm": p_norm, "p Binomial": p_bi,
            "Z p less": p_norm_less,
            "CI norm": {"CI l": CI_l, "CI u": CI_u,
                        "CI high": CI_high, "CI low": CI_low},
            "p Sterne": p_s, "p Blaker": p_b,
            "CI exact": {"CI l": p_exct_l, "CI u": p_exct_u,
                         "CI high": p_exct_high, "CI low": p_exct_low},
            "JMP chi sq": chi_res
            }


if __name__ == "__main__":
    print(prop_test_1sample(9, 250, .073, print_out=True))
    prop_2sample(n1=250, e1=9, e2=9, n2=350, print_out=True)
    prop_2sample(n2=250, e1=9, e2=9, n1=350, print_out=True)
    #  print(p_blaker(250, .073, 9), p_sterne(250, .073, 9))
    #  print(p_likelihood_ratio(250, .073, 9))
    #  print(p_likelihood_ratio(50, .35, 10))
    #  print(p_sterne(50, .35, 10))
