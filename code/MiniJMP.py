from tkinter import Frame, Menu, BOTH, Toplevel, END, Tk, PhotoImage
import pickle
import os
import platform
import time
###############################
from pandastable_local import config, plotting
# ####### Own Module ###########
from modified_app import Minijmp_pre
from modified_table import MTable as Table
from plots import plot_viewer
from txt_output import txt_viewer
from fit_dialog import LinearFitDialog, CorrelationDialog, OrthoFitDialog, ResidDialog, MCorDialog
from basic_dialogs import DescribeDialog, NormTestDialog, CIDialog, MultiDescribeDialog, FitDistDialog
from sample_test_dialog import Mean1SampleDialog, Mean1SampleZDialog, Var1SampleDialog, Mean2SampleDialog, PairedTDialog, MultiVarDialog, Prop1SDialog, Prop2SDialog
from anova_dialog import Anova1WayDialog, TtestDialog, Anova2WayDialog
from chi2_dialog import Chi2TableDialog, Chi2PropDialog
from qc_dialog import GRRDialog, CpkDialog, CpkSubDialog, TIDialog
from ctrlchart_dialog import IMRDialog, IDialog, MRDialog, XBRDialog, XBSDialog, NPDialog, PDialog, CDialog, UDialog
from sb_hist_dialog import singleHistoDialog, multiHistoDialog, xyHistoDialog
from sb_box_dialog import singleBoxDialog, multiBoxDialog
from sb_misc_dialog import countPlotDialog, linePlotDialog, dotPlotDialog
from dist_plot_dialog import displayProbDialog, displayProb2xDialog


