from scipy.stats import t as t_test
from scipy.stats import norm
import statistics as stat
############ Own Module #############
#  from utilities import mean_std_CIs


def t_test_1sample(data_list, u0, print_out=False,
                   sample_mean=None, sample_std=None, sample_n=None,
                   df=None, alpha=0.05, print_port=print):
    # Test if the data has the same mean of u0

    if sample_mean is not None and sample_std is not None and sample_n is not None:
        mean = sample_mean
        stdev = sample_std
        n = sample_n
    else:
        mean = stat.mean(data_list)
        stdev = stat.stdev(data_list)
        n = len(data_list)

    t = (mean - u0) / stdev * (n**.5)

    if df is None:
        df = n - 1

    p = (1 - t_test.cdf(abs(t), df)) * 2
    p_l = t_test.cdf(t, df)
    p_g = 1 - p_l

    t_0025 = t_test.ppf(alpha / 2, df)
    t_0975 = t_test.ppf(1 - alpha / 2, df)
    t_005 = t_test.ppf(alpha, df)
    t_095 = t_test.ppf(1 - alpha, df)

    u0_95range = (mean - t_0975 * stdev / (n**.5),
                  mean - t_0025 * stdev / (n**.5))
    u0_lower = mean - t_095 * stdev / (n**.5)
    u0_upper = mean - t_005 * stdev / (n**.5)
    pct = "%.2f%%" % (100 - 100 * alpha)

    # Here P is two tailed test, for one tailed test 1/2
    if print_out:
        print = print_port
        print("\n---- One sample t ----")
        print("mean = %.3f" % mean)
        print("SD = %.3f" % stdev)
        print("t = %.3f" % t)
        print("df = %.3f" % df)
        print("u0 = %.3f"%u0)
        print("Two-tailed test H0 u==u0, H1 u!=u0: p = %.3f" % p)
        print("P-value is the prob of that population mean equals the specified value, which the samples came from.")
        print(
            pct +
            " range of population mean which the samples came from: (%.3f, %.3f)" %
            u0_95range)
        print("H0 u==u0, H1 u>u0 p value = %.3f" % p_g)
        print(pct + " Lower bound of population mean: %.3f" % u0_lower)
        print("H0 u==u0, H1 u<u0 p value = %.3f" % p_l)
        print(pct + " Upper bound of population mean: %.3f" % u0_upper)
    return {
        "t": t,
        "p": p,
        "df": df,
        "mean": mean,
        "stdev": stdev,
        "u0_95range": u0_95range,
        "p gt": p_g, "p lt": p_l,
        "u0 lower": u0_lower, "u0 upper": u0_upper
    }


def z_test_1sample(
        data_list,
        u0,
        s0,
        sample_mean=None,
        alpha=0.05,
        sample_n=None,
        print_out=True,
        print_port=print):

    if sample_mean is None or sample_n is None:
        mean = stat.mean(data_list)
        n = len(data_list)
    else:
        n = sample_n
        mean = sample_mean

    deno = s0 / (n**.5)
    z = (mean - u0) / deno
    p = 2 * (1 - norm.cdf(abs(z)))
    p_l = norm.cdf(z)
    p_u = 1 - p_l

    df = n - 1

    za2 = norm.ppf(alpha / 2)
    CI_95 = (mean + za2 * deno, mean - za2 * deno)
    za = norm.ppf(alpha)
    CI_l = mean + za * deno
    CI_u = mean - za * deno

    # Here P is two tailed test, for one tailed test 1/2
    if print_out:
        print = print_port
        pct = "%.2f%%" % (100 - 100 * alpha)
        print("\n---- One sample Z ----")
        print("mean = %.3f" % mean)
        print("z = %.3f" % z)
        print("df = %.3f" % df)
        print("u0 = %.3f"%u0)
        print("Known SD = %.3f"%s0)
        print("Two-tailed test H0: u==u0, H1 u!=u0: p = %.3f" % p)
        print("P-value is the prob of that population mean equals the specified value, which the samples came from.")
        print(
            pct +
            " range of population mean which the samples came from: (%.3f, %.3f)" %
            CI_95)
        print("H0 u==u0, H1 u>u0 p value = %.3f" % p_u)
        print(pct + " Lower bound of population mean: %.3f" % CI_l)
        print("H0 u==u0, H1 u<u0 p value = %.3f" % p_l)
        print(pct + " Upper bound of population mean: %.3f" % CI_u)

    return {"z": z, "p": p, "df": df, "mean": mean,
            "u0_95range": CI_95,
            "p gt": p_u, "p lt": p_l,
            "u0 lower": CI_l, "u0 upper": CI_u}


