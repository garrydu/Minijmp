from scipy.special import gamma
from scipy import integrate
from scipy.stats import norm, shapiro, chi2
from functools import lru_cache
import numpy as np
from statsmodels.stats.diagnostic import normal_ad
from scipy.stats import t as t_dist
import statistics as stat
from math import isnan
import re
from pandas import DataFrame as DF
######### Own Modules ############
# from binomial import binomial
from chi_sq import chi2_test_stdev
from t_test import t_test_1sample


def split_string(text, delimiters):
    # Create a regular expression pattern from the delimiters
    pattern = '|'.join(map(re.escape, delimiters))
    # Split the string using the pattern
    return re.split(pattern, text)


def add_Y_refs(ax, y_values=[], color='gray', linestyle='dashed', label=False,
               on_top=True):
    zorder = 50 if on_top else None
    if isinstance(y_values, str):
        try:
            y_values = [float(i) for i in split_string(
                y_values, [',', ' ', ';', ':', '|'])
                if len(i) > 0]
        except BaseException:
            return
    if isinstance(y_values, list):
        for y in y_values:
            ax.axhline(y, color=color, linestyle=linestyle)
            if label:
                ax.text(ax.get_xlim()[1] * 1.01, y, f'{y}',
                        verticalalignment='center',
                        horizontalalignment='left',
                        color=color, zorder=zorder)
    return


def is_number(x):
    try:
        i = float(x)
        if i > 0 or i <= 0:
            return True
    except BaseException:
        pass
    return False


def is_void(x):
    if len(str(x).replace(" ", "")) == 0:
        return True
    try:
        if isnan(x):
            return True
    except BaseException:
        pass
    return False


def count_1factor(col):
    [col] = filter_voids([col])
    keys = sorted(list(set(col)))
    res = [0 for i in range(len(keys))]
    for item in col:
        res[keys.index(item)] += 1
    return res, keys


def count_2factors(colr, colc):
    """
    A list of the column data of rows
    and a list of the column data of cols.
    """
    r, c = [], []
    for i, j in zip(colr, colc):
        if is_void(i) or is_void(j):
            continue
        r.append(i)
        c.append(j)
    rKeys = sorted(list(set(r)))
    cKeys = sorted(list(set(c)))
    v = [1 for i in range(len(c))]
    res = group_by2factors(r, c, v)
    return [[sum(_) for _ in i] for i in res], rKeys, cKeys


def make_dict(data, col_names):
    """
    Input data is a list of the data points, which can be lists too.
    col_names are the key values of the dict
    output: dict with by order key with the data points
    """
    res = dict()
    for i in range(len(col_names)):
        try:
            res[col_names[i]] = data[i]
        except BaseException:
            pass
    return res


def event_count(data, x):
    xs = str(x).upper()
    cnt = ttl = 0
    for _ in data:
        try:
            if is_void(_):
                continue
        except BaseException:
            pass
        ttl += 1
        if str(_).upper() == xs:
            cnt += 1
        else:
            try:
                if float(_) == float(x):
                    cnt += 1
            except BaseException:
                pass
    return ttl, cnt


