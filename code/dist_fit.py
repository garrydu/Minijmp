from scipy.stats import norm, gamma, weibull_min, lognorm, johnsonsu, expon
#  from scipy.stats import gamma as gamma
from scipy.stats import t as t_dist
from math import log as ln
from math import exp
from numpy import nan
import statistics as stat
import numpy as np
from prettytable import PrettyTable as PT
#  from scipy.optimize import minimize
##### Own Modules #####
from utilities import norm_test


def ABL(rv, data, k):
    """
    calculate -2*log-likelihood, AICc and BIC
    rv is the frozen dist function
    k is the number of parameters of the dist funciton.
    """
    log_likelihood = sum(
        ln(rv.pdf(i)) for i in data)
    n = len(data)
    if n - k > 1:
        AICc = -2 * log_likelihood + 2 * k * n / (n - k - 1)
    else:
        AICc = nan
    if n > 0:
        BIC = -2 * log_likelihood + ln(n) * k
    else:
        BIC = nan
    return (-2 * log_likelihood, AICc, BIC)


def print_table(fit_name, para_names, paras, abl, a2, p, print_port=print):
    print = print_port
    print("\n---- Fitted " + fit_name + " Distribution ----")
    t = PT()
    t.field_names = ['Parameter', 'Estimate']
    for i, j in zip(para_names, paras):
        t.add_row([i, "%.3f" % j])
    print(str(t))
    t = PT()
    t.field_names = ['Measures', '-2*LogLikelihood', 'AICc', 'BIC']
    t.add_row(["Value", "%.2f" % abl[0], "%.2f" % abl[1], "%.2f" % abl[2]])
    print(str(t))
    t = PT()
    t.field_names = [' ', 'A-sq', 'Approx. p-value']
    t.add_row(["Anderson-Darling", "%.2f" % a2,
               p if isinstance(p, str) else "%.3f" % p])
    print(str(t))
    print("H0: The data is from the distribution. Small p-value rejects H0.")
    return


def AD(rv, data):
    n = len(data)
    data = np.array(data, dtype=float)
    data = np.sort(data)
    cdf = rv.cdf(data)
# Calculate the AD statistic
    ad_stat = -n - np.sum((2 * np.arange(1, n + 1) - 1) * (np.log(cdf) + np.log(1 - cdf[::-1]))) / n
    return ad_stat


def p_simulation(rv, a2, n, TTL=10000):
    cnt = 0
    for i in range(TTL):
        if AD(rv, rv.rvs(size=n)) >= a2:
            cnt += 1
    return cnt / TTL


def approximate_p(ad_adjusted):
    # The approximate p-value for the second test statistic is computed from a set of four interpolating functions
    # R.B. D'Augostino and M.A. Stephens, Eds., 1986, Goodness-of-Fit Techniques, Marcel Dekker.
    # This is the normal-distribution formula; it expects the adjusted
    # statistic A2 * (1 + 0.75/n + 2.25/n**2).

    if ad_adjusted >= 0.6:
        p = np.exp(1.2937 - 5.709 * ad_adjusted + 0.0186 * ad_adjusted**2)
    elif 0.34 < ad_adjusted < 0.6:
        p = np.exp(0.9177 - 4.279 * ad_adjusted - 1.38 * ad_adjusted**2)
    elif 0.2 < ad_adjusted <= 0.34:
        p = 1 - np.exp(-8.318 + 42.796 * ad_adjusted - 59.938 * ad_adjusted**2)
    else:  # ad_adjusted <= 0.2
        p = 1 - np.exp(-13.436 + 101.14 * ad_adjusted - 223.73 * ad_adjusted**2)

    return p


