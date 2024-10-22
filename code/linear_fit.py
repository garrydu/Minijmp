import statistics as stat
from scipy.stats import f as f_dist
from scipy.stats import t as t_dist
from prettytable import PrettyTable as PT
######## Own Module ###########
from utilities import norm_test


def linear_fit(x, y, print_out=True, print_port=print):
    print = print_port
    # Source:
    # https://support.minitab.com/en-us/minitab/help-and-how-to/statistical-modeling/regression/how-to/fitted-line-plot/methods-and-formulas/methods-and-formulas/
    x_u = stat.mean(x)
    y_u = stat.mean(y)
    n = len(x)
    if n != len(y):
        return

    # Get b1 as slope and b0 as intercept
    b1 = sum([(xi - x_u) * (yi - y_u) for xi, yi in zip(x, y)]) / sum(
        [(xi - x_u)**2 for xi in x])
    b0 = y_u - b1 * x_u

    # Fitted y response
    y_est = [b0 + b1 * xi for xi in x]
    y_est_u = stat.mean(y_est)

    # Residual
    e = [yi - ye for yi, ye in zip(y, y_est)]
    # Normality test
    ntest_e = norm_test(e)

    # sum of square regression
    SSR = sum([(ye - y_u)**2 for ye in y_est])
    # Sum of Square Error
    SSE = sum([(yi - ye)**2 for yi, ye in zip(y, y_est)])
    # Sum of Square Total
    SST = sum([(yi - y_u)**2 for yi in y])

    # Mean Square of the error
    # MSE= SSE / DF_error DF_error=n-p-1
    # where p is the num of coefficient excluding constant
    MSE = SSE / (n - 1 - 1)
#      the standard error of the estimate (s):
    S = MSE**.5
    R_sq = 1 - SSE / SST

    # R-sq is 1 - MSE/(SST/(DF total))
    # DF total is n-1
    R_sq_adj = 1 - MSE / (SST / (n - 1))

    # Adj mean square regression
    MSR = SSR / 1
    # 1 is the dfn two terms in the fit two-1=1

    # Adj Mean square total
    MST = SST / (n - 1)

    # F value
    if MSE != 0:
        F_reg = MSR / MSE
        p_reg = 1 - f_dist.cdf(F_reg, dfn=1, dfd=n - 2)
    else:
        F_reg = -1
        p_reg = 0

#     If p < 0.05 (or your chosen significance level):
# Reject the null hypothesis
# Conclude that your model provides a statistically significantly
# better fit than the intercept-only model ( which is a horizontal
# line at y mean)
# At least one of your independent variables is significantly
# related to the dependent variable
# The p-value is used to test the hypothesis that there is no
# relationship between the predictor and the response. Or,
# stated differently, the p-value is used to test the hypothesis
# that the true slope coefficient is zero.

    # Lack of fit
    # c is number of distinct x values
    c = len(set(x))
    # DF Pure Error
    DFPE = n - c
    # DF lack of fit
    DFLF = c - 2

    # SSPE = Sum of Squares for Pure Error
#     SSPE = Σ Σ (yij - y̅i)²
# Where yij is the jth y value for the ith x value,
# and y̅i is the mean y for the ith x value.
    SSPE = sum([sum([(y[i] - stat.mean([y[i]
                                        for i in range(n) if x[i] == uni_x]))**2
                     for i in range(n) if x[i] == uni_x
                     ]) for uni_x in set(x)])

    SSLF = SSE - SSPE

    # Mean square of lack of fit
    MSLF = SSLF / DFLF

    if DFPE > 0 and SSPE != 0:
        # Mean square of Pure Error
        MSPE = SSPE / DFPE

        F_lack = MSLF / MSPE
    #     If p-value < significance level (typically 0.05):
    # Reject the null hypothesis. There is evidence of lack of fit,
    # suggesting the linear model may not be adequate. A more complex
    # model (e.g., polynomial) might be more appropriate.
        p_lack = 1 - f_dist.cdf(F_lack, dfn=DFLF, dfd=DFPE)
    else:
        MSPE = F_lack = p_lack = -1

#     Calculate sum of squares for the saturated model (SSM):
# SSM = Σni(ȳi - ȳ)², where ȳi is the mean of each group and
# ni is the number of observations in each group.
    SSM = sum([sum([(y_u - stat.mean([y[i]
                                      for i in range(n) if x[i] == uni_x]))**2
                    for i in range(n) if x[i] == uni_x
                    ]) for uni_x in set(x)])

    max_r_sq = SSM / SST


# Calculate the standard error of the slope (SEb1):
# SEb1 = s / sqrt(Σ(x - x_bar^2)
# Calculate the standard error of the intercept (SEb0):
# SEb0 = s * sqrt((1/n) + (x_bar^2 / Σ(x - x̄x_bar²))
# Calculate t-ratios:
# For slope: t = b1 / SEb1
# For intercept: t = b0 / SEb0

    SEb1 = S / (sum([(xi - x_u)**2 for xi in x]))**.5
    SEb0 = S * (1 / n + x_u * x_u / sum([(xi - x_u)**2 for xi in x]))**.5

