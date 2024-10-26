import numpy as np
from scipy import stats
from scipy.stats import rankdata


def spearman(x, y, print_out=False, print_port=print):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    spearman_result = stats.spearmanr(x, y)
    if print_out:
        print = print_port
        print("\n---- Spearman's rho Correlation ----")
        print("Spearman's rho correlation: " + "%.3f" % spearman_result.correlation)
        print("Spearman's rho p-value: " + "%.3f" % spearman_result.pvalue)
        print("H0: The population Spearman's rho = 0, which means no monotonic relationship between the two variables.")
    return {"cor": spearman_result.correlation, "p": spearman_result.pvalue}


def kendall(x, y, print_out=False, print_port=print):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    # Kendall
    kendall_result = stats.kendalltau(x, y)
    if print_out:
        print = print_port
        print("\n---- Kendall's tau Correlation ----")
        print("Kendall's tau: " + "%.3f" % kendall_result.correlation)
        print("Kendall's tau p-value: " + "%.3f" % kendall_result.pvalue)
        print("H0: The population Kendall's tau = 0, which means no monotonic association between the two variables.")
    return {"cor": kendall_result.correlation, "p": kendall_result.pvalue}


#  def pearson_correlation(x, y, alpha=0.05, print_out=True, print_port=print):

def hoeffd_example(X, Y):
    # This function was copy-pasted from https://github.com/Dicklesworthstone/hoeffdings_d_explainer/blob/main/README.md
    # Credit to this author.

    X, Y = np.array(X, dtype=float), np.array(Y, dtype=float)

    # # The 'average' ranking method assigns the average of the ranks that would have been assigned to all the tied values.
    R = rankdata(X, method='average')
    S = rankdata(Y, method='average')

    N = len(X)  # Total number of data points
    # Q is an array that will hold a special sum for each data point, which is crucial for Hoeffding's D computation.
    Q = np.zeros(N)
    # Loop through each data point to calculate its Q value.
    for i in range(N):
        # For each data point 'i', count how many points have both a lower height and weight rank (concordant pairs).
        Q[i] = 1 + sum(np.logical_and(R < R[i], S < S[i]))

        # Adjust Q[i] for ties: when both ranks are equal, it contributes partially (1/4) to the Q[i] value.
        # The "- 1" accounts for not including the point itself in its own comparison.
        Q[i] += (1 / 4) * (sum(np.logical_and(R == R[i], S == S[i])) - 1)

        # When only the height rank is tied but the weight rank is lower, it contributes half (1/2) to the Q[i] value.
        Q[i] += (1 / 2) * sum(np.logical_and(R == R[i], S < S[i]))

        # Similarly, when only the weight rank is tied but the height rank is lower, it also contributes half (1/2).
        Q[i] += (1 / 2) * sum(np.logical_and(R < R[i], S == S[i]))
    # Print the Q values for each data point, indicating the weighted count of points considered "lower" or "equal".
    #  print(f"Q values: {Q}")
    # Calculate intermediate sums required for Hoeffding's D formula:
    # D1: This sum leverages the Q values calculated earlier. Each Q value encapsulates information about how
    # a data point's ranks relate to others in both sequences, including concordance and adjustments for ties.
    # The term (Q - 1) * (Q - 2) for each data point quantifies the extent to which the ranks of this point
    # are concordant with others, adjusted for the expected concordance under independence.
    # Summing these terms across all data points (D1) aggregates this concordance information for the entire dataset.
    D1 = sum((Q - 1) * (Q - 2))
    # D2: This sum involves products of rank differences for each sequence, adjusted for ties. The term
    # (R - 1) * (R - 2) * (S - 1) * (S - 2) for each data point captures the interaction between the rank variances
    # within each sequence, providing a measure of how the joint rank distribution diverges from what would
    # be expected under independence due to the variability in ranks alone, without considering their pairing.
    # Summing these products across all data points (D2) gives a global assessment of this divergence.
    D2 = sum((R - 1) * (R - 2) * (S - 1) * (S - 2))
    # D3: This sum represents an interaction term that combines the insights from Q values with rank differences.
    # The term (R - 2) * (S - 2) * (Q - 1) for each data point considers the rank variances alongside the Q value,
    # capturing how individual data points' rank concordance/discordance contributes to the overall dependency measure,
    # adjusted for the expected values under independence. Summing these terms (D3) integrates these individual
    # contributions into a comprehensive interaction term for the dataset.
    D3 = sum((R - 2) * (S - 2) * (Q - 1))
    # The final computation of Hoeffding's D integrates D1, D2, and D3, along with normalization factors
    # that account for the sample size (N). The normalization ensures that Hoeffding's D is scaled appropriately,
    # allowing for meaningful comparison across datasets of different sizes. The formula incorporates these sums
    # and normalization factors in a way that balances the contributions of concordance, discordance, and rank variances,
    # resulting in a statistic that robustly measures the degree of association between the two sequences.
    D = 30 * ((N - 2) * (N - 3) * D1 + D2 - 2 * (N - 2) * D3) / (N * (N - 1) * (N - 2) * (N - 3) * (N - 4))
    # Return the computed Hoeffding's D value.
    return D