def mean_std_CIs(data, alpha=0.05, print_out=False, print_port=print):
    chi2_r = chi2_test_stdev(
        data,
        1,
        alpha=alpha,
        print_out=False,
        print_port=print_port)
    std_2side_range = chi2_r["95_range_from_S"]
    chi2_r = chi2_test_stdev(
        data,
        1,
        alpha=2 * alpha,
        print_out=False,
        print_port=print_port)
    std_1side_range = chi2_r["95_range_from_S"]

    t_r = t_test_1sample(
        data,
        1,
        alpha=alpha,
        print_out=False,
        print_port=print_port)
    mean_2side_range = t_r["u0_95range"]
    t_r = t_test_1sample(
        data,
        1,
        alpha=2 * alpha,
        print_out=False,
        print_port=print_port)
    mean_1side_range = t_r["u0_95range"]

    if print_out:
        print = print_port
        print("\n---- Confidence Intervals ----")
        pct = "%.1f%% " % (100 - 100 * alpha)
        print("For the population where the samples came from:\n")
        print(
            pct +
            "Prob that mean is in the range of (%.3f, %.3f)" %
            mean_2side_range)
        print(pct + "Prob that mean is less than %.3f." % mean_1side_range[1])
        print(
            pct +
            "Prob that mean is greater than %.3f.\n" %
            mean_1side_range[0])
        print(
            pct +
            "Prob that stdev is in the range of (%.3f, %.3f)" %
            std_2side_range)
        print(pct + "Prob that stdev is less than %.3f." % std_1side_range[1])
        print(
            pct +
            "Prob that stdev is greater than %.3f." %
            std_1side_range[0])
        print("Stdev CI method is same to JMP but different from Minitab.")
    return {"std 2side": std_2side_range, "std 1side": std_1side_range,
            "mean 2side": mean_2side_range, "mean 1side": mean_1side_range}


def pearson_correlation(x, y, alpha=0.05, print_out=True, print_port=print):
    print = print_port
    sx, sy = sum(x), sum(y)
    sx2 = sum([i * i for i in x])
    sy2 = sum([i * i for i in y])
    sxy = sum([i * j for i, j in zip(x, y)])
    n = len(x)
    x_bar, y_bar = sx / n, sy / n
#     r = [n(ΣXY) - (ΣX)(ΣY)] / √[n(ΣX²) - (ΣX)²][n(ΣY²) - (ΣY)²]
    r = (n * sxy - sx * sy) / ((n * sx2 - sx * sx) * (n * sy2 - sy * sy))**.5
#     Cov(X,Y) = Σ[(X - X̄)(Y - Ȳ)] / (n - 1)
    cov = sum([(i - x_bar) * (j - y_bar) for i, j in zip(x, y)]) / (n - 1)
    # https://zhiyzuo.github.io/Pearson-Correlation-CI-in-Python/
    # below confidence level calc
    #  print(r)
    if abs(r) < 1:
        r_z = np.arctanh(r)
    else:
        r_z = 10000
    se = 1 / np.sqrt(n - 3)
    z = norm.ppf(1 - alpha / 2)
    lo_z, hi_z = r_z - z * se, r_z + z * se
    lo, hi = np.tanh((lo_z, hi_z))
#     Calculate the t-statistic using the formula:
#     t = r * √((n-2) / (1-r²))
#     where n is the sample size
#     Determine the degrees of freedom (df):
#     df = n - 2
    if abs(r) == 1:
        p = a = b = theta = 0
    else:
        t = abs(r * ((n - 2) / (1 - r * r))**.5)
        p = (1 - t_dist.cdf(t, n - 2)) * 2

    # Calculate ellipse
# Source: https://education.illinois.edu/docs/default-source/carolyn-anderson/edpsy584/lectures/MultivariateNormal-beamer-online.pdf
# page 8 to p 22
# The numpy eigenvalue flipped order comparing to the slide
# Don't know why, swapping D1 and D0 seems work well.
# Important: chi2 cumulated prob uses 1-alpha, not 1-alpha/2

        xv = stat.variance(x)
        yv = stat.variance(y)
        D, E = np.linalg.eig([[xv, cov], [cov, yv]])
        X2 = chi2.ppf(1 - alpha, 2)
        x1 = (X2 * D[1])**.5 * E[0][0]
        y1 = (X2 * D[1])**.5 * E[0][1]
        x2 = (X2 * D[0])**.5 * E[1][0]
        y2 = (X2 * D[0])**.5 * E[1][1]
        a = (x1 * x1 + y1 * y1)**.5
        b = (x2 * x2 + y2 * y2)**.5
        theta = np.arctan(x1 / y1)

    if print_out:
        print("\n---- Pearson correlation alpha = %.3f ----" % alpha)
        print("Correlation coefficient: %.3f" % r)
        print("Confidence Interval (%.3f, %.3f)" % (lo, hi))
        print("Covariance: %.3f" % cov)
        print("p-value = %.3f\tN = %d" % (p, n))
        print("P-value is the probability of there is no relationship betweent the two populations.")

    return {"r": r, "r_l": lo, "r_u": hi, "cov": cov, "p": p, "N": n,
            "ellipse": {"a": a, "b": b, "theta": theta}}


