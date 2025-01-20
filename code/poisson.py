from scipy.stats import poisson as ps


def poisson(mu, x=None, pvalue=None, print_out=False, print_port=print, ax=None, grid=True, color='black'):
    rv = ps(mu)
    res = dict()

    mean, var, skew, kurt = rv.stats(moments='mvsk')
    stdev = var**.5
    res["mean"], res["var"], res["skew"], res["kurt"], res["stdev"] = \
        mean, var, skew, kurt, stdev

    if print_out:
        print = print_port
        print("mean = %.2f\tvariance = %.2f\tSD=%.2f" % (mean, var, stdev))
        print(
            "skewness coefficient = %.2f\tkurtosis coefficient = %.2f" %
            (skew, kurt))

    if x is not None:
        x = int(x)
        res["px"] = rv.pmf(x)
        res["left_acc_p"] = rv.cdf(x)
        res["right_acc_p"] = 1 - rv.cdf(x - 1)
        if res["left_acc_p"] < res["right_acc_p"]:
            right_x = rv.ppf(1 - res["left_acc_p"]) + 1
            right_acc_p = 1 - rv.cdf(right_x - 1)
            left_acc_p, left_x = res["left_acc_p"], x
        else:
            #  left_acc_p, left_x = acc_p(0, x + 1, 1, res["right_acc_p"])
            right_acc_p, right_x = res["right_acc_p"], x
            left_x = rv.ppf(right_acc_p)
            if rv.cdf(left_x) > right_acc_p:
                left_x -= 1
            left_acc_p = rv.cdf(left_x)

        res["equal_tail"] = {
            "x_left": left_x, "x_right": right_x,
            "acc_p_left": left_acc_p, "acc_p_right": right_acc_p
        }

        if print_out:
            print("Prob at x = %d is %.3f." % (x, res["px"]))
            print("Prob 0 to x including x total is %.3f." % res["left_acc_p"])
            print(
                "Prob x to inf including x total is %.3f." %
                res["right_acc_p"])
            print(
                "Equal tail at two sides \nLeft at %.0f, acc. prob is %.3f." %
                (left_x, left_acc_p))
            print("Right at %.0f, acc. prob is %.3f." % (right_x, right_acc_p))

    elif pvalue is not None:
        res["x_left"] = rv.ppf(pvalue)
        if rv.cdf(res["x_left"]) > pvalue:
            res["x_left"] -= 1
        res["left_acc_p"] = rv.cdf(res["x_left"])
        res["x_right"] = rv.ppf(1 - pvalue) + 1
        res["right_acc_p"] = 1 - rv.cdf(res["x_right"] - 1)
        left_x = rv.ppf(pvalue / 2)
        if rv.cdf(left_x) > pvalue / 2:
            left_x -= 1
        left_acc_p = rv.cdf(left_x)
        right_x = rv.ppf(1 - pvalue / 2) + 1
        right_acc_p = 1 - rv.cdf(right_x - 1)
        res["equal_tail"] = {
            "x_left": left_x, "x_right": right_x,
            "acc_p_left": left_acc_p, "acc_p_right": right_acc_p
        }

        if print_out:
            print("P value = %.3f" % pvalue)
            print("Prob 0 to x = %d including x total is %.3f." %
                  (res["x_left"], res["left_acc_p"]))
            print("Prob x = %d to inf including x total is %.3f." %
                  (res["x_right"], res["right_acc_p"]))
            print(
                "Equal tail at two sides \nLeft at %d, acc. prob is %.3f." %
                (left_x, left_acc_p))
            print("Right at %d, acc. prob is %.3f." % (right_x, right_acc_p))

    #  res["pmf"] = [rv.pmf(i) for i in range(n + 1)]
    if ax is not None:
        def triangle(x_input, ax, color, offset, xlist, ylist, label):
            x, y = [], []
            for xx in x_input:
                if xx not in xlist:
                    continue
                yy = ylist[xlist.index(xx)] + offset
                x.append(xx)
                y.append(yy)
            if len(x) == 0:
                return
            ax.plot(x, y, marker='v', markersize=10, markerfacecolor='none', markeredgecolor=color, label=label,
                    color='none')

        x, y = [], []
        max_pmf = rv.pmf(int(mu))
        for xx in range(int(mu), -1, -1):
            pmf = rv.pmf(xx)
            if pmf > max_pmf / 100:
                x.append(xx)
                y.append(pmf)
            else:
                break
        for xx in range(int(mu) + 1, (int(mu) + 1) * 100):
            pmf = rv.pmf(xx)
            if pmf > max_pmf / 100:
                x.append(xx)
                y.append(pmf)
            else:
                break

        ax.bar(x, y, facecolor='none', edgecolor=color, linewidth=1)
        ymax = max(y) * 1.1
        ylim = ax.get_ylim()
        if ymax > ylim[1]:
            ax.set_ylim(top=ymax)
        ax.set_xlabel("X")
        ax.set_ylabel("Probability")
        ax.grid(grid)

        bottom, top = ax.get_ylim()
        offset = (top - bottom) / 50
        try:
            triangle([res["equal_tail"]["x_right"], res["equal_tail"]["x_left"]], ax, "red", offset, x, y, "Equal Tail")
        except BaseException:
            pass
        try:
            triangle([res["x_left"]], ax, "blue", offset * 2, x, y, "Left Tail")
            triangle([res["x_right"]], ax, "green", offset * 2, x, y, "Right Tail")
        except BaseException:
            pass
        ax.legend(loc='best', frameon=True)

        return res


if __name__ == "__main__":
    poisson(10, pvalue=0.05, print_out=True)
    poisson(0.01, pvalue=0.05, print_out=True)
    poisson(0.1, pvalue=0.05, print_out=True)
    poisson(0.1, x=4, print_out=True)
    poisson(200, x=30, print_out=True)
    poisson(200, x=180, print_out=True)
    poisson(200, pvalue=0.05, print_out=True)
    poisson(0.5, x=1, print_out=True)