# Anderson-Darling p-values for fitted (estimated-parameter) distributions,
# as in Minitab's Individual Distribution Identification: D'Agostino and
# Stephens (1986). Exponential uses their closed-form formula; Weibull and
# Gamma use their tables (linear interpolation in p, bounds outside).
# Each table: (p levels, critical values of the modified statistic).
def expon_p(a):
    """Exponential (scale estimated): D'Agostino and Stephens (1986)
    closed-form p-value of the modified statistic a = A2 * (1 + 0.6/n).
    Reproduces Minitab (scale 1.94288, AD 0.256, P 0.883). Minitab shows
    p below 0.003 as '<0.003' (the formula is not used out there)."""
    if a < 0.26:
        p = 1 - np.exp(-12.2204 + 67.459 * a - 110.3 * a**2)
    elif a < 0.51:
        p = 1 - np.exp(-6.1327 + 20.218 * a - 18.663 * a**2)
    elif a < 0.95:
        p = np.exp(0.9209 - 3.353 * a + 0.300 * a**2)
    else:
        p = np.exp(0.731 - 3.009 * a + 0.15 * a**2)
    if a > 2.4 or p < 0.003:
        return "<0.003"
    return float(min(p, 1.0))


# Weibull: extreme-value table (the Weibull of x is the extreme value of ln x)
AD_WEIBULL = ((0.25, 0.10, 0.05, 0.025, 0.01),
              (0.474, 0.637, 0.757, 0.877, 1.038))
# Gamma: the critical values depend on the shape k (last row is k > 20)
AD_GAMMA_P = (0.25, 0.10, 0.05, 0.025, 0.01, 0.005)
AD_GAMMA = {
    1: (0.486, 0.657, 0.786, 0.917, 1.092, 1.227),
    2: (0.477, 0.643, 0.768, 0.894, 1.062, 1.190),
    3: (0.475, 0.639, 0.762, 0.886, 1.052, 1.178),
    4: (0.473, 0.637, 0.759, 0.883, 1.048, 1.173),
    5: (0.472, 0.635, 0.758, 0.881, 1.045, 1.170),
    6: (0.472, 0.635, 0.757, 0.880, 1.043, 1.168),
    8: (0.471, 0.634, 0.755, 0.878, 1.041, 1.165),
    10: (0.471, 0.633, 0.754, 0.877, 1.040, 1.164),
    12: (0.471, 0.633, 0.754, 0.876, 1.038, 1.162),
    15: (0.470, 0.632, 0.754, 0.876, 1.038, 1.162),
    20: (0.470, 0.632, 0.753, 0.875, 1.037, 1.161),
    float("inf"): (0.470, 0.631, 0.752, 0.873, 1.035, 1.159)}


def table_p(a, levels, crit):
    """p-value of the modified statistic a from a critical-value table:
    a number inside the table, or a bound like '>0.250' / '<0.010'."""
    if a < crit[0]:
        return ">%.3f" % levels[0]
    if a > crit[-1]:
        return "<%.3f" % levels[-1]
    return float(np.interp(a, crit, levels))


def gamma_crit(k):
    """Gamma critical values for shape k, interpolated between table rows."""
    keys = sorted(AD_GAMMA)
    if k <= keys[0]:
        return AD_GAMMA[keys[0]]
    if k > 20:
        return AD_GAMMA[float("inf")]
    hi = next(x for x in keys if x >= k)
    lo = keys[keys.index(hi) - 1] if hi != k else hi
    if lo == hi:
        return AD_GAMMA[hi]
    w = (k - lo) / (hi - lo)
    return tuple(a + w * (b - a) for a, b in zip(AD_GAMMA[lo], AD_GAMMA[hi]))


def p_bootstrap(dist, data, a2, n_sim=100, seed=2024):
    """Parametric bootstrap p-value (refits the distribution to every
    simulated sample, as JMP does). A fixed seed gives the same p each run."""
    rng = np.random.default_rng(seed)
    params = dist.fit(data)
    n, hits = len(data), 0
    for _ in range(n_sim):
        sim = dist.rvs(*params, size=n, random_state=rng)
        if AD(dist(*dist.fit(sim)), sim) >= a2:
            hits += 1
    return (hits + 1) / (n_sim + 1)