def paired_t_test(l1, l2, print_out=False, u0=0,
                  alpha=0.05, print_port=print):
    diff = [i - j for i, j in zip(l1, l2)]
    res = t_test_1sample(diff, u0, print_out=False, alpha=alpha)
#     If p < alpha (e.g., p < 0.05): Reject the null hypothesis.
# There is strong evidence of a significant difference between the
# paired measurements.
    pct = "%.2f%%" % (100 - alpha * 100)
    if print_out:
        print = print_port
        print("\n---- Paired t test ----")
        print("Hypothesized mean of the differences u0 = %.3f" % u0)
        print("Paired difference (Sample 1 - Sample 2):")
        print("mean (ud) = %.3f" % res["mean"])
        print("SD = %.3f" % res["stdev"])
        print("t = %.3f" % res["t"])
        print("df = %.3f" % res["df"])
        print("n = %d" % len(l1))
        print("H0: ud == u0, H1: ud != u0, p = %.3f" % res["p"])
        print("" + pct +
              " range of the difference's mean: (%.3f, %.3f)" %
              res["u0_95range"])
        print("H0: u == u0, H1: ud > u0, p value = %.3f" % res["p gt"])
        print(
            pct +
            " Lower bound of difference's mean: %.3f" %
            res["u0 lower"])
        print("H0: u == u0, H1: ud < u0, p value = %.3f" % res["p lt"])
        print(
            pct +
            " Upper bound of difference's mean: %.3f" %
            res["u0 upper"])
    return res

# Assumptions:
#   Pooled t-test assumes equal population variances between the two groups.
#   Unpooled t-test (Welch's t-test) does not assume equal population variances.
# Degrees of freedom (df) calculation:
#   Pooled t-test: df = n1 + n2 - 2
#   Unpooled t-test: Uses a more complex formula (Welch–Satterthwaite equation)
#   that typically results in non-integer df.
#        df = (s1^2/n1 + s2^2/n2)^2 / [(s1^2/n1)^2/(n1-1) + (s2^2/n2)^2/(n2-1)]
# Variance estimation:
#   Pooled t-test uses a weighted average of the two sample variances (pooled variance).
#   Unpooled t-test uses separate variance estimates for each group.
# Applicability:
#   Pooled t-test is more appropriate when variances are truly equal or sample sizes are equal.
# Unpooled t-test is more robust and generally recommended when unsure
# about variance equality.


