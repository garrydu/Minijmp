from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
#### Own Modules ####
from binomial import binomial
from poisson import poisson


def cont_dist(dist=None, pvalue=None, x=None, print_out=True, plot_out=False,
              color='black',
              plot_tail=0.001, p=None, print_port=print, ax=None, **kwargs):

    if pvalue is None and p is not None:
        pvalue = p

    def process(rv, pvalue, x, print_out, print_port, ax, color):
        res = dict()

        mean, var, skew, kurt = rv.stats(moments='mvsk')
        stdev = var**.5
        res["mean"], res["var"], res["skew"], res["kurt"], res["stdev"] = \
            mean, var, skew, kurt, stdev

        if print_out:
            print = print_port
            print("mean = %.2f\tvariance = %.2f\tSD=%.2f" % (mean, var, stdev))
            print("skewness coefficient = %.2f\tkurtosis coefficient = %.2f\n" % (skew, kurt))

        if x is not None:
            res["px"] = rv.pdf(x)
            res["left_acc_p"] = rv.cdf(x)
            res["right_acc_p"] = 1 - rv.cdf(x)
            if res["left_acc_p"] < res["right_acc_p"]:
                right_acc_p, right_x = res["left_acc_p"], rv.ppf(1 - res["left_acc_p"])
                left_acc_p, left_x = res["left_acc_p"], x
            else:
                left_acc_p, left_x = res["right_acc_p"], rv.ppf(res["right_acc_p"])
                right_acc_p, right_x = res["right_acc_p"], x
            res["equal_tail"] = {
                "x_left": left_x, "x_right": right_x,
                "acc_p_left": left_acc_p, "acc_p_right": right_acc_p
            }

            if print_out:
                print("PDF at x = %.3f is %.3f." % (x, res["px"]))
                print("Left tail till x acc. prob. is %.3f." % res["left_acc_p"])
                print("Right tail from x acc. prob. is %.3f." % res["right_acc_p"])
                print("Equal tail at two sides \nLeft at %.3f, acc. prob is %.3f." % (
                    left_x, left_acc_p))
                print("Right at %.3f, acc. prob is %.3f." % (right_x, right_acc_p))

        elif pvalue is not None:
            res["left_acc_p"], res["x_left"] = pvalue, rv.ppf(pvalue)
            res["right_acc_p"], res["x_right"] = pvalue, rv.ppf(1 - pvalue)
            left_acc_p, left_x = pvalue / 2, rv.ppf(pvalue / 2)
            right_acc_p, right_x = pvalue / 2, rv.ppf(1 - pvalue / 2)
            res["equal_tail"] = {
                "x_left": left_x, "x_right": right_x,
                "acc_p_left": left_acc_p, "acc_p_right": right_acc_p
            }

            if print_out:
                print("P value = %.3f" % pvalue)
                print("Left tail till x = %.3f having p = %.3f." %
                      (res["x_left"], res["left_acc_p"]))
                print("Right tail from x = %.3f having p = %.3f." %
                      (res["x_right"], res["right_acc_p"]))
                print("Equal tail at two sides \nLeft at %.3f, acc. prob is %.3f." % (
                    left_x, left_acc_p))
                print("Right at %.3f, acc. prob is %.3f." % (right_x, right_acc_p))

        if plot_out:
            if ax is None:
                _, ax = plt.subplots(1, 1)
            left = rv.ppf(plot_tail)
            right = rv.ppf(1 - plot_tail)
            try:
                left = min(res["equal_tail"]["x_left"], left)
                right = max(res["equal_tail"]["x_right"], right)
            except BaseException:
                pass
            #  x = np.linspace(rv.ppf(plot_tail), rv.ppf(1 - plot_tail), 200)
            x = np.linspace(left, right, 200)
            y = rv.pdf(x)
            ax.plot(x, y, color=color)
            ymax = max(y) * 1.1
            ylim = ax.get_ylim()
            if ymax > ylim[1]:
                ax.set_ylim(top=ymax)
            ax.set_ylim(bottom=0)
            ax.set_xlabel("X")
            ax.set_ylabel("Density")
            if "equal_tail" in res:
                x = res["equal_tail"]["x_left"]
                ax.vlines(x, 0, rv.pdf(x), colors='r', linestyles='dashed',
                          label="Equal Tail")
                x = res["equal_tail"]["x_right"]
                ax.vlines(x, 0, rv.pdf(x), colors='r', linestyles='dashed')
                if "x_left" in res:
                    x = res["x_left"]
                    ax.vlines(x, 0, rv.pdf(x), colors='g', linestyles='dotted',
                              label="Left Tail")
                    x = res["x_right"]
                    ax.vlines(x, 0, rv.pdf(x), colors='blue', linestyles='dotted',
                              label="Right Tail")
                ax.legend(loc='best', frameon=False)

            #  plt.show()

        return res

    dist_s = dist.lower()[:3]

    if print_out:
        print = print_port
        print("\n---- " + dist + " ----")
        for key in kwargs:
            if key == "NA":
                continue
            print(key + ": %.3f" % kwargs[key])

    if dist_s == "nor":
        return process(stats.norm(kwargs["Mean"], kwargs["Standard deviation"]),
                       pvalue, x, print_out, print_port, ax, color)
    if dist_s == "chi":
        return process(stats.chi2(kwargs["Degrees of freedom"]),
                       pvalue, x, print_out, print_port, ax, color)
    if dist_s == "f":
        return process(stats.f(kwargs["Numerator degrees of freedom"], kwargs["Denominator degrees of freedom"]),
                       pvalue, x, print_out, print_port, ax, color)
    if dist.lower()[:4] == "logn":
        return process(stats.lognorm(kwargs["Scale"]),
                       pvalue, x, print_out, print_port, ax, color)
    if dist_s == "t":
        return process(stats.t(kwargs["Degrees of freedom"]),
                       pvalue, x, print_out, print_port, ax, color)

    if dist_s == "bin":
        return binomial(int(kwargs["Number of trials"]), kwargs["Event probability"],
                        pvalue=pvalue, x=x, print_out=print_out, print_port=print_port, ax=ax, color=color)

    if dist_s == "poi":
        return poisson(kwargs["Mean"],
                       pvalue=pvalue, x=x, print_out=print_out, print_port=print_port, ax=ax, color=color)
    return