# https://en.wikipedia.org/wiki/Unbiased_estimation_of_standard_deviation
# to get unbiased std use normal std (mean.stdev) divided by c4 below
# n is the number of sample points.


def c4_values(n):
    return (2 / (n - 1))**.5 * gamma(n / 2) / gamma((n - 1) / 2)


def scale_factor_f(n):
    # https://www.jmp.com/support/help/en/17.0/#page/jmp/statistical-details-for-capability-indices-for-normal-distributions.shtml
    return 1 / 2 / (n - 1) / (1 / c4_values(n)**2 - 1)


def d2_2D(n, k):
    # https://andrewmilivojevich.com/d2-values-for-the-distribution-of-the-average-range/
    data = [
        [1.414, 1.912, 2.239, 2.481, 2.673, 2.830, 2.963, 3.078, 3.179, 3.263, 3.330, 3.424, 3.491, 3.533],
        [1.279, 1.809, 2.151, 2.405, 2.604, 2.768, 2.906, 3.025, 3.129, 3.221, 3.308, 3.380, 3.449, 3.513],
        [1.197, 1.729, 2.079, 2.379, 2.631, 2.847, 3.036, 3.196, 3.332, 3.449, 3.589, 3.689, 3.825, 3.930],
        [1.206, 1.750, 2.105, 2.366, 2.570, 2.736, 2.877, 2.997, 3.103, 3.197, 3.282, 3.358, 3.428, 3.492],
        [1.171, 1.733, 2.096, 2.398, 2.628, 2.830, 3.021, 2.987, 3.098, 3.173, 3.272, 3.347, 3.424, 3.489],
        [1.181, 1.721, 2.090, 2.333, 2.558, 2.726, 2.867, 2.988, 3.095, 3.189, 3.274, 3.351, 3.421, 3.486],
        [1.173, 1.726, 2.085, 2.349, 2.555, 2.723, 2.864, 2.986, 3.095, 3.187, 3.272, 3.345, 3.419, 3.481],
        [1.166, 1.721, 2.082, 2.346, 2.559, 2.720, 2.862, 2.984, 3.090, 3.187, 3.274, 3.354, 3.417, 3.482],
        [1.164, 1.718, 2.080, 2.344, 2.550, 2.719, 2.860, 2.982, 3.089, 3.184, 3.269, 3.346, 3.416, 3.481],
        [1.160, 1.716, 2.072, 2.343, 2.548, 2.712, 2.858, 2.981, 3.088, 3.183, 3.269, 3.342, 3.414, 3.480],
        [1.157, 1.714, 2.076, 2.340, 2.547, 2.716, 2.858, 2.980, 3.087, 3.182, 3.267, 3.344, 3.415, 3.473],
        [1.155, 1.712, 2.074, 2.3491, 2.546, 2.715, 2.857, 2.979, 3.086, 3.181, 3.266, 3.343, 3.414, 3.479],
        [1.154, 1.710, 2.072, 2.338, 2.545, 2.714, 2.856, 2.978, 3.085, 3.180, 3.266, 3.343, 3.413, 3.478],
        [1.151, 1.709, 2.072, 2.337, 2.545, 2.714, 2.856, 2.978, 3.085, 3.180, 3.265, 3.342, 3.413, 3.478],
        [1.150, 1.708, 2.071, 2.337, 2.544, 2.713, 2.855, 2.977, 3.084, 3.179, 3.265, 3.342, 3.412, 3.477],
        [1.128, 1.693, 2.059, 2.326, 2.534, 2.704, 2.847, 2.970, 3.078, 3.173, 3.259, 3.336, 3.407, 3.472]]
    if n > 15:
        n = 15
    if k > 16:
        k = 16
    return data[k - 1][n - 2]


