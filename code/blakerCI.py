"""
The code is translated from BlakerCI module in R except for the p-value function.
https://cran.r-project.org/src/contrib/BlakerCI_1.0-6.tar.gz

"""

from scipy import stats
import numpy as np
from scipy.stats import beta


def qbeta(p, shape1, shape2, ncp=0, lower_tail=True, log_p=False):
    if ncp != 0:
        raise NotImplementedError("Non-central beta distribution is not implemented in SciPy")

    if log_p:
        p = np.exp(p)

    if not lower_tail:
        p = 1 - p

    return beta.ppf(p, shape1, shape2)


def pbinom(q, size, prob, lower_tail=True, log_p=False):
    """
    Cumulative distribution function for the binomial distribution.

    Parameters:
    q (int or array-like): Quantile(s)
    size (int): Number of trials
    prob (float): Probability of success on each trial
    lower_tail (bool): If True (default), probabilities are P[X ≤ x], otherwise P[X > x]
    log_p (bool): If True, probabilities are given as log(p)

    Returns:
    float or array-like: Cumulative probabilities
    """
    if lower_tail:
        result = stats.binom.cdf(q, size, prob)
    else:
        result = stats.binom.sf(q, size, prob)

    if log_p:
        return np.log(result)
    else:
        return result


def qbinom(p, size, prob, lower_tail=True, log_p=False):
    """
    Quantile function for the binomial distribution.

    Parameters:
    p (float or array-like): Probability or probabilities
    size (int): Number of trials
    prob (float): Probability of success on each trial
    lower_tail (bool): If True (default), probabilities are P[X ≤ x], otherwise P[X > x]
    log_p (bool): If True, probabilities are given as log(p)

    Returns:
    int or array-like: Quantile(s)
    """
    if log_p:
        p = np.exp(p)

    if not lower_tail:
        p = 1 - p

    return stats.binom.ppf(p, size, prob)


def binom_blaker_lower_limit(x, n, level, tol=1e-7, maxiter=10000):
    if x <= 0:
        return 0
    if x > 0:
        alpha = 1 - level
        # Clopper-Pearson limit (CPL)
        lower = qbeta(alpha / 2, x, n - x + 1)
        p1 = pbinom(x - 1, n, lower, lower_tail=False)
        q1_cp = qbinom(p1, n, lower) - 1
        upper = x / n
        iter_count = 0
        while upper - lower >= tol:
            iter_count += 1
            if iter_count > maxiter:
                print(f"Warning: Tolerance limit of {tol} not attained after {maxiter} iterations for n = {n}, x = {x}")
                break
            mid = (lower + upper) / 2
            p1 = pbinom(x - 1, n, mid, lower_tail=False)
            # Blaker's limit is below the midpoint if either
            # (i)  acceptability at mid > alpha (NEW!! orig: >=), or
            # (ii) acceptability function has a discontinuity between
            #      the midpoint and CPL (first test).
            if p1 >= pbinom(q1_cp + 1, n, mid) or p1 + pbinom(q1_cp, n, mid) > alpha:
                upper = mid
            else:
                lower = mid
        return lower


def binom_blaker_limits(x, n, level=0.95, tol=1e-10, **kwargs):
    """
    Calculate Blaker's confidence interval for binomial proportion.

    Parameters:
    x (int): Number of successes
    n (int): Number of trials
    level (float): Confidence level (default 0.95)
    tol (float): Tolerance for numerical calculations (default 1e-10)
    **kwargs: Additional arguments to pass to binom_blaker_lower_limit

    Returns:
    tuple: (lower limit, upper limit) of the confidence interval
    """
    if n < 1 or x < 0 or x > n:
        raise ValueError(f"Parameters n = {n}, x = {x} wrong!")
    if level <= 0 or level >= 1:
        raise ValueError(f"Confidence level {level} out of (0, 1)!")
    if tol <= 0:
        raise ValueError(f"Numerical tolerance {tol} nonpositive!")

    lower = binom_blaker_lower_limit(x, n, level, tol, **kwargs)
    upper = 1 - binom_blaker_lower_limit(n - x, n, level, tol, **kwargs)

    return (lower, upper)


def binom_blaker_upper_limit(x, n, level, tol, **kwargs):
    return 1 - binom_blaker_lower_limit(n - x, n, level, tol, **kwargs)


def binom_blaker_p(x, n, p0, tol=1e-6, **kwargs):
    """
    Calculate the p-value for a binomial test using Blaker's method.

    This function implements Blaker's method for calculating the p-value
    of a binomial test with null hypothesis H0: p = p0 vs. H1: p != p0.

    Parameters:
    x (int): Number of successes
    n (int): Number of trials
    p0 (float): Hypothesized probability of success under the null hypothesis
    tol (float): Tolerance for numerical calculations (default 1e-6)
    **kwargs: Additional arguments to pass to binom_blaker_lower_limit or binom_blaker_upper_limit

    Returns:
    float: The p-value for the test

    Raises:
    ValueError: If input parameters are invalid

    Note:
    This implementation uses a binary search algorithm to find the p-value.
    """
    if n < 1 or x < 0 or x > n:
        raise ValueError(f"Parameters n = {n}, x = {x} wrong!")
    if p0 <= 0 or p0 >= 1:
        raise ValueError(f"Hypothesized probability p0 = {p0} out of (0, 1)!")
    if tol <= 0:
        raise ValueError(f"Numerical tolerance {tol} nonpositive!")

    p = x / n
    if p == p0:
        return 1
    if p < p0:
        sign = -1
        func = binom_blaker_upper_limit
    else:
        sign = 1
        func = binom_blaker_lower_limit

    left = 1e-10
    right = 1 - left
    while abs(right - left) > tol:
        mid = (right + left) / 2
        res = func(x, n, 1 - mid, tol, **kwargs)
        if sign * (res - p0) > 0:
            right = mid
        else:
            left = mid
    return left


if __name__ == "__main__":
    print(binom_blaker_p(9, 250, 0.03))
    print(binom_blaker_p(9, 250, 0.073))
