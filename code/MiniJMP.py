import zh_i18n  # 中文字体配置（必须最先导入）
from tkinter import Frame, Menu, BOTH, Toplevel, END, Tk, PhotoImage
from PIL import Image, ImageTk
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
from qc_dialog import GRRDialog, CpkDialog, CpkSubDialog, TIDialog, GRR_Nested_Dialog
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
        filemenuitems = {'01新建项目': {'cmd': self.new_file},
                         '02打开项目': {'cmd': self.load_file},
                         '04保存': {'cmd': self.save_file},
                         '05另存为': {'cmd': self.save_as_file},
                         '06sep': '',
                         '07导入CSV': {'cmd': self.import_csv},
                         '10导入Excel': {'cmd': self.load_excel},
                         '10导出CSV': {'cmd': lambda: self._call('doExport')},
                         '11sep': '',
                         '12退出': {'cmd': self.quit}}

        self.file_menu = self.createPulldown(
            self.menu, filemenuitems, var=file_menu)
        self.menu.add_cascade(label='文件', menu=self.file_menu['var'])

        editmenuitems = {'01撤销 (Ctrl-Z)': {'cmd': self.undo},
                         '02重做': {'cmd': lambda: self._call('redo')},
                         '03无表头粘贴 (Ctrl-V)': {'cmd': lambda: self._call('paste')},
                         '04含表头粘贴': {'cmd': lambda: self._call('paste_header')},
                         '05复制表格': {'cmd': self.copyTable},
                         '06复制选中 (Ctrl-C)': {'cmd': lambda: self._call('copy')},
                         '07删除选中并上移': {'cmd': lambda: self._call('clearDataUp')},
                         '08清除选中 (DEL)': {'cmd': lambda: self._call('clearData')},
                         '13查找/替换 (Ctrl-F)': {'cmd': self.findText},
                         '20sep': 'ddddd',
                         '24首选项': {'cmd': self.currentTablePrefs}}
        self.edit_menu = self.createPulldown(self.menu, editmenuitems)
        self.menu.add_cascade(label='编辑', menu=self.edit_menu['var'])

        self.view_menu = {
            '01放大': {
                'cmd': lambda: self._call('zoomIn')}, '02缩小': {
                'cmd': lambda: self._call('zoomOut')}, '03自动换行': {
                'cmd': lambda: self._call('setWrap')}, '04sep': '', '05深色主题': {
                    'cmd': lambda: self._call(
                        'setTheme', name='dark')}, 
                        # '06Bold Theme': {'cmd': lambda: self._call(
                        #         'setTheme', name='bold')}, 
                                '07浅色主题': {
                                    'cmd': lambda: self._call(
                                        'setTheme', name='default')}, }
        self.view_menu = self.createPulldown(self.menu, self.view_menu)
        self.menu.add_cascade(label='视图', menu=self.view_menu['var'])

        self.data_menu = {
            '01创建分类变量': {'cmd': lambda: self._call('createCategorical')},
            '02应用函数': {'cmd': lambda: self._call('applyColumnFunction')},
            '03重采样/变换': {'cmd': lambda: self._call('applyTransformFunction')},
            '04值计数': {'cmd': lambda: self._call('valueCounts')},
            '05字符串操作': {'cmd': lambda: self._call('applyStringMethod')},
            '06日期/时间转换': {'cmd': lambda: self._call('convertDates')},
            '22筛选行': {'cmd': lambda: self._call('queryBar')},
            '32拆分数据列': {'cmd': lambda: self._call('splitColumn')},
            '33堆叠选中列': {'cmd': lambda: self._call('stackColumn')},
            '34排序所有列': {'cmd': lambda: self._call('sortAll')},
            '35排序选中列': {'cmd': lambda: self._call('sortSelected')},
            '42第1行复制为表头': {'cmd': lambda: self._call('row1ToHeader')},
            '30sep': '', '40sep': ''}
        self.data_menu = self.createPulldown(self.menu, self.data_menu)
        self.menu.add_cascade(label='数据', menu=self.data_menu['var'])

        self.table_menu = {
            #  '01Describe Table': {'cmd': self.describe},
            '02转换列名': {'cmd': lambda: self._call('convertColumnNames')},
            '03转换为数值': {'cmd': lambda: self._call('convertNumeric')},
            '04清理数据': {'cmd': lambda: self._call('cleanData')},
            '05查找重复': {'cmd': lambda: self._call('findDuplicates')},
            #  '06Correlation Matrix': {'cmd': lambda: self._call('corrMatrix')},
            #  '07Concatenate Tables': {'cmd': self.concat},
            '08表格转文本': {'cmd': lambda: self._call('showasText')},
            '09表格信息': {'cmd': lambda: self._call('showInfo')},
            '10sep': '',
            '11变换数值': {'cmd': lambda: self._call('transform')},
            '12分组-聚合': {'cmd': lambda: self._call('aggregate')},
            '13交叉表': {'cmd': lambda: self._call('crosstab')},
            '14合并表格': {'cmd': lambda: self._call('doCombine')},
            '15数据透视表': {'cmd': lambda: self._call('pivot')},
            '16表格重塑(Melt)': {'cmd': lambda: self._call('melt')},
            '17时间序列重采样': {'cmd': lambda: self._call('resample')}
        }
        self.table_menu = self.createPulldown(self.menu, self.table_menu)
        self.menu.add_cascade(label='工具', menu=self.table_menu['var'])

        self.stats_menu = {
            '01描述统计': {'cmd': self.describe},
            '02多变量描述统计': {'cmd': self.multi_describe},
            '04正态性检验': {'cmd': self.norm_test},
            '05置信区间': {'cmd': self.confidence_interval},
            '06分布拟合': {'cmd': self.fit_dist},
            '13相关分析': {'cmd': self.correlation},
            '16正交回归': {'cmd': self.ortho_fit},
            '14线性回归': {'cmd': self.linear_fit},
            '15残差图': {'cmd': self.resid},
            '17相关矩阵': {'cmd': self.multi_cor},
            '22单样本均值 t 检验': {'cmd': self.mean_1sample},
            '23单样本均值 Z 检验': {'cmd': self.mean_1sampleZ},
            '24单样本标准差检验': {'cmd': self.var_1sample},
            '25单比例检验': {'cmd': self.prop_1sample},
            '26双样本 t 检验': {'cmd': self.mean_2samples},
            '27配对 t 检验': {'cmd': self.paired_t},
            '28双比例检验': {'cmd': self.prop_2samples},
            '29多样本标准差检验': {'cmd': self.multi_var},
            '32单因素方差分析': {'cmd': self.anova_1way},
            #  '33Mean Comparison t': {'cmd': self.JMP_t_test},
            '34双因素方差分析': {'cmd': self.anova_2way},
            '42列联表与卡方检验': {'cmd': self.chi2table},
            '43比例卡方检验': {'cmd': self.chi2prop},
            '06sep': '', '20sep': '', '30sep': '', '40sep': ''}
        self.stats_menu = self.createPulldown(self.menu, self.stats_menu)
        self.menu.add_cascade(label='统计', menu=self.stats_menu['var'])

        # ================= DOE 菜单（对标 Minitab） =================
        self.doe_menu = {
            '01创建因子设计': {'cmd': self.doe_factorial},
            '02创建响应曲面设计': {'cmd': self.doe_rsm},
            '03创建混料设计': {'cmd': self.doe_mixture},
            '04创建田口设计': {'cmd': self.doe_taguchi},
            '05创建最优设计': {'cmd': self.doe_optimal},
            '06sep': '',
            '10分析因子设计': {'cmd': self.doe_analyze_fact},
            '11分析响应曲面': {'cmd': self.doe_analyze_rsm},
            '12分析混料设计': {'cmd': self.doe_analyze_mix},
            '13分析田口设计': {'cmd': self.doe_analyze_tag},
            '20sep': '',
            '21因子图': {'cmd': self.doe_plots},
            '22等值线/曲面图': {'cmd': self.doe_contour},
            '23响应优化器': {'cmd': self.doe_optimizer},
            '30sep': ''}
        self.doe_menu = self.createPulldown(self.menu, self.doe_menu)
        self.menu.add_cascade(label='DOE', menu=self.doe_menu['var'])
        # ============================================================

        self.quality_menu = {
            '01交叉量具 R&R': {'cmd': self.grr},
            '02嵌套量具 R&R': {'cmd': self.grr_nst},
            '07过程能力 (Cpk)': {'cmd': self.cpk},
            '08分组过程能力 (Cpk)': {'cmd': self.cpksub},
            '22公差区间': {'cmd': self.ti_norm},
            '32控制图 I/MR': {'cmd': self.cChartIMR},
            '33控制图 I': {'cmd': self.cChartI},
            '34控制图 MR': {'cmd': self.cChartMR},
            '35控制图 xBar/R': {'cmd': self.cChartXBR},
            '36控制图 xBar/S': {'cmd': self.cChartXBS},
            '42控制图 NP': {'cmd': self.cChartNP},
            '43控制图 P': {'cmd': self.cChartP},
            '44控制图 C': {'cmd': self.cChartC},
            '45控制图 U': {'cmd': self.cChartU},
            '06sep': '', '20sep': '', '30sep': '', '40sep': ''}
        self.quality_menu = self.createPulldown(self.menu, self.quality_menu)
        self.menu.add_cascade(label='质量', menu=self.quality_menu['var'])

        self.plots_menu = {
            '01绘图向导（旧版）': {'cmd': self.plot_selected},
            '53保存图表': {'cmd': self.addPlot},
            '54清除图表': {'cmd': self.updatePlotsMenu},
            '55PDF报告': {'cmd': self.pdfReport},
            '12直方图与分布拟合': {'cmd': self.singleHisto},
            '13分组直方图': {'cmd': self.multiHisto},
            '14二维直方图': {'cmd': self.xyHisto},
            '15多Y箱线图': {'cmd': self.singleBox},
            '16分组箱线图': {'cmd': self.multiBox},
            '18分组计数图': {'cmd': self.countPlot},
            '20分组线图': {'cmd': self.linePlot},
            '22分组点图': {'cmd': self.dotPlot},
            '30sep': '',
            '32概率分布图': {'cmd': self.distDPPlot},
            '33概率图比较': {'cmd': self.dist2XPlot},
            '02sep': '', '50sep': '', '60sep': ''}
        self.plots_menu = self.createPulldown(self.menu, self.plots_menu)
        self.menu.add_cascade(label='图表', menu=self.plots_menu['var'])
        self.plot_menu_orig_len = len(self.plots_menu)

        self.debug_menu = {
            '01打印数据框': {'cmd': self.printDF},
            '06sep': ''}
        self.debug_menu = self.createPulldown(self.menu, self.debug_menu)
        self.menu.add_cascade(label='调试', menu=self.debug_menu['var'])

        self.help_menu = {'01在线帮助': {'cmd': self.online_documentation},
                          '02查看错误日志': {'cmd': self.showErrorLog},
                          '03关于': {'cmd': self.about}}
        self.help_menu = self.createPulldown(self.menu, self.help_menu)
        self.menu.add_cascade(label='帮助', menu=self.help_menu['var'])

        self.main.config(menu=self.menu)
        return

    def update_title(self):
        self.pickle_fname = self.table.filename
        if self.pickle_fname is not None:
            file_name_with_extension = os.path.basename(self.pickle_fname)
            self.main.title(file_name_with_extension + " - Minijmp")
        else:
            self.main.title("未命名 - Minijmp")
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

    # ================= DOE 菜单方法（懒加载，加快启动） =================
    def _doe_dialog(self, dlg_name, title):
        import doe.dialogs as _doe_dlgs
        Dlg = getattr(_doe_dlgs, dlg_name)
        _ = Dlg(self.table, app=self, df=self.table.model.df, title=title)
        return

    def doe_factorial(self):
        self._doe_dialog('FactorialDesignDialog', '创建因子设计')
        return

    def doe_rsm(self):
        self._doe_dialog('RSMDesignDialog', '创建响应曲面设计')
        return

    def doe_mixture(self):
        self._doe_dialog('MixtureDesignDialog', '创建混料设计')
        return

    def doe_taguchi(self):
        self._doe_dialog('TaguchiDesignDialog', '创建田口设计')
        return

    def doe_optimal(self):
        self._doe_dialog('OptimalDesignDialog', '创建最优设计')
        return

    def doe_analyze_fact(self):
        self._doe_dialog('AnalyzeFactorialDialog', '分析因子设计')
        return

    def doe_analyze_rsm(self):
        self._doe_dialog('AnalyzeRSMDialog', '分析响应曲面')
        return

    def doe_analyze_mix(self):
        self._doe_dialog('AnalyzeMixtureDialog', '分析混料设计')
        return

    def doe_analyze_tag(self):
        self._doe_dialog('AnalyzeTaguchiDialog', '分析田口设计')
        return

    def doe_plots(self):
        self._doe_dialog('FactorialPlotsDialog', '因子图')
        return

    def doe_contour(self):
        self._doe_dialog('ContourSurfaceDialog', '等值线/曲面图')
        return

    def doe_optimizer(self):
        self._doe_dialog('ResponseOptimizerDialog', '响应优化器')
        return
    # ===================================================

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
            title='One sample Std Dev test')
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
            title='Mutli-sample Std Dev Test')
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
            title='Crossed Gage R&R')
        return

    def grr_nst(self):
        _ = GRR_Nested_Dialog(
            self.table, app=self,
            df=self.table.model.df,
            title='Nested Gage R&R')
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
    img = Image.open("icon.png")
    icon = ImageTk.PhotoImage(img)
    #  icon = PhotoImage(file="icon.png")
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