def d2_values(n):
    # The d2 value here is same to the GRR d2 with k==15
    # Source: https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/control-charts/how-to/time-weighted-charts/ewma-chart/methods-and-formulas/unbiasing-constants-d2-d3-and-d4/
    #
    d2 = [0, 0,
          1.128379167,  # n = 2
          1.692568751,  # n = 3
          2.058751154,  # n = 4
          2.325929342,  # n = 5
          2.534413951,  # n = 6
          2.704000246,  # n = 7
          2.847000307,  # n = 8
          2.970000000,  # n = 9
          3.077999711,  # n = 10
          3.173000000,  # n = 11
          3.258000000,  # n = 12
          3.336000000,  # n = 13
          3.407000000,  # n = 14
          3.472000000,  # n = 15
          3.532000000,  # n = 16
          3.588000000,  # n = 17
          3.640000000,  # n = 18
          3.689000000,  # n = 19
          3.735000000,   # n = 20
          3.778, 3.819, 3.858, 3.895, 3.931, 3.964, 3.997, 4.027, 4.057, 4.086, 4.113, 4.139, 4.165, 4.189, 4.213, 4.236, 4.259, 4.280, 4.301, 4.322, 4.341, 4.361, 4.379, 4.398, 4.415, 4.433, 4.450, 4.466, 4.482, 4.498]
    return d2[n] if n < 51 else d2[50]


def grouping_by_labels(data_list, grouping_list, keys=None, return_keys=False):
    [data_list, grouping_list] = filter_voids([data_list, grouping_list])
    #  print(data_list, grouping_list)
    if keys is None:
        #  print(grouping_list)
        keys = sorted(list(set(grouping_list)))
    res = [[] for i in range(len(keys))]
    for i, j in zip(grouping_list, data_list):
        res[keys.index(i)].append(j)
    if return_keys:
        return res, keys
    return res


def group_df_to_list(df, y_key="Value", grp_key="Date"):
    return [list(df[df[grp_key] == gid][y_key])
            for gid in df[grp_key].unique()]


def group_by2factors(f1, f2, d):
    [f1, f2, d] = filter_voids([f1, f2, d])
    f2_d = [(i, j) for i, j in zip(f2, d)]
    gf1 = grouping_by_labels(f2_d, f1)
    res = []
    f2key = sorted(list(set(f2)))
    for sublist in gf1:
        factor = [i[0] for i in sublist]
        data = [i[1] for i in sublist]
        res.append(grouping_by_labels(
            data, factor, keys=f2key))
    return res


def filter_voids(data):
    """
    data comes as a 2D list, all the elements in the same row
    will not be void
    """
    res = [[] for i in range(len(data))]
    for y in range(len(data[0])):
        OK = True
        for x in range(len(data)):
            try:
                if is_void(data[x][y]):
                    OK = False
            except BaseException:
                OK = False
        if OK:
            for x in range(len(data)):
                res[x].append(data[x][y])
    return res


@lru_cache
def calculate_d2(n):
    def integrand(x):
        return 1 - (1 - norm.cdf(x))**n - norm.cdf(x)**n

    d2, _ = integrate.quad(integrand, -10, 10)  # -float('inf'), float('inf'))
    return d2  # round(d2,5)


@lru_cache
def calculate_d3(n):
    def inner_integrand(x, y):
        return 1 - norm.cdf(y)**n - (1 - norm.cdf(x))**n + \
            (norm.cdf(y) - norm.cdf(x))**n

    def outer_integrand(y):
        result, _ = integrate.quad(
            lambda x: inner_integrand(
                x, y), -10, y)  # -float('inf'), y)
        return result

    integral, _ = integrate.quad(outer_integrand, -10, 10)
    # -float('inf'), float('inf'))
    d3 = (2 * integral - calculate_d2(n)**2)**.5
    return d3  # round(d3,5)