# The prob of the values are zero in truth
    if SEb1 != 0:
        slope_t = abs(b1 / SEb1)
        p_slope = (1 - t_dist.cdf(slope_t, n - 2)) * 2
    else:
        slope_t = -1
        p_slope = 0

    if SEb0 != 0:
        int_t = abs(b0 / SEb0)  # two tails test needs abs
        p_int = (1 - t_dist.cdf(int_t, n - 2)) * 2
    else:
        int_t = -1
        p_int = 1 if b0 == 0 else 0

    if print_out:
        print("\n---- Linear Fit ----")
        print("Summary of Fit")
        print(f"RSquare {R_sq:.3f}\t\t\tRSquare Adj {R_sq_adj:.3f}")
        print(
            f"Root Mean Square Error {S:.3f}\tMean of Response {y_est_u:.3f}")
        print("N = %d" % len(x))
        print("\nParameter Estimates")
        t = PT()
        t.field_names = ["Item", "Est.", "Std Error", "t Ratio", "Prob > |t|"]
        t.add_row(["Slope", "%.3f" %
                   b1, "%.3f" %
                   SEb1, "%.3f" %
                   slope_t, "%.3f" %
                   p_slope])
        t.add_row(["Intercept", "%.3f" %
                   b0, "%.3f" %
                   SEb0, "%.3f" %
                   int_t, "%.3f" %
                   p_int])
        print(str(t))
        #  print(f"Slope Est. {b1:.3f}\tStd Error {SEb1:.3f}")
        #  print(f"t ratio {slope_t:.3f}\tProb>|t| {p_slope:.3f}")
        #  print(f"Intercept Est. {b0:.3f}\tStd Error {SEb0:.3f}")
        #  print(f"t ratio {int_t:.3f}\tProb>|t| {p_int:.3f}")
        print("p values above are the probabilities of each term == 0.")
        print("\nAnalysis of Variances")
        t = PT()
        t.field_names = ["Item", "DF", "Sum of Sq.", "Mean Sq."]
        t.add_row(["Model", "1", "%.3f" % SSR, "%.3f" % MSR])
        t.add_row(["Error", "%d" % (n - 2), "%.3f" % SSE, "%.3f" % MSE])
        t.add_row(["Total", "%d" % (n - 1), "%.3f" % SST, " "])
        print(str(t))
        #  print(f"Model DF 1\tSum of Sq {SSR:.3f}\tMean Sq {MSR:.3f}")
        #  print("Error DF %d\tSum of Sq %.3f\tMean Sq %.3f" % (n - 2, SSE, MSE))
        #  print("Total DF %d\tSum of Sq %.3f" % (n - 1, SST))
        print(f"F Ratio {F_reg:.3f}\tProb > F {p_reg:.3f}")
        print("p value is the probability of slope == 0.")
        print("\nLack of Fit")
        t = PT()
        t.field_names = ["Item", "DF", "Sum of Sq.", "Mean Sq."]
        t.add_row(["Lack of fit", "%d" % DFLF, "%.3f" % SSLF, "%.3f" % MSLF])
        t.add_row(["Pure Error", "%d" % DFPE, "%.3f" % SSPE, "%.3f" % MSPE])
        t.add_row(["Total", "%d" % (n - 1), "%.3f" % SST, " "])
        print(str(t))

        #  print(
        #      f"Lack of Fit DF {DFLF:d}\tSum of Sq {SSLF:.3f}\tMean Sq {MSLF:.3f}")
        #  print(
        #      f"Pure Error DF {DFPE:d}\tSum of Sq {SSPE:.3f}\tMean Sq {MSPE:.3f}")
        #  print("Total Error is the Error in Variances Analysis.")
        print(
            f"F Ratio {F_lack:.3f}\tProb > F {p_lack:.3f}\tMax R Square {max_r_sq:.3f}")
        print("p value is the probability of the true relationship is linear.")
        #  print(f"Max R Square {max_r_sq:.3f}")
        print("\nNormality of Residuals")
        print("Shapiro-Wilk Statistics %.3f\tp-value %.3f" %
              (ntest_e["shapiro s"], ntest_e["shapiro p"]))
        print(
            "Anderson Darling Stats. %.3f\tp-value %.3f" %
            (ntest_e["AD s"], ntest_e["AD p"]))
        print("p values are the probabilities of true dist is normal.")

    return {"slope": b1, "intercept": b0,
            "R Square": R_sq, "R Square Adj": R_sq_adj,
            "MSE": MSE, "Mean of Response": y_est_u,
            "N": len(x), "DF reg": 1, "DF Error": n - 2,
            "DF Total": n - 1, "SSR": SSR, "SSE": SSE,
            "SST": SST, "MSR": MSR, "MSE": MSE,
            "F Reg": F_reg, "p reg": p_reg,
            "Root MSE": S, "DFPE": DFPE,
            "DFLF": DFLF, "SSPE": SSPE,
            "SSLF": SSLF, "MSPE": MSPE,
            "MSLF": MSLF, "F lack": F_lack,
            "p lack": p_lack, "Max R Square": max_r_sq,
            "Std Error Slope": SEb1,
            "Std Error Int.": SEb0,
            "t slope": slope_t, "t int.": int_t,
            "p slope": p_slope, "p int.": p_int,
            "Normal Test Resid": ntest_e,
            "MST": MST, "Residual": e}


if __name__ == "__main__":
    # From JMP body measure fore and Bicep
    waist = [
        85.0,
        90.5,
        80.5,
        91.5,
        92.0,
        101.0,
        76.0,
        84.0,
        74.0,
        76.0,
        80.0,
        86.0,
        82.0,
        82.0,
        95.5,
        81.0,
        76.0,
        84.0,
        88.0,
        82.0,
        96.0,
        99.5]
    bicep = [
        33.5,
        36.5,
        31.0,
        34.0,
        36.5,
        38.0,
        29.0,
        31.0,
        29.0,
        31.0,
        37.0,
        33.0,
        36.0,
        30.0,
        36.0,
        32.5,
        30.0,
        28.5,
        34.5,
        34.5,
        35.5,
        33.5]
    linear_fit(waist, bicep)
