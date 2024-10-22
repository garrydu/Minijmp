from pandastable_local.plotting import PlotViewer, addButton, addFigure
from pandastable_local import handlers, images
from matplotlib.figure import Figure
#  from tkinter.ttk import Frame
from tkinter import BOTH, Toplevel, VERTICAL, TOP, BOTTOM, LEFT, BooleanVar, Checkbutton, IntVar, Label, X, Entry, Frame
import os
from collections import OrderedDict


class plot_viewer(PlotViewer):
    def __init__(self, table, parent=None, showoptions=True, figsize=(10, 7)):

        self.parent = parent
        self.table = table
        if table is not None:
            self.table.pf = self  # opaque ref
        #self.mode = '2d'
        self.showoptions = showoptions
        self.multiviews = False
        if self.parent is not None:
            Frame.__init__(self, parent)
            self.main = self.master
        else:
            self.main = Toplevel()
            self.master = self.main
            self.main.title('Plot Viewer')
            self.main.protocol("WM_DELETE_WINDOW", self.close)
            g = '1000x750+120+0'
            self.main.geometry(g)
        self.orient = VERTICAL
        self.style = None
        self.figsize = figsize
        self.setupGUI()
        #  self.updateStyle()
        self.currentdir = os.path.expanduser('~')
        return

    def setupGUI(self):
        """Add GUI elements"""

        #import tkinter as tk
        #self.m = PanedWindow(self.main, orient=self.orient)
        self.m = Frame(self.main)
        self.m.pack(fill=BOTH, expand=1)
        # frame for figure
        self.plotfr = Frame(self.m)
        # add it to the panedwindow
        print(self.figsize)
        self.fig, self.canvas = addFigure(
            self.plotfr, figure=Figure(
                figsize=self.figsize, dpi=100, facecolor='white'))
        #  self.ax = self.fig.add_subplot(111)

        #self.m.add(self.plotfr, weight=12)
        self.plotfr.pack(side=TOP, fill=BOTH, expand=1)

        # frame for controls
        self.ctrlfr = Frame(self.main)
        #self.m.add(self.ctrlfr, weight=4)
        self.ctrlfr.pack(side=BOTTOM, fill=BOTH)

        # button frame
        bf = Frame(self.ctrlfr, padx=2)  # padding=2)
        bf.pack(side=TOP, fill=BOTH)

        side = LEFT
        addButton(bf, 'Save', self.savePlot, images.save(),
                  'save plot', side=side)

        # dicts to store global options, can be saved with projects
        self.globalvars = {}
        self.globalopts = OrderedDict({'dpi': 100})
        # , 'grid layout': False, '3D plot': False})
        from functools import partial
        for n in self.globalopts:
            val = self.globalopts[n]
            if isinstance(val, bool):
                v = self.globalvars[n] = BooleanVar()
                v.set(val)
                b = Checkbutton(
                    bf, text=n, variable=v, command=partial(
                        self.setGlobalOption, n))
            else:
                v = self.globalvars[n] = IntVar()
                v.set(val)
                Label(bf, text=n).pack(side=LEFT, fill=X, padx=2)
                b = Entry(bf, textvariable=v, width=5)
                v.trace("w", partial(self.setGlobalOption, n))
            b.pack(side=LEFT, padx=2)
        dr = handlers.DragHandler(self)
        dr.connect()
        return

    def close(self):
        """Close the window"""
        print('plot close')
        try:
            self.table.pf = None
            self.animateopts.stop()
        except BaseException:
            pass
        self.main.destroy()
        return