def phoeffd(D, n):
    # This code was rewritten from a R code: https://rdrr.io/cran/Hmisc/src/R/hoeffd.s
    # Yes it gives same values to R, but a little different from JMP pro 17.

    # Ensure inputs are floats
    d = float(D) / 30
    n = float(n)

    # Calculate b and z
    b = d + 1 / (36 * n)
    z = 0.5 * (np.pi ** 4) * n * b
    #  print(b, z)

    # Handle NaN values
    if np.isnan(z):
        z = 1e50  # Set to a large value if z is NaN

    # Define tabvals as in the R code
    tabvals = np.array([
        5297, 4918, 4565, 4236, 3930,
        3648, 3387, 3146, 2924, 2719,
        2530, 2355, 2194, 2045, 1908,
        1781, 1663, 1554, 1453, 1359,
        1273, 1192, 1117, 1047, 982,
        921, 864, 812, 762, 716,
        673, 633, 595, 560, 527,
        496, 467, 440, 414, 390,
        368, 347, 327, 308, 291,
        274, 259, 244, 230, 217,
        205, 194, 183, 173, 163,
        154, 145, 137, 130, 123,
        116, 110, 104, 98, 93,
        87, 83, 78, 74, 70,
        66, 63, 59, 56, 53,
        50, 47, 45, 42, 25,
        14, 8, 5, 3, 2,
        1
    ]) / 10000

    # Calculate P based on the conditions
    if z < 1.1 or z > 8.5:
        P = max(1e-8, min(1.0, np.exp(0.3885037 - (1.164879 * z))))
    else:
        # Interpolation for z in [1.1,8.5]
        x_values = np.concatenate((np.arange(1.1, 5.05, .05), np.arange(5.5, 8.55, .5)))

        # Interpolating using numpy's interpolation
        P = np.interp(z, x_values, tabvals)

    return P


def hoeffding(x, y, print_out=False, print_port=print):
    D = hoeffd_example(x, y)
    p = phoeffd(D, len(x))
    if print_out:
        print = print_port
        print("\n---- Hoeffding's D Correlation ----")
        print("Hoeffding's D: " + "%.3f" % D)
        print("Hoeffding's D p-value: " + "%.3f" % p)
        print("H0: The two variables are independent.")
        #  print("
    return {"cor": D, "p": p}


if __name__ == "__main__":
    l1 = [0.276054974090457, 0.0899289063522398, 0.231651196339091, 0.0330764279084449, 0.367658351155205, 0.130477153153308, 0.783413726366693, 0.667374723260036, 0.641938575216257, 3.61724714184063, 0.218655991783686, 0.945107232675843, 1.16028890958127, 0.839573829832848, 0.667927943621081, 0.497905771893942, 0.63186521899019, 1.2693032394988, 2.03622385034504, 2.31914810376975]
    l2 = [2.0, 1.0, 3.0, 1.0, 24.0, 5.0, 3.0, 10.0, 4.0, 3.0, 2.0, 12.0, 4.0, 3.0, 23.0, 1.0, 23.0, 2.0, 12.0, 3.0]
    spearman(l1, l2, print_out=True)
    kendall(l1, l2, print_out=True)
    hoeffding(l1, l2, print_out=True)
