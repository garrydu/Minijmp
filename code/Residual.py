import numpy as np
from scipy.stats import probplot
import matplotlib.pyplot as plt
####### Own Modules ###########
from cpk_plot import hist_norm
from linear_plot import fit_plot
from control_chart import x_plot
from linear_fit import linear_fit
from utilities import norm_test


def linear_fit_resid_test(x, y, print_out=False, show_plot=False,
                          axs=None, filename=None, print_port=print):
    #  pearson_correlation(x, y, print_out=False)
    res = linear_fit(x, y, print_out=False)

    data = res["Residual"]
    y_est = np.array(x) * res["slope"] + res["intercept"]
    return resid_test(data, y_est, print_out=print_out,
                      print_port=print_port, axs=axs,
                      show_plot=show_plot, filename=filename)


def resid_test(data, y_est, print_out=False, show_plot=False,
               axs=None, print_port=print, filename=None):

    res = norm_test(data, print_out=print_out, print_port=print_port)

    if axs is None:
        fig, axs = plt.subplots(2, 2, dpi=200, figsize=(16, 9))
    else:
        fig = None

    probplot(data, dist="norm", plot=axs[1][1])
    axs[1][1].set_xlabel('Theoretical quantiles')
    axs[1][1].set_ylabel('Residual Values')
    axs[1][1].set_title("")

    hist_norm(data, ax=axs[1][0], xlabel="Residual")

    fit_plot(y_est, data, linear=True, print_out=False, ax=axs[0][1],
             xlabel="Fitted Value", ylabel="Residual")

    x_plot(data, ax=axs[0][0], xlabel="Observation Order", ylabel1="Residual",one_chart=True)

    if fig is not None:
        fig.suptitle("SW p-value = %.3f   AD p-value = %.3f" % (
            res["shapiro p"], res["AD p"]), y=0.95)

    if show_plot:
        plt.show()

    if filename is not None:
        fname = str(filename) + '.png'
        plt.savefig(
            fname,
            dpi=200,
            format='png')

    return res


if __name__ == "__main__":
    N = 30
    x = np.random.normal(0, 10, N)
    y = x + np.random.normal(0, 10, N)
