import statistics as stat
import numpy as np
from prettytable import PrettyTable as PT
########### Own Modules ########
from utilities import quantiles, is_number


def describe(data, print_port=print,
             print_out=False, percentiles=[100, 99.5, 97.5, 90, 75, 50,
                                           25, 10, 2.5, 0.5, 0]):
    data = [float(i) for i in data if is_number(i)]
    mean = stat.mean(data)
    N = len(data)
    if N < 2:
        return
    R = max(data) - min(data)
    mode = stat.mode(data)
    N_mode = len([i for i in data if i == mode])
    median = stat.median(data)
    qnt = quantiles(data, percentiles=[25, 75])
    IQR = max(qnt) - min(qnt)
    qnt2 = quantiles(data, percentiles=percentiles)

    std = stat.stdev(data)
    SEM = std / N**.5
    var = stat.variance(data)
    coefvar = 100 * std / mean
    try:
        kurt = N * (N + 1) / (N - 1) / (N - 2) / (N - 3) * sum(
            ((i - mean) / std)**4 for i in data
        ) - 3 * (N - 1)**2 / (N - 2) / (N - 3)
    except BaseException:
        kurt = np.nan
    try:
        skew = N / (N - 1) / (N - 2) * sum(((i - mean) / std)**3
                                           for i in data)
    except BaseException:
        skew = np.nan

    if print_out:
        print = print_port
        print("\n---- Descriptive Statistics ----")
        t = PT()
        #  t.field_names = ["Item", "Value", "Item", "Value", "Item", "Value"]
        t.add_row(["N", "%d" %
                   N, "Mean", "%.3f" %
                   mean, "StDev", "%.3f" %
                   std])
        t.add_row(["SE Mean", "%.3f" % SEM, "Variance", "%.3f" % var,
                   "CoefVar", "%.2f" % coefvar])
        t.add_row(["Sum", "%.3f" % (sum(data)), "Min", "%.3f" % min(data),
                   "Q1", "%.3f" % qnt[0]])
        t.add_row(["Median", "%.3f" % median, "Q3", "%.3f" % qnt[1],
                   "Max", "%.3f" % max(data)])
        t.add_row(["Range", "%.3f" %
                   R, "IQR", "%.3f" %
                   IQR, "Mode", "%.3f" %
                   mode])
        t.add_row(["N for Mode", "%d" % N_mode, "Skewness", "%.3f" % skew,
                   "Kurtosis", "%.3f" % kurt])
        print(t.get_string(header=False))
        print("\nQuantiles")
        t = PT()
        t.field_names = ["Percentiles", "Values"]
        for i, j in zip(percentiles, qnt2):
            t.add_row(["%.2f%%" % i, "%.3f" % j])
        print(str(t))

    return {
        "N": N,
        "mean": mean,
        "stdev": std,
        "SEM": SEM,
        "var": var,
        "coefvar": coefvar,
        "sum": sum(data),
        "min": min(data),
        "max": max(data),
        "Q1": qnt[0],
        "Q3": qnt[1],
        "median": median,
        "range": R,
        "IQR": IQR,
        "mode": mode,
        "n mode": N_mode,
        "skew": skew,
        "kurt": kurt,
        "quantiles": qnt2,
        "Mean": mean,
        "Standard Deviation": std,
        "Variance": var,
        "Maximum": max(data),
        "Median": median,
        "First Quartile": qnt[0],
        "Third Quartile": qnt[1],
        "SE of Mean": SEM,
        "Coefficient of Variation": coefvar,
        "Sum": sum(data),
        "Minimum": min(data),
        "Range": R,
        "Skewness": skew,
        "Kurtosis": kurt,
        "Mode": mode,
        "N of Mode": N_mode,
        "Interquartile Range": IQR}


if __name__ == "__main__":
    describe([1, 1, 2, 2, 3, 4, 1], print_out=True)
    describe([1, 1, 2, 3, 3, 3, 3, 4, 1, 1, 1, 1, 1, 1], print_out=True)
    from scipy.stats import skew
    print(skew([1, 1, 2, 3, 3, 3, 3, 4, 1, 1, 1, 1, 1, 1]))