def goodness_of_fit(rv, data, dist="Normal"):
    """Anderson-Darling statistic of the fitted distribution and its
    p-value (a number, or a bound such as '<0.010' outside the tables)."""
    n = len(data)
    if dist == "Normal":
        res = norm_test(data, print_out=False)
        return res['AD s'], res['AD p']
    if dist == "Lognormal":
        # The normal test on ln(x), as Minitab does
        res = norm_test(np.log(np.asarray(data, dtype=float)), print_out=False)
        return res['AD s'], res['AD p']
    a2 = AD(rv, data)
    if dist == "Exponential":
        p = expon_p(a2 * (1 + 0.6 / n))
    elif dist == "Weibull":
        p = table_p(a2 * (1 + 0.2 / n**.5), *AD_WEIBULL)
    elif dist == "Gamma":
        p = table_p(a2, AD_GAMMA_P, gamma_crit(rv.args[0]))
    elif dist == "Student's t":
        p = "%.2f (simulated)" % p_bootstrap(t_dist, data, a2)
    else:
        p = approximate_p(a2 * (1 + 0.75 / n + 2.25 / n**2))
    return a2, p


def fit_norm(data, print_out=True, print_port=print):
    u, s = stat.mean(data), stat.stdev(data)
    #  u, s = norm.fit(data)
    #  print(u, s)
    rv = norm(u, s)
    #  n = len(data)
    abl = ABL(rv, data, 2)
    a2, p = goodness_of_fit(rv, data, "Normal")
    if print_out:
        print_table("Normal", ("Location mu", "Dispersion sigma"),
                    (u, s), abl, a2, p, print_port=print_port)
    return {"fits": (u, s), "ABL": abl, "rv": rv}

    #  sem = s / n**.5
    #  ses = s / (2 * (n - 1))**.5
    #  print(sem, ses)
    #  print(ll, aicc, bic)
    #  u4 = sum((i - u)**4 for i in data) / n
    #  sess = (1 / n * (u4 - (n - 3) / (n - 1) * s**4))**.5
    #  print(sess / 2 / s)
    #  print(stat.stdev(data))


def fit_t(data, print_out=True, print_port=print):
    #  data = np.array(data)
    df, u, s = t_dist.fit(data)
    #  print(ABL(t_dist(df), (data - u) / s, 3))
    rv = t_dist(df, loc=u, scale=s)
    abl = ABL(rv, data, 3)
    a2, p = goodness_of_fit(rv, data, "Student's t")
    if print_out:
        print_table("Stundent's t",
                    ("Location mu", "Scale sigma", "DF"),
                    (u, s, df), abl, a2, p, print_port=print_port)
    return {"fits": (u, s, df), "ABL": abl, "rv": rv}

    ##### The minimum fitting gives similar but not same results #####

    #  def lsq(parameters):
    #      u, s = parameters
    #      nd = (data - u) / s
    #      df, _, _ = t_dist.fit(nd)
    #      #  rv=t_dist(df)
    #      osm, osr = probplot(data, dist="t", sparams=(df,))[0]
    #      return np.sum((osm - osr) ** 2)
    #  # Initial guess for the parameters
    #  initial_guess = np.array([stat.mean(data), stat.stdev(data)])
    #
    #  # Perform the minimization
    #  objective_function = lsq
    #  result = minimize(objective_function, initial_guess, method='BFGS')
    #
    #  # Extract the results
    #  optimized_params = result.x
    #  minimum_value = result.fun
    #
    #  print("Optimized Parameters:", optimized_params)
    #  print("Minimum Value of the Function:", minimum_value)
    #


def fit_gamma(data, print_out=True, print_port=print):
    #  data = np.array(data)
    # this replicate JMP 17 with fixed location at zero
    #  print(gamma.fit(data, floc=0))
    u, _, s = gamma.fit(data, floc=0)
    #  print(ABL(t_dist(df), (data - u) / s, 3))
    rv = gamma(u, loc=0, scale=s)
    abl = ABL(rv, data, 2)
    a2, p = goodness_of_fit(rv, data, "Gamma")
    if print_out:
        print_table("Gamma", ("Shape alpha", "Scale sigma"),
                    (u, s), abl, a2, p, print_port=print_port)
    return {"fits": (u, s), "ABL": abl, "rv": rv}


