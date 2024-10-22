    
import numpy as np
from scipy import integrate
from scipy.stats import chi2, ncx2, norm, nct
from statistics import mean, stdev
from prettytable import PrettyTable as PT


def ti_norm(data=None, alpha=0.05, P=0.9,
            sample_mean=None, sample_std=None, sample_n=None,
            print_out=False, print_port=print):
    def equation(k):
        # Source:
        # https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/quality-tools/how-to/tolerance-intervals-normal-distribution/methods-and-formulas/methods-and-formulas/
        def f(x):
            dn = (n - 1) * ncx2.ppf(P, 1, x * x / n)
            return 2 * (1 - chi2.cdf(dn / k / k, n - 1)) * norm.pdf(x)
        result, error = integrate.quad(f, 0, np.inf)
        return result

    def solve(alpha=0.05):
        l, r = 0, 10000
        thd = 0.0001
        while abs(r - l) > thd:
            m = (l + r) / 2
            res = equation(m) - 1 + alpha
            if res > 0:
                r = m
            else:
                l = m
        return l

    if None in [sample_mean, sample_n, sample_std]:
        try:
            n = len(data)
            u = mean(data)
            s = stdev(data)
        except BaseException:
            return
    else:
        n = sample_n
        s = sample_std
        u = sample_mean

    delta = norm.ppf(P) * (n**.5)
    k = nct.ppf(1 - alpha, n - 1, delta) / (n**.5)
    ul = u + k * s
    ll = u - k * s

    k = solve(alpha=alpha)
    ti = (u - k * s, u + k * s)

    if print_out:
        print = print_port
        print("\n---- Tolerance Interval ----")
        pct = "%.2f%%" % (100 - 100 * alpha)
        Pct = "%.2f%%" % (100 * P)
        print(
            pct +
            " confident that at least " +
            Pct +
            " of the population's values for this characteristic will fall between %.2f and %.2f" %
            ti)
        t = PT()
        t.field_names = ["Proportion", "Lower TI", "Upper TI", "1-Alpha"]
        t.add_row(["%.2f" %
                   P, "%.2f" %
                   ti[0], "%.2f" %
                   ti[1], "%.3f" %
                   (1 - alpha)])
        print(str(t))
        print("\nOne-Sided Tolerance Interval")
        t = PT()
        t.field_names = ["Proportion", "Lower TI", "Upper TI", "1-Alpha"]
        t.add_row(["%.2f" % P, "%.2f" % ll, "-", "%.3f" % (1 - alpha)])
        t.add_row(["%.2f" % P, "-", "%.2f" % ul, "%.3f" % (1 - alpha)])
        print(str(t))

    return {"TI": ti, "Upper Bound": ul, "Lower Bound": ll}


if __name__ == "__main__":
    ti_norm(sample_n=10, sample_std=3.052, sample_mean=5.95, print_out=True)
