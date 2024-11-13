from scipy.stats import norm
import statistics as stats
from math import exp


def trimmed_mean(data):
    n = len(data)
    if n <= 5:
        return stats.mean(data)
    trim_portion = 1 / 2 / (n - 4)**.5
    num2trim = int(n * trim_portion)
    data_sorted = sorted(data.copy())
    return stats.mean(
        data_sorted[num2trim:-num2trim])


def ratio(alpha, se, n, negative=False):
    z_a2 = norm.ppf(1 - alpha / 2)
    c_a2 = n / (n - z_a2)
    sign = -1 if negative else 1
    return (c_a2 * exp(sign * c_a2 * z_a2 * se))**.5


def solution(r, se, n, negative=False):
    sign = -1 if negative else 1
    left, right = 0.00001, .99999
    while abs(right - left) > 0.00001:
        mid = (left + right) / 2
        res = -sign * (ratio(mid, se, n, negative=negative) - r)
        if res < 0:
            left = mid
        else:
            right = mid
    return left


def var_1sample(data, alpha=0.05, s0=None):
    n = len(data)
    std = stats.stdev(data)
    m = trimmed_mean(data)
    y = n / (n - 1) / (n - 1) * sum(((x - m) / std)**4 for x in data)
    se = ((y - (n - 3) / n) / (n - 1))**.5
    z_a2 = norm.ppf(1 - alpha / 2)
    if n <= z_a2:
        return None
    ll = std * ratio(alpha, se, n, negative=True)
    ul = std * ratio(alpha, se, n, negative=False)
    lb = std * ratio(alpha * 2, se, n, negative=True)
    ub = std * ratio(alpha * 2, se, n, negative=False)
    r = s0 / std
    if r > 1:
        p = solution(r, se, n, negative=False)
    else:
        p = solution(r, se, n, negative=True)

    return {"Bonett p": p,
            "Bonett CI": (ll, ul),
            #  "CI upper limit": ul,
            "One tail lower boundary": lb,
            "One tail upper boundary": ub}


if __name__ == "__main__":
    data = [0,
            0.05263,
            0.10526,
            0.15789,
            0.21053,
            0.26316,
            0.31579,
            0.36842,
            0.42105,
            0.47368,
            0.52632,
            0.57895,
            0.63158,
            0.68421,
            0.73684,
            0.78947,
            0.84211,
            0.89474,
            0.94737,
            1.00000
            ]
    print(var_1sample(data=data, s0=0.39))