def fit_weibull(data,
                print_out=True, print_port=print):
    #  print(weibull_min.fit(data, floc=0))
    u, _, s = weibull_min.fit(data, floc=0)
    rv = weibull_min(u, loc=0, scale=s)
    abl = ABL(rv, data, 2)
    a2, p = goodness_of_fit(rv, data, "Weibull")
    if print_out:
        print_table("Weibull", ("Scale alpha", "Shape beta"),
                    (s, u), abl, a2, p, print_port=print_port)
    return {"fits": (s, u), "ABL": abl, "rv": rv}


def fit_lognorm(data,
                print_out=True, print_port=print):
    #  data = [-i for i in data]
    a, _, s = lognorm.fit(data, floc=0)
    #  print(a, ln(s))
    rv = lognorm(a, loc=0, scale=s)
    abl = ABL(rv, data, 2)
    a2, p = goodness_of_fit(rv, data, "Lognormal")
    if print_out:
        print_table("Lognormal", ("Scale mu", "Shape sigma"),
                    (ln(s), a), abl, a2, p, print_port=print_port)
    return {"fits": (s, a), "ABL": abl, "rv": rv}


def fit_jsu(data):
    print(johnsonsu.fit(data))


def fit_expon(data,
              print_out=True, print_port=print):
    #  print(expon.fit(data, floc=0))
    _, s = expon.fit(data, floc=0)
    rv = expon(loc=0, scale=s)
    abl = ABL(rv, data, 1)
    a2, p = goodness_of_fit(rv, data, "Exponential")
    if print_out:
        print_table("Exponential", ("Scale sigma", ),
                    (s, ), abl, a2, p, print_port=print_port)
    return {"fits": (s,), "ABL": abl, "rv": rv}


def compare_dist(
    data,
    print_out=True,
    print_port=print,
    selected=[
        "Normal",
        "Student's t",
        "Gamma",
        "Lognormal",
        "Exponential",
        "Weibull"]):
    funcs = [fit_norm, fit_t, fit_gamma, fit_lognorm, fit_expon,
             fit_weibull]
    names = ["Normal", "Student's t", "Gamma", "Lognormal", "Exponential",
             "Weibull"]
    aiccs, res = [], []
    for name, func in zip(names, funcs):
        try:
            if name not in selected:
                continue
            r = func(data, print_out=print_out, print_port=print_port)
            res.append([name, r["ABL"], r])
            aiccs.append(r["ABL"][1])
        except BaseException:
            if print_out:
                print = print_port
                print("---- " + name + " ----")
                print("Error: Check input values.")
            pass
    delta_AICc = [i - min(aiccs) for i in aiccs]
    rel_likelihood = [exp(-.5 * i) for i in delta_AICc]
    AICc_weight = [i / sum(rel_likelihood) for i in rel_likelihood]
    for r, i in zip(res, AICc_weight):
        r.append(i)
    res.sort(key=lambda x: -x[-1])
    if print_out and len(selected) > 1:
        print = print_port
        print("\n---- Compare Distributions ----")
        t = PT()
        t.field_names = ['Distribution', 'AICc', 'AICc Weight', 'BIC',
                         '-2*LogLikelihood']
        for r in res:
            t.add_row([r[0],
                       "%.2f" % r[1][1], "%.3f" % r[-1],
                       "%.2f" % r[1][2], "%.2f" % r[1][0]])
        print(str(t))
        print("Note: The AICc weight is the probability that a given model is the best model among a set of candidate models.")
    return res


if __name__ == "__main__":
    data = [
        59,
        61,
        55,
        66,
        52,
        60,
        61,
        51,
        60,
        61,
        56,
        65,
        63,
        58,
        59,
        61,
        62,
        65,
        63,
        62,
        63,
        64,
        65,
        64,
        68,
        64,
        69,
        62,
        64,
        67,
        65,
        66,
        62,
        66,
        65,
        60,
        68,
        62,
        68,
        70]
    data = [1, 2, 3, 4, 2, 12, 3, 12, 3, 2, 14, 3, 2]
    fit_norm(data)
    fit_t(data)
    fit_gamma(data)
    fit_weibull(data)
    fit_lognorm(data)
    fit_jsu(data)
    fit_expon(data)
    compare_dist(data)
