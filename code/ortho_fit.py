import numpy as np
from utilities import norm_test
from scipy.stats import norm


def orthogonal_fit(x, y, error_ratio=1.0, alpha=0.05,
                   print_port=print, print_out=True):
    """
    Perform orthogonal fit with unequal variances.

    Parameters:
    x, y: arrays of data points
    error_ratio: ratio of error variances (var_y / var_x)
    Ratio here is the ratio of measurement variance not the
    data variance itself. So setting the ratio is 1 as default

    Returns:
    slope, intercept
    and the CI of them
    All the results are same to Minitab 20
    slope and int have same 3~4 digits with JMP, CIs are different w/JMP
    """
    print = print_port
    x_mean = np.mean(x)
    y_mean = np.mean(y)

    x_centered = x - x_mean
    y_centered = y - y_mean

    n = len(x)
    Sxx = np.sum(x_centered**2) / (n - 1)
    Syy = np.sum(y_centered**2) / (n - 1)
    Sxy = np.sum(x_centered * y_centered) / (n - 1)

    # Modified slope calculation incorporating error_ratio
    w = error_ratio
    b1 = slope = ((Syy - w * Sxx) + np.sqrt((Syy - w * Sxx)
                                            ** 2 + 4 * w * Sxy**2)) / (2 * Sxy)

    b0 = intercept = y_mean - slope * x_mean

# Confidence Intervals
#   Source: https://support.minitab.com/en-us/minitab/help-and-how-to/statistical-modeling/regression/how-to/orthogonal-regression/methods-and-formulas/methods-and-formulas/
# The code below replicated the minitab math,
# the confidence interval outputs are not same to JMP but MiniTab 20

    var_u = (Syy + w * Sxx - ((Syy - w * Sxx)**2 + 4 * w * Sxy**2)**.5) / 2 / w
    #  var_e = w * var_u
    # above noted as est. delta ^2 u and est. delta ^2 e
    if Sxy == 0 and Syy < w * Sxx:
        var_u = Syy / w

    var_xx = (((Syy - w * Sxx)**2 + 4 * w * Sxy**2)
              ** .5 - (Syy - w * Sxx)) / 2 / w
    if Sxy == 0 and Syy < w * Sxx:
        var_xx = Sxx - Syy / w

    Svv = (n - 1) * (w + slope**2) * var_u / (n - 2)

    v_slope = (var_xx * Svv + var_u * Svv - slope **
               2 * var_u**2) / (n - 1) / var_xx**2

    z = norm.ppf(1 - alpha / 2)
    slope_l = slope - z * (v_slope)**.5
    slope_u = slope + z * (v_slope)**.5

    v_int = Svv / n + x_mean**2 * v_slope
    int_l = intercept - z * (v_int)**.5
    int_u = intercept + z * (v_int)**.5

    ######### Fitted values ############
    x_est = [(w * xt + (yt - b0) * b1) / (b1 * b1 + w)
             for xt, yt in zip(x, y)]
    y_est = [b0 + b1 * xt for xt in x_est]
    # Residuals
    vt_est = [yt - b0 - xt * b1 for xt, yt in zip(x, y)]
    ######### Std. Residuals
    std_vt_est = [vt / ((w + b1 * b1) * var_u)**.5
                  for vt in vt_est]
    # Normalitiy of the residuals
    ntest_resid = norm_test(vt_est)
#     ntest_st_resid=norm_test(std_vt_est)
# They are propotionally same values

    if print_out:
        print("\n---- Orthogonal Regression alpha = %.3f ----" % alpha)
        print("Error Variance Ratio %.3f" % w)
        print("Slope %.3f CI(%.3f, %.3f)" % (b1, slope_l, slope_u))
        print("Intercept %.3f CI(%.3f, %.3f)" % (b0, int_l, int_u))
        print("Normality of Residuals")
        print("Shaprio-Wilk p %.3f\tAnderson Darling p %.3f" % (
            ntest_resid["shapiro p"], ntest_resid["AD p"]))

    return {"slope": slope, "intercept": intercept,
            "slope_l": slope_l, "slope_u": slope_u,
            "int_l": int_l, "int_u": int_u,
            "Fitted Y": y_est, "Fitted X": x_est,
            "Residuals": vt_est, "St Resid": std_vt_est,
            "Normal test Resid": ntest_resid}