def quantiles(input_data,
              percentiles=[100, 99.5, 97.5, 90, 75, 50,
                           25, 10, 2.5, 0.5, 0]):

    data = sorted([i for i in input_data])
    N = len(data)
    # x input is percentile
    def p(x): return (N + 1) * x / 100

    def value(i):
        if i <= 1:
            return data[0]
        if i >= N:
            return data[-1]
        a1 = data[int(i) - 1]
        a2 = data[int(i)]
        dec = i - int(i)
        return a1 + (a2 - a1) * dec

    res = []
    for i in percentiles:
        res.append(value(p(i)))
    return res
    ########## Result same to JMP  ##################


def norm_test(data, print_out=False, print_port=print):
    s1, p1 = shapiro(data)
    s2, p2 = normal_ad(np.array(data))
    if print_out:
        print = print_port
        print("\n---- Normality Test ----")
        print(f"Shapiro-Wilk test\tstats {s1:.3f}\tp-value {p1:.3f}")
        print(f"Anderson Darling test\tstats {s2:.3f}\tp-value {p2:.3f}")
        print("P-value indicates the probability of sampling from a normal distributed population.")
    return {"shapiro s": s1, "shapiro p": p1, "AD s": s2, "AD p": p2}


def number_list(data, col_name="unknown", print_out=False,
                print_port=print):
    l = list(data)
    res = []
    for i in l:
        try:
            j = float(i)
            if j < 0 or j >= 0:
                res.append(j)
        except BaseException:
            pass
    if print_out:
        print = print_port
        print("Col: " +
              col_name +
              ", inputs: %d, valid numbers: %d" %
              (len(l), len(res)))
    return res


def number_2lists(d1, d2, col_name1="unknown",
                  col_name2="unknown", print_out=False,
                  print_port=print):
    l1 = list(d1)
    l2 = list(d2)
    x, y = [], []
    for i, j in zip(l1, l2):
        try:
            ii = float(i)
            jj = float(j)
            if jj < 0 or jj >= 0:
                if ii < 0 or ii >= 0:
                    x.append(ii)
                    y.append(jj)
        except BaseException:
            pass
    if print_out:
        print = print_port
        print(
            "Col " +
            col_name1 +
            " inputs: %d" %
            len(l1) +
            ", Col " +
            col_name2 +
            " inputs: %d." %
            len(l2))
        print("Valid number pairs: %d." % len(x))
    return x, y


def get_number(x):
    """x is a tk variable with get()"""
    try:
        return float(x.get())
    except BaseException:
        return None


def transpose_2D_list(matrix):
    return list(map(list, zip(*matrix)))


def stack_df_num_cols(df=None, cols=None, x=None):
    data = []
    if x is None:
        for key in cols:
            for i in df[key]:
                if is_number(i):
                    data.append([key, float(i)])
        return DF(data, columns=["Labels", "Values"])
    for key in cols:
        for i, j in zip(df[key], df[x]):
            if is_number(i) and is_number(j):
                data.append([key, float(i), float(j)])
    return DF(data, columns=["Labels", "Values", x])


def number_2Dlist(df=None, cols=None,
                  print_out=False, print_port=print):
    n = df[cols[0]].shape[0]
    res = []
    for i in range(n):
        r = []
        for col in cols:
            try:
                _ = float(df[col].iloc[i])
                if _ > 0 or _ <= 0:
                    r.append(_)
            except BaseException:
                pass
        if len(r) == len(cols):
            res.append(r)
    if print_out:
        print = print_port
        print("Received %d cols of data. Found %d rows valid." % (
            len(cols), len(res)))
    return transpose_2D_list(res)


def verifyNewColName(newName, cols):
    cnt = 0
    res = newName
    while res in cols:
        cnt += 1
        res = newName + "_" + str(cnt)
    return res


if __name__ == "__main__":
    pearson_correlation([1, 2, 3], [2, 3, 1])
    print(count_2factors(["F", "M", "F", "F", "M", "M"],
                         ["D", "M", "W", "D", 'D', 'M']))