class Minijmp(Minijmp_pre):
    """Basic test frame for the table"""

    def __init__(self, parent=None):
        self.parent = parent
        Frame.__init__(self)
        self.main = self.master
        self.main.geometry('600x400+50+100')
        #  self.main.title('Untitled - Minijmp')

        # Get platform into a variable
        self.currplatform = platform.system()
        self.setConfigDir()
        if not hasattr(self, 'defaultsavedir'):
            self.defaultsavedir = os.path.join(os.path.expanduser('~'))
        self.loadAppOptions()
        # start logging
        self.start_logging()

        f = Frame(self.main)
        f.pack(fill=BOTH, expand=1)
        self.table = Table(f, showtoolbar=False, showstatusbar=True,
                           enable_menus=True)
        options = {'colheadercolor': 'green', 'floatprecision': 3,
                   'rowheaderfgcolor': 'black', 'rowheaderbgcolor': 'gray'}
        config.apply_options(options, self.table)
        self.table.show()
        self.createMenuBar()
        self.setStyles()
        self.clipboarddf = None
        self.projopen = False
        self.plots = dict()
        self.table.tOut = None

        self.main.protocol('WM_DELETE_WINDOW', self.quit)
        self.main.lift()
        self.pickle_fname = None
        self.update_title()
        return

    def createMenuBar(self):
        """Create the menu bar for the application. """

        self.menu = Menu(self.main)
        file_menu = Menu(self.menu, tearoff=0)
        # add recent first
        #  self.createRecentMenu(file_menu)
        filemenuitems = {'01New Project': {'cmd': self.new_file},
                         '02Open Project': {'cmd': self.load_file},
                         '04Save': {'cmd': self.save_file},
                         '05Save As': {'cmd': self.save_as_file},
                         '06sep': '',
                         '07Import CSV': {'cmd': self.import_csv},
                         '10Import Excel': {'cmd': self.load_excel},
                         '10Export CSV': {'cmd': lambda: self._call('doExport')},
                         '11sep': '',
                         '12Quit': {'cmd': self.quit}}

        self.file_menu = self.createPulldown(
            self.menu, filemenuitems, var=file_menu)
        self.menu.add_cascade(label='File', menu=self.file_menu['var'])

        editmenuitems = {'01Undo (C-Z)': {'cmd': self.undo},
                         '02Redo': {'cmd': lambda: self._call('redo')},
                         '03Paste w/o header (C-V)': {'cmd': lambda: self._call('paste')},
                         '04Paste w/ header': {'cmd': lambda: self._call('paste_header')},
                         '05Copy Table': {'cmd': self.copyTable},
                         '06Copy Selected (C-C)': {'cmd': lambda: self._call('copy')},
                         '07Del selected & move up': {'cmd': lambda: self._call('clearDataUp')},
                         '08Clear Selected (DEL)': {'cmd': lambda: self._call('clearData')},
                         '13Find/Replace (C-F)': {'cmd': self.findText},
                         '20sep': 'ddddd',
                         '24Preferences': {'cmd': self.currentTablePrefs}}
        self.edit_menu = self.createPulldown(self.menu, editmenuitems)
        self.menu.add_cascade(label='Edit', menu=self.edit_menu['var'])

        self.view_menu = {
            '01Zoom In': {
                'cmd': lambda: self._call('zoomIn')}, '02Zoom Out': {
                'cmd': lambda: self._call('zoomOut')}, '03Wrap Columns': {
                'cmd': lambda: self._call('setWrap')}, '04sep': '', '05Dark Theme': {
                    'cmd': lambda: self._call(
                        'setTheme', name='dark')}, '06Bold Theme': {
                            'cmd': lambda: self._call(
                                'setTheme', name='bold')}, '07Default Theme': {
                                    'cmd': lambda: self._call(
                                        'setTheme', name='default')}, }
        self.view_menu = self.createPulldown(self.menu, self.view_menu)
        self.menu.add_cascade(label='View', menu=self.view_menu['var'])

        self.data_menu = {
            '01Create Categorical': {'cmd': lambda: self._call('createCategorical')},
            '02Apply Function': {'cmd': lambda: self._call('applyColumnFunction')},
            '03Resample/Transform': {'cmd': lambda: self._call('applyTransformFunction')},
            '04Value Counts': {'cmd': lambda: self._call('valueCounts')},
            '05String Operation': {'cmd': lambda: self._call('applyStringMethod')},
            '06Date/Time Conversion': {'cmd': lambda: self._call('convertDates')},
            '22Filter Rows': {'cmd': lambda: self._call('queryBar')},
            '32Split Data Column': {'cmd': lambda: self._call('splitColumn')},
            '33Stack Selected Columns': {'cmd': lambda: self._call('stackColumn')},
            '34Sort All Columns': {'cmd': lambda: self._call('sortAll')},
            '35Sort Selected Colunms': {'cmd': lambda: self._call('sortSelected')},
            '42Copy Row 1 to Headers': {'cmd': lambda: self._call('row1ToHeader')},
            '30sep': '', '40sep': ''}
        self.data_menu = self.createPulldown(self.menu, self.data_menu)
        self.menu.add_cascade(label='Data', menu=self.data_menu['var'])

        self.table_menu = {
            #  '01Describe Table': {'cmd': self.describe},
            '02Convert Column Names': {'cmd': lambda: self._call('convertColumnNames')},
            '03Convert Numeric': {'cmd': lambda: self._call('convertNumeric')},
            '04Clean Data': {'cmd': lambda: self._call('cleanData')},
            '05Find Duplicates': {'cmd': lambda: self._call('findDuplicates')},
            #  '06Correlation Matrix': {'cmd': lambda: self._call('corrMatrix')},
            #  '07Concatenate Tables': {'cmd': self.concat},
            '08Table to Text': {'cmd': lambda: self._call('showasText')},
            '09Table Info': {'cmd': lambda: self._call('showInfo')},
            '10sep': '',
            '11Transform Values': {'cmd': lambda: self._call('transform')},
            '12Group-Aggregate': {'cmd': lambda: self._call('aggregate')},
            '13Cross Tabulation': {'cmd': lambda: self._call('crosstab')},
            '14Merge/Concat Tables': {'cmd': lambda: self._call('doCombine')},
            '15Pivot Table': {'cmd': lambda: self._call('pivot')},
            '16Melt Table': {'cmd': lambda: self._call('melt')},
            '17Time Series Resampling': {'cmd': lambda: self._call('resample')}
        }
        self.table_menu = self.createPulldown(self.menu, self.table_menu)
        self.menu.add_cascade(label='Tools', menu=self.table_menu['var'])

        self.stats_menu = {
            '01Describe': {'cmd': self.describe},
            '02Describe MutliVar': {'cmd': self.multi_describe},
            '04Normality': {'cmd': self.norm_test},
            '05Confidence Intervals': {'cmd': self.confidence_interval},
            '06Fit Distributions': {'cmd': self.fit_dist},
            '13Correlation': {'cmd': self.correlation},
            '16Orthogonal Regression': {'cmd': self.ortho_fit},
            '14Linear Regression': {'cmd': self.linear_fit},
            '15Residual Plots': {'cmd': self.resid},
            '17Correlation Matrix': {'cmd': self.multi_cor},
            '22One Sample Mean t-test': {'cmd': self.mean_1sample},
            '23One Sample Mean Z-test': {'cmd': self.mean_1sampleZ},
            '24One Sample Stdev': {'cmd': self.var_1sample},
            '25One Proportion Test': {'cmd': self.prop_1sample},
            '26Two Samples t-test': {'cmd': self.mean_2samples},
            '27Paired t-test': {'cmd': self.paired_t},
            '28Two Proportions Test': {'cmd': self.prop_2samples},
            '29Multi-Sample Stdev Test': {'cmd': self.multi_var},
            '32One-Way ANOVA': {'cmd': self.anova_1way},
            #  '33Mean Comparison t': {'cmd': self.JMP_t_test},
            '34Two-Way ANOVA': {'cmd': self.anova_2way},
            '42Contingency table & Chi2': {'cmd': self.chi2table},
            '43Proportion Chi Square': {'cmd': self.chi2prop},
            '06sep': '', '20sep': '', '30sep': '', '40sep': ''}
        self.stats_menu = self.createPulldown(self.menu, self.stats_menu)
        self.menu.add_cascade(label='Stats', menu=self.stats_menu['var'])

        self.quality_menu = {
            '01Gauge R&R Balanced': {'cmd': self.grr},
            '07Process Capability (Cpk)': {'cmd': self.cpk},
            '08Cpk with Subgroups': {'cmd': self.cpksub},
            '22Tolerance Interval': {'cmd': self.ti_norm},
            '32Control Chart I/MR': {'cmd': self.cChartIMR},
            '33Control Chart I': {'cmd': self.cChartI},
            '34Control Chart MR': {'cmd': self.cChartMR},
            '35Control Chart xBar/R': {'cmd': self.cChartXBR},
            '36Control Chart xBar/S': {'cmd': self.cChartXBS},
            '42Control Chart NP': {'cmd': self.cChartNP},
            '43Control Chart P': {'cmd': self.cChartP},
            '44Control Chart C': {'cmd': self.cChartC},
            '45Control Chart U': {'cmd': self.cChartU},
            '06sep': '', '20sep': '', '30sep': '', '40sep': ''}
        self.quality_menu = self.createPulldown(self.menu, self.quality_menu)
        self.menu.add_cascade(label='Quality', menu=self.quality_menu['var'])

        self.plots_menu = {
            '01Plot Wizard (Legacy)': {'cmd': self.plot_selected},
            '53Store plot': {'cmd': self.addPlot},
            '54Clear plots': {'cmd': self.updatePlotsMenu},
            '55PDF report': {'cmd': self.pdfReport},
            '12Histogram & Dist. Fit': {'cmd': self.singleHisto},
            '13Histogram w/ Groups': {'cmd': self.multiHisto},
            '14Histogram 2D': {'cmd': self.xyHisto},
            '15Box Plot Multiple Y': {'cmd': self.singleBox},
            '16Box Plot w/ Groups': {'cmd': self.multiBox},
            '18Count Plot w/ Grps': {'cmd': self.countPlot},
            '20Line Plot w/ Grps': {'cmd': self.linePlot},
            '22Dot Plot w/ Groups': {'cmd': self.dotPlot},
            '30sep': '',
            '32Display Probability': {'cmd': self.distDPPlot},
            '33Prob. Plot Compare': {'cmd': self.dist2XPlot},
            '02sep': '', '50sep': '', '60sep': ''}
        self.plots_menu = self.createPulldown(self.menu, self.plots_menu)
        self.menu.add_cascade(label='Plots', menu=self.plots_menu['var'])
        self.plot_menu_orig_len = len(self.plots_menu)

        self.debug_menu = {
            '01Print DF': {'cmd': self.printDF},
            '06sep': ''}
        self.debug_menu = self.createPulldown(self.menu, self.debug_menu)
        self.menu.add_cascade(label='Debug', menu=self.debug_menu['var'])

        self.help_menu = {'01Online Help': {'cmd': self.online_documentation},
                          '02View Error Log': {'cmd': self.showErrorLog},
                          '03About': {'cmd': self.about}}
        self.help_menu = self.createPulldown(self.menu, self.help_menu)
        self.menu.add_cascade(label='Help', menu=self.help_menu['var'])

        self.main.config(menu=self.menu)
        return

    def update_title(self):
        self.pickle_fname = self.table.filename
        if self.pickle_fname is not None:
            file_name_with_extension = os.path.basename(self.pickle_fname)
            self.main.title(file_name_with_extension + " - Minijmp")
        else:
            self.main.title("Untitled - Minijmp")
        return

    def new_file(self):
        self._call('new')
        self.update_title()
        return

    def load_file(self):
        self._call('load')
        self.update_title()
        return

    def save_file(self):
        if self.pickle_fname is None:
            self.save_as_file()
        else:
            self._call('save')
        return

    def save_as_file(self):
        self._call('saveAs')
        self.update_title()
        return

    def import_csv(self):
        self._call('importCSV')
        self.update_title()
        return

    def load_excel(self):
        self._call('loadExcel')
        self.update_title()
        return

    def printDF(self):
        print(self.table.model.df)
        return

    def getCurrentTable(self):
        return self.table

    def addPlot(self):
        """Store the current plot so it can be re-loaded"""

        #  name = self.getCurrentSheet()
        #  table = self.sheets[name]
        table = self.getCurrentTable()
        fig = table.pf.fig
        t = time.strftime("%H:%M:%S")
        label = t
        # dump and reload the figure to get a new object
        p = pickle.dumps(fig)
        fig = pickle.loads(p)
        self.plots[label] = fig

        def func(label):
            fig = self.plots[label]
            win = Toplevel()
            win.title(label)
            plotting.addFigure(win, fig)

        menu = self.plots_menu['var']
        menu.add_command(label=label, command=lambda: func(label))
        return

    def updatePlotsMenu(self, clear=True):
        """Clear stored plots"""

        if clear:
            self.plots = {}
        menu = self.plots_menu['var']
        menu.delete(self.plot_menu_orig_len - 1, menu.index(END))
        return

    def plot_selected(self):
        if hasattr(self.table, 'pf') and self.table.pf is not None:
            self.addPlot()
            self.table.pf.close()
        self._call('plotSelected')
        return

    def showPlotViewer(self, parent=None, figsize=(10, 7), save_last=True):
        """Create plot frame"""

        if hasattr(self.table, 'pf') and self.table.pf is not None:
            if save_last:
                self.addPlot()
            self.table.pf.close()

        self.table.pf = plot_viewer(
            table=self.table,
            parent=parent,
            figsize=figsize)
        if hasattr(self.table, 'child') and self.table.child is not None:
            self.table.child.pf = self.table.pf
        return self.table.pf

    def print(self, txt, end="\n"):
        if self.table.tOut is None:
            self.tOut = txt_viewer(table=self.table)
        self.tOut.add_txt(txt + end)
        self.tOut.to_end()
        return

    def linear_fit(self):

        _ = LinearFitDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Linear Regression')
        return

    def correlation(self):

        _ = CorrelationDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Correlation')
        return

    def ortho_fit(self):

        _ = OrthoFitDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Orthogonal Regression')
        return

    def describe(self):
        _ = DescribeDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Stats Summary')
        return

    def multi_describe(self):
        _ = MultiDescribeDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Stats Summary Multi Datasets')
        return

    def norm_test(self):
        _ = NormTestDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Normality Test')
        return

    def resid(self):
        _ = ResidDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Residual Plots')
        return

    def confidence_interval(self):
        _ = CIDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Confidence Intervals')
        return

    def multi_cor(self):
        _ = MCorDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Multi Column Correlation')
        return

    def mean_1sample(self):
        _ = Mean1SampleDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='One sample mean t-test')
        return

    def mean_1sampleZ(self):
        _ = Mean1SampleZDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='One sample mean Z-test')
        return

    def var_1sample(self):
        _ = Var1SampleDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='One sample Stdev test')
        return

    def mean_2samples(self):
        _ = Mean2SampleDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Two samples t-test')
        return

    def paired_t(self):
        _ = PairedTDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Paired t-test')
        return

    def multi_var(self):
        _ = MultiVarDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Mutli-sample Stdev Test')
        return

    def prop_1sample(self):
        _ = Prop1SDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='One Proportion Test')
        return

    def prop_2samples(self):
        _ = Prop2SDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Two Proportions Test')
        return

    def anova_1way(self):
        _ = Anova1WayDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='One-Way ANOVA')
        return

    def JMP_t_test(self):
        _ = TtestDialog(
            self.table, app=self,
            df=self.table.model.df,
            title="Mean Comparison Student's t")
        return

    def anova_2way(self):
        _ = Anova2WayDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Two-Way ANOVA')
        return

    def chi2table(self):
        _ = Chi2TableDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Contingency Table and Chi SQ Test')
        return

    def chi2prop(self):
        _ = Chi2PropDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Propabilities Chi SQ Test')
        return

    def grr(self):
        _ = GRRDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Guage R&R')
        return

    def cpk(self):
        _ = CpkDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Process Capability')
        return

    def cpksub(self):
        _ = CpkSubDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Process Capability with Subgroups')
        return

    def ti_norm(self):
        _ = TIDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Normal Dist TI')
        return

    def cChartIMR(self):
        _ = IMRDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Control Chart I/MR')
        return

    def cChartI(self):
        _ = IDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Control Chart I')
        return

    def cChartMR(self):
        _ = MRDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Control Chart MR')
        return

    def cChartXBR(self):
        _ = XBRDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Control Chart X Bar/R')
        return

    def cChartXBS(self):
        _ = XBSDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Control Chart X Bar/S')
        return

    def cChartNP(self):
        _ = NPDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Control Chart NP')
        return

    def cChartP(self):
        _ = PDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Control Chart P')
        return

    def cChartC(self):
        _ = CDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Control Chart C')
        return

    def cChartU(self):
        _ = UDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Control Chart U')
        return

    def fit_dist(self):
        _ = FitDistDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Fit Distributions')
        return

    def singleHisto(self):
        _ = singleHistoDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Histogram + Distribution Fit')
        return

    def multiHisto(self):
        _ = multiHistoDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Histogram with Groups')
        return

    def xyHisto(self):
        _ = xyHistoDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='2D Histogram')
        return

    def singleBox(self):
        _ = singleBoxDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Box Plot')
        return

    def multiBox(self):
        _ = multiBoxDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Box Plot with Groups')
        return

    def countPlot(self):
        _ = countPlotDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Count Plot with Groups')
        return

    def linePlot(self):
        _ = linePlotDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Line Plot with Groups')
        return

    def dotPlot(self):
        _ = dotPlotDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Dot Plot with Groups')
        return

    def distDPPlot(self):
        _ = displayProbDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Distribution Plot')
        return

    def dist2XPlot(self):
        _ = displayProb2xDialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Distribution Plot Compare')
        return


def main():
    # Create the main window
    root = Tk()
    icon = PhotoImage(file="icon.png")
    root.iconphoto(True, icon)

    # Create an instance of the custom frame
    _ = Minijmp(root)

    # Run the application
    root.mainloop()
    return


if __name__ == "__main__":
    main()

#  if __name__ == "__main__":
#      app = Minijmp()
#      # launch the app
#      app.mainloop()
