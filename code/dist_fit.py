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
    t.add_row(["Anderson-Darling", "%.2f" % a2, "%.3f" % p])
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

    #  ad_adjusted = ad_stat * (1 + (0.75/n) + (2.25/n**2))
    # However, I found without adj the p value is closer to the JMP simulated p-value

    if ad_adjusted >= 0.6:
        p = np.exp(1.2937 - 5.709 * ad_adjusted + 0.0186 * ad_adjusted**2)
    elif 0.34 < ad_adjusted < 0.6:
        p = np.exp(0.9177 - 4.279 * ad_adjusted - 1.38 * ad_adjusted**2)
    elif 0.2 < ad_adjusted <= 0.34:
        p = 1 - np.exp(-8.318 + 42.796 * ad_adjusted - 59.938 * ad_adjusted**2)
    else:  # ad_adjusted <= 0.2
        p = 1 - np.exp(-13.436 + 101.14 * ad_adjusted - 223.73 * ad_adjusted**2)

    return p


def goodness_of_fit(rv, data, normal=False):
    if normal:
        res = norm_test(data, print_out=False)
        return res['AD s'], res['AD p']
    else:
        a2 = AD(rv, data)
        #  p = p_simulation(rv, a2, len(data))
        p = approximate_p(a2)
    return a2, p


def fit_norm(data, print_out=True, print_port=print):
    u, s = stat.mean(data), stat.stdev(data)
    #  u, s = norm.fit(data)
    #  print(u, s)
    rv = norm(u, s)
    #  n = len(data)
    abl = ABL(rv, data, 2)
    a2, p = goodness_of_fit(rv, data, normal=True)
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
    a2, p = goodness_of_fit(rv, data)
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
    a2, p = goodness_of_fit(rv, data)
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
    a2, p = goodness_of_fit(rv, data)
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
    a2, p = goodness_of_fit(rv, data)
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
    a2, p = goodness_of_fit(rv, data)
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
