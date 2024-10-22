import seaborn as sb
#  import numpy as np
from matplotlib import pyplot as plt
########## Own Modules ###########
from utilities import add_Y_refs


def count_plot(xlabel=None, y_max=None, y_min=None, grid=False,
               palette=None,
               ax_margin=0.1, ax=None, ylabel=None,
               show_y_ref_label=False,
               y_ref=None, **kwargs):

    if ax is None:
        fig, ax = plt.subplots()

    sb.countplot(ax=ax, zorder=3,
                 palette=palette, **kwargs)
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


def dot_plot(xlabel=None, y_max=None, y_min=None, grid=False,
             palette=None,
             ax_margin=0.1, ax=None, ylabel=None,
             show_y_ref_label=False,
             y_ref=None, **kwargs):

    if ax is None:
        fig, ax = plt.subplots()

    sb.scatterplot(ax=ax, zorder=3,
                   palette=palette, **kwargs)
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


def line_plot(xlabel=None, y_max=None, y_min=None, grid=False,
              palette=None,
              ax_margin=0.1, ax=None, ylabel=None,
              show_y_ref_label=False,
              y_ref=None, **kwargs):

    if ax is None:
        fig, ax = plt.subplots()

    sb.lineplot(ax=ax, zorder=3,
                palette=palette, **kwargs)
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