def t_test_2samples(l1=None, l2=None,
                    n1=None, n2=None, u1=None, u2=None,
                    s1=None, s2=None,
                    alpha=0.05, d0=0, pooled=False,
                    print_out=False, print_port=print):

    def tTest(dx, d0, s, df, alpha, title,
              print_out=False, print_port=None):
        ta2 = t_test.ppf(alpha / 2, df)
        CI = (dx + ta2 * s, dx - ta2 * s)
        t = (dx - d0) / s
        pl = t_test.cdf(t, df)
        pu = 1 - pl
        p = 2 * (1 - t_test.cdf(abs(t), df))
        if print_out:
            print = print_port
            print("\n" + title)
            pct = "%.2f%%" % (100 - 100 * alpha)
            print(pct + " CI of u2 - u1: (%.3f,%.3f)" % CI)
            print("df = %.3f\tt = %.3f" % (df, t))
            print("H0: u2 - u1 == d0, H1: u2 - u1 != d0, p = %.3f" % p)
            print("H0: u2 - u1 == d0, H1: u2 - u1 < d0, p = %.3f" % pl)
            print("H0: u2 - u1 == d0, H1: u2 - u1 > d0, p = %.3f" % pu)
        return {"CI": CI, "p": p, "p lower": pl, "p upper": pu, "t": t,
                "df": df}

    #  summarized = False
    #  if n1 is not None and n2 is not None:
    #      if s1 is not None and s2 is not None:
    #          if u1 is not None and u2 is not None:
    #              summarized = True
    #  if not summarized:
    #      if l1 is None or l2 is None:
    #          return
    if n1 is None or s1 is None or u1 is None:
        u1 = stat.mean(l1)
        s1 = stat.stdev(l1)
        n1 = len(l1)

    if n2 is None or s2 is None or u2 is None:
        u2 = stat.mean(l2)
        s2 = stat.stdev(l2)
        n2 = len(l2)

    if print_out:
        print = print_port
        print("\n---- Two Samples t tests ----")
        print("u1 = %.3f\ts1 = %.3f\tn1 = %d" % (u1, s1, n1))
        print("u2 = %.3f\ts2 = %.3f\tn2 = %d" % (u2, s2, n2))
        print("d0 = %.3f\tu2 - u1 = %.3f" % (d0, u2 - u1))
    # t = (x̄₁ - x̄₂) / √((s₁²/n₁) + (s₂²/n₂))
    # df = (s1^2/n1 + s2^2/n2)^2 / [(s1^2/n1)^2/(n1-1) + (s2^2/n2)^2/(n2-1)]

    if not pooled:
        # JMP 17 method unequal variances
        s = (s1 * s1 / n1 + s2 * s2 / n2)**.5
        df = (s1 * s1 / n1 + s2 * s2 / n2)**2 / ((s1 * s1 / n1)
                                                 ** 2 / (n1 - 1) + (s2 * s2 / n2)**2 / (n2 - 1))
        res = tTest(u2 - u1, d0, s, df, alpha,
                    "JMP 17 method unequal variances",
                    print_out=print_out, print_port=print_port)
    else:
        #  Minitab unequal variances method
        #  var1 = s1 * s1 / n1
        #  var2 = s2 * s2 / n2
        #  df = (var1 + var2)**2 / (var1**2 / (n1 - 1) + var2**2 / (n2 - 1))
        #  resM = tTest(u2 - u1, d0, s, df, alpha,
        #               "Minitab 20 method unequal variances",
        #               print_out=print_out, print_port=print_port)

        # Equal variances same to both
        sp = (((n1 - 1) * s1 * s1 + s2 * s2 * (n2 - 1)) / (n1 + n2 - 2))**.5
        s = sp * (1 / n1 + 1 / n2)**.5
        df = n1 + n2 - 2
        res = tTest(u2 - u1, d0, s, df, alpha,
                    "Equal variances, pooled t",
                    print_out=print_out, print_port=print_port)

    return res
    #  {"pooled": resP,
    #  #  "minitab": resM,
    #  "jmp": resJ}


if __name__ == "__main__":
    l1 = [1, 2, 3, 1, 1, 2, 2]
    l2 = [1, 3, 4, 2, 2, 1, 3]
    #  t_test_1sample(l1, 1, print_out=True)
    #  paired_t_test(l1, l2, print_out=True)
    #  print(t_test_2samples(l1, l2, print_out=True))
    #  print(t_test_2samples_pooled(l1, l2, print_out=True))
    z_test_1sample(l1, 1, 1, print_out=True)
    t_test_2samples(l1, l2, print_out=True)
    paired_t_test(l1, l2, print_out=True)
