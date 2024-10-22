from seaborn import stripplot
import matplotlib.pyplot as plt
import pandas as pd


def create_inset_grid(ax, n):
    # Calculate the size of each inset subplot
    inset_size = 1.0 / n  # Size of each subplot as a fraction of the main Axes
    inset_axes = []  # 2D list to store inset Axes

    for j in range(n):
        # Calculate the position of each inset subplot
        x0 = j * inset_size
        #  y0 = 1 - (i + 1) * inset_size
        inset_ax = ax.inset_axes(
            [x0, 0, inset_size, 1], transform=ax.transAxes)

        #  Example plot for each inset
        #  x = np.linspace(0, 10, 100)
        #  inset_ax.plot(x, np.sin(x + i + j), label=f'Inset {i*n + j + 1}')
        #  inset_ax.set_title(f'Inset {i*n + j + 1}', fontsize=8)
        #  inset_ax.set_xticks([])
        #  inset_ax.set_yticks([])

        # Append the inset Axes to the row list
        #  row_axes.append(inset_ax)
        inset_axes.append(inset_ax)

    # Append the row of Axes to the 2D list

    return inset_axes


def grr_plot(y=None, part=None, op=None,
             ax=None, ylabel="Y"):

    def subplot(df, ax, title=""):
        stripplot(data=df, x="Part", y="Y", jitter=False, ax=ax)
        ax.set_title(title)
        return

    dt = {"Y": list(y), "Part": list(part)}
    if op is not None:
        dt["OP"] = list(op)
    df = pd.DataFrame(dt)

    if ax is None:  # or fig is None:
        # n - 1, n - 1)  # , sharex=True, sharey=True)
        _, ax = plt.subplots(1)

    if op is None:
        subplot(df, ax)
    else:
        top = max(y) + (max(y) - min(y)) / 10
        bottom = min(y) - (max(y) - min(y)) / 10
        ax.axis('off')
        n = len(list(df["OP"].unique()))
        axs = create_inset_grid(ax, n)
        for subax, operator in zip(axs, list(df["OP"].unique())):
            subplot(df[df["OP"] == operator], subax, title="OP=" + str(operator))
            subax.set_ylim(bottom, top)
            subax.tick_params(axis='y', which='both', left=False, labelleft=False)
            subax.grid(axis='y')
            subax.set_ylabel("")
        axs[0].set_ylabel(ylabel)
        axs[0].tick_params(axis='y', which='both', left=True, labelleft=True)

    return
