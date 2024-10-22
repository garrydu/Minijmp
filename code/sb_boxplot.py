import seaborn as sb
#  import numpy as np
from matplotlib import pyplot as plt
########## Own Modules ###########
from utilities import add_Y_refs


def single_boxplot(xlabel=None, y_max=None, y_min=None, grid=False,
                   ax_margin=0.1, ax=None, ylabel=None, fliersize=None,
                   whis=1.5, fill_color='lightblue', dot_color='k',
                   show_y_ref_label=False, gap=.05, hide_box=False,
                   y_ref=None, add_swarm=False, **kwargs):

    if ax is None:
        fig, ax = plt.subplots()
    if not hide_box:
        sb.boxplot(ax=ax, zorder=2, whis=whis,
                   fliersize=0 if add_swarm else fliersize,
                   gap=gap, color=fill_color, **kwargs)
    if add_swarm:
        sb.swarmplot(ax=ax, zorder=3, color=dot_color, **kwargs)
    if y_max is not None:
        ax.set_ylim(top=y_max)
    if y_min is not None:
        ax.set_ylim(bottom=y_min)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if grid:
        ax.grid(grid, zorder=1)
    add_Y_refs(ax, y_values=y_ref, label=show_y_ref_label)
    return


def multi_boxplot(xlabel=None, y_max=None, y_min=None, grid=False,
                  swarm_dodge=True, swarm_size=1, palette=None,
                  ax_margin=0.1, ax=None, ylabel=None, fliersize=None,
                  whis=1.5, fill_color='lightblue', dot_color='k',
                  show_y_ref_label=False, gap=.05, hide_box=False,
                  y_ref=None, add_swarm=False, **kwargs):

    if ax is None:
        fig, ax = plt.subplots()
    if not hide_box:
        sb.boxplot(ax=ax, zorder=2, whis=whis,  # fill=(not add_swarm),
                   palette=palette,
                   fliersize=0 if add_swarm else fliersize,
                   gap=gap, color=fill_color, **kwargs)
    if add_swarm:
        sb.swarmplot(ax=ax, zorder=3, color=dot_color,
                     palette=palette if hide_box else None,
                     dodge=swarm_dodge, size=swarm_size, **kwargs)
    if y_max is not None:
        ax.set_ylim(top=y_max)
    if y_min is not None:
        ax.set_ylim(bottom=y_min)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if grid:
        ax.grid(grid, zorder=1)
    add_Y_refs(ax, y_values=y_ref, label=show_y_ref_label)
    return
