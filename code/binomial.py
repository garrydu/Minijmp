from scipy.stats import binom


def binomial(n, p, x=None, pvalue=None, print_out=False, print_port=print, ax=None, grid=True, color='black'):
    rv = binom(n, p)
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

    def acc_p(h, t, s, threshold):
        pp = 0
        for i in range(h, t, s):
            pp += rv.pmf(i)
            if pp > threshold:
                return pp - rv.pmf(i), i - s
        print(h, t, s, threshold, n, p, x)
        print(res["left_acc_p"], res["right_acc_p"])

    if x is not None:
        x = int(x)
        res["px"] = rv.pmf(x)
        res["left_acc_p"] = sum([rv.pmf(i) for i in range(x + 1)])
        res["right_acc_p"] = sum([rv.pmf(i) for i in range(x, n + 1)])
        if res["left_acc_p"] < res["right_acc_p"]:
            right_acc_p, right_x = acc_p(n, x - 1, -1, res["left_acc_p"])
            left_acc_p, left_x = res["left_acc_p"], x
        else:
            left_acc_p, left_x = acc_p(0, x + 1, 1, res["right_acc_p"])
            right_acc_p, right_x = res["right_acc_p"], x
        res["equal_tail"] = {
            "x_left": left_x, "x_right": right_x,
            "acc_p_left": left_acc_p, "acc_p_right": right_acc_p
        }
        prop_test_y = min(x, n - x)
        #  print(prop_test_y)
        res['not equal p'] = sum(rv.pmf(i) for i in range(prop_test_y + 1)) +\
            sum(rv.pmf(i) for i in range(n - prop_test_y, n + 1))

        if print_out:
            print("Prob at x = %d is %.3f." % (x, res["px"]))
            print("Prob 0 to x including x total is %.3f." % res["left_acc_p"])
            print(
                "Prob x to n including x total is %.3f." %
                res["right_acc_p"])
            print(
                "Equal tail at two sides \nLeft at %d, acc. prob is %.3f." %
                (left_x, left_acc_p))
            print("Right at %d, acc. prob is %.3f." % (right_x, right_acc_p))

    elif pvalue is not None:
        res["left_acc_p"], res["x_left"] = acc_p(0, n + 1, 1, pvalue)
        res["right_acc_p"], res["x_right"] = acc_p(n, -1, -1, pvalue)
        left_acc_p, left_x = acc_p(0, n + 1, 1, pvalue / 2)
        right_acc_p, right_x = acc_p(n, -1, -1, pvalue / 2)
        res["equal_tail"] = {
            "x_left": left_x, "x_right": right_x,
            "acc_p_left": left_acc_p, "acc_p_right": right_acc_p
        }

        if print_out:
            print("P value = %.3f" % pvalue)
            print("Prob 0 to x = %d including x total is %.3f." %
                  (res["x_left"], res["left_acc_p"]))
            print("Prob x = %d to n including x total is %.3f." %
                  (res["x_right"], res["right_acc_p"]))
            print(
                "Equal tail at two sides \nLeft at %d, acc. prob is %.3f." %
                (left_x, left_acc_p))
            print("Right at %d, acc. prob is %.3f." % (right_x, right_acc_p))

    res["pmf"] = [rv.pmf(i) for i in range(n + 1)]
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
        for xx, yy in zip(list(range(n + 1)), res["pmf"]):
            if yy > max(res["pmf"]) / 100:
                x.append(xx)
                y.append(yy)
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
        #  triangle(, ax, "red", offset, x, y, None)
        try:
            triangle([res["x_left"]], ax, "blue", offset * 2, x, y, "Left Tail")
            triangle([res["x_right"]], ax, "green", offset * 2, x, y, "Right Tail")
        except BaseException:
            pass
        ax.legend(loc='best', frameon=True)

    return res


if __name__ == "__main__":
    binomial(250, .073, x=9, print_out=True)
