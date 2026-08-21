# -*- coding: utf-8 -*-
# ============================================================
# 贡献者 / Contributors
#   胡志东 (Nico HU) <Hzd378747710@outlook.com>
#   - DOE 模块: GUI 对话框 (2026-08)
# ============================================================
"""DOE GUI 对话框模块
=========================================================
复刻 Minitab DOE 菜单的对话框：
  创建因子设计 / 创建响应曲面 / 创建混料 / 创建田口 / 创建最优设计
  分析因子设计 / 分析响应曲面 / 分析混料 / 分析田口
  因子图 / 等值线曲面图 / 响应优化器
遵循项目 Dialog 模式：继承 dialogs.Dialogs，实现 createWidgets + apply。
=========================================================
"""
from tkinter import ttk
import tkinter as tk
from tkinter import TOP, LEFT, X, BOTH
import numpy as np
import pandas as pd

from dialog import Dialogs
from .designs import (ff2n, full_factorial, frac_factorial, alias_table,
                      pb_design, dsd, ccd, box_behnken,
                      simplex_centroid, simplex_lattice, extreme_vertices,
                      mixture_process, taguchi_design, d_optimal_design,
                      factor_letters, make_doe_worksheet)
from .analyze import (factorial_analysis, rsm_analysis, mixture_analysis,
                      taguchi_analysis)
from . import plots_doe


# =====================================================================
# 工具：写回表格
# =====================================================================

def write_back(table, df):
    """把设计 DataFrame 写回当前表格（TableModel 机制）"""
    from pandastable_local.data import TableModel
    model = TableModel(dataframe=df)
    table.updateModel(model)
    table.redraw()
    return


def _names_input(k, var):
    """解析因子名输入（逗号分隔），返回列表或 None"""
    s = var.get().strip()
    if not s:
        return None
    names = [x.strip() for x in s.split(',') if x.strip()]
    if len(names) != k:
        return None
    return names


def _num_list(var):
    """解析逗号分隔数字列表"""
    s = var.get().strip()
    if not s:
        return []
    return [float(x.strip()) for x in s.split(',') if x.strip()]


# =====================================================================
# 一、创建因子设计（Minitab 风格：名称/低高/随机化/标准工作表）
# =====================================================================

class FactorialDesignDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='设计类型')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.dtype = tk.StringVar(value='2水平全因子')
        types = ['2水平全因子', '部分因子(2^(k-p))', 'Plackett-Burman 筛选', '确定性筛选(DSD)']
        for t in types:
            tk.Radiobutton(f, text=t, variable=self.dtype, value=t,
                           anchor='w').pack(side=TOP, fill=X)

        f = tk.LabelFrame(m, text='因子设置（逗号分隔，顺序对应）')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r1, text='因子名', width=8, anchor='w').pack(side=LEFT)
        self.fnamevar = tk.StringVar(value='A,B,C')
        tk.Entry(r1, textvariable=self.fnamevar).pack(side=LEFT, fill=X, expand=1)
        r2 = tk.Frame(f); r2.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r2, text='低水平', width=8, anchor='w').pack(side=LEFT)
        self.lowvar = tk.StringVar(value='-1,-1,-1')
        tk.Entry(r2, textvariable=self.lowvar).pack(side=LEFT, fill=X, expand=1)
        r3 = tk.Frame(f); r3.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r3, text='高水平', width=8, anchor='w').pack(side=LEFT)
        self.highvar = tk.StringVar(value='1,1,1')
        tk.Entry(r3, textvariable=self.highvar).pack(side=LEFT, fill=X, expand=1)

        f = tk.LabelFrame(m, text='设计选项')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r4 = tk.Frame(f); r4.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r4, text='部分阶数 p').pack(side=LEFT)
        self.pvar = tk.StringVar(value='1')
        tk.Entry(r4, textvariable=self.pvar, width=4).pack(side=LEFT)
        tk.Label(r4, text='  中心点数').pack(side=LEFT)
        self.ncvar = tk.StringVar(value='0')
        tk.Entry(r4, textvariable=self.ncvar, width=4).pack(side=LEFT)
        self.randvar = tk.BooleanVar(value=True)
        tk.Checkbutton(r4, text='随机化运行序', variable=self.randvar).pack(side=LEFT, padx=6)
        r5 = tk.Frame(f); r5.pack(side=TOP, fill=X, padx=2, pady=1)
        self.showalias = tk.BooleanVar(value=False)
        tk.Checkbutton(r5, text='输出别名结构(部分因子)', variable=self.showalias).pack(side=LEFT)

    def apply(self):
        dtype = self.dtype.get()
        names = [x.strip() for x in self.fnamevar.get().split(',') if x.strip()]
        k = len(names)
        try:
            lows = _num_list(self.lowvar)
            highs = _num_list(self.highvar)
        except ValueError:
            self.error(msg='低/高水平须为数字（逗号分隔）。')
            return
        if k < 2 or len(lows) != k or len(highs) != k:
            self.error(msg='因子名/低水平/高水平数量必须一致且 ≥ 2。')
            return
        try:
            if dtype == '2水平全因子':
                if k > 15:
                    raise ValueError('全因子设计最多 15 个因子')
                ddf = pd.DataFrame(ff2n(k), columns=factor_letters(k))
                info = {'type': '2^k 全因子', 'k': k, 'runs': len(ddf),
                        'resolution': '完全分辨（无混杂）'}
            elif dtype == '部分因子(2^(k-p))':
                p = int(self.pvar.get())
                if k < 4 or k > 15 or p < 1 or p >= k:
                    raise ValueError('因子数 4~15，部分阶数 p 须满足 1<=p<k')
                ddf, info = frac_factorial(k, p)
                if self.showalias.get():
                    self.app.print('别名结构（前几组）:')
                    for eff, ali in alias_table(k, p)[:10]:
                        self.app.print('  %s = %s' % (eff, ' + '.join(ali)))
            elif dtype == 'Plackett-Burman 筛选':
                if k > 47:
                    raise ValueError('PB 设计最多 47 个因子')
                ddf, info = pb_design(k)
            elif dtype == '确定性筛选(DSD)':
                if k < 3 or k > 48:
                    raise ValueError('DSD 因子数须在 3~48 之间')
                nc = int(self.ncvar.get())
                ddf, info = dsd(k, ncenter=nc)
            else:
                return
        except ValueError as e:
            self.error(msg=str(e))
            return

        # 中心点（全因子/部分因子按用户指定追加；DSD 已含）
        nc = int(self.ncvar.get())
        if dtype in ('2水平全因子', '部分因子(2^(k-p))') and nc > 0:
            zeros = pd.DataFrame(np.zeros((nc, k)), columns=ddf.columns)
            ddf = pd.concat([ddf, zeros], ignore_index=True)
            info['center_points'] = nc

        # 构建 Minitab 风格工作表（标准序/运行序/点类型/区组/实际值）
        ws, winfo = make_doe_worksheet(ddf, lows=lows, highs=highs,
                                       randomize=self.randvar.get())
        ws.columns = list(ws.columns[:4]) + names + ['Y']
        write_back(self.parent, ws)

        # 输出设计摘要
        self.app.print('设计生成完成: %s' % info.get('type', ''))
        self.app.print('  因子数: %d    试验次数: %d    中心点: %d' % (
            k, len(ws), nc))
        self.app.print('  因子水平:')
        for i, nm in enumerate(names):
            self.app.print('    %s: %g ~ %g' % (nm, lows[i], highs[i]))
        self.app.print('  已随机化运行序: %s' % ('是' if self.randvar.get() else '否'))
        if 'resolution' in info:
            self.app.print('  分辨率: %s' % info['resolution'])
        if 'generators' in info:
            for g, v in info['generators'].items():
                self.app.print('  生成元: %s = %s' % (g, v))
        self.app.print('工作表中：StdOrder=标准序  RunOrder=运行序  PtType=点类型(1因子/0中心/-1轴)')
        self.app.print('在 Y 列填写响应数据后，选择【分析因子设计】。')
        return


def _store_fit(app, key, fit):
    """保存拟合结果供图形/优化器复用"""
    if not hasattr(app, 'doe_fits'):
        app.doe_fits = {}
    app.doe_fits[key] = fit


# =====================================================================
# 二、创建响应曲面设计（Minitab 风格）
# =====================================================================

class RSMDesignDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='设计类型')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.dtype = tk.StringVar(value='中心复合(CCD)')
        tk.Radiobutton(f, text='中心复合设计 (CCD)', variable=self.dtype,
                       value='中心复合(CCD)', anchor='w').pack(side=TOP, fill=X)
        tk.Radiobutton(f, text='Box-Behnken 设计 (BBD)', variable=self.dtype,
                       value='Box-Behnken(BBD)', anchor='w').pack(side=TOP, fill=X)

        f = tk.LabelFrame(m, text='CCD 类型')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.ctype = tk.StringVar(value='旋转(CCC)')
        for t in ['旋转(CCC)', '面心(CCF)', '内切(CCI)']:
            tk.Radiobutton(f, text=t, variable=self.ctype, value=t,
                           anchor='w').pack(side=LEFT, padx=4)

        f = tk.LabelFrame(m, text='因子设置（逗号分隔，顺序对应）')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r1, text='因子名', width=8, anchor='w').pack(side=LEFT)
        self.fnamevar = tk.StringVar(value='A,B,C')
        tk.Entry(r1, textvariable=self.fnamevar).pack(side=LEFT, fill=X, expand=1)
        r2 = tk.Frame(f); r2.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r2, text='低水平', width=8, anchor='w').pack(side=LEFT)
        self.lowvar = tk.StringVar(value='-1,-1,-1')
        tk.Entry(r2, textvariable=self.lowvar).pack(side=LEFT, fill=X, expand=1)
        r3 = tk.Frame(f); r3.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r3, text='高水平', width=8, anchor='w').pack(side=LEFT)
        self.highvar = tk.StringVar(value='1,1,1')
        tk.Entry(r3, textvariable=self.highvar).pack(side=LEFT, fill=X, expand=1)

        f = tk.LabelFrame(m, text='设计选项')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r4 = tk.Frame(f); r4.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r4, text='中心点数').pack(side=LEFT)
        self.ncvar = tk.StringVar(value='1')
        tk.Entry(r4, textvariable=self.ncvar, width=4).pack(side=LEFT)
        self.randvar = tk.BooleanVar(value=True)
        tk.Checkbutton(r4, text='随机化运行序', variable=self.randvar).pack(side=LEFT, padx=6)

    def apply(self):
        names = [x.strip() for x in self.fnamevar.get().split(',') if x.strip()]
        k = len(names)
        try:
            nc = int(self.ncvar.get())
            lows = _num_list(self.lowvar)
            highs = _num_list(self.highvar)
        except ValueError:
            self.error(msg='数值输入无效。')
            return
        if k < 2 or len(lows) != k or len(highs) != k:
            self.error(msg='因子名/低水平/高水平数量必须一致且 ≥ 2。')
            return
        try:
            if self.dtype.get() == '中心复合(CCD)':
                if k > 10:
                    raise ValueError('CCD 因子数最多 10 个')
                ctype = self.ctype.get()
                alpha = {'旋转(CCC)': 'rotatable', '面心(CCF)': 'face',
                         '内切(CCI)': 'inscribed'}[ctype]
                ddf, info = ccd(k, alpha=alpha, ncenter=nc)
            else:
                if k < 3:
                    raise ValueError('BBD 至少需要 3 个因子')
                ddf, info = box_behnken(k, ncenter=nc)
        except ValueError as e:
            self.error(msg=str(e))
            return
        ws, winfo = make_doe_worksheet(ddf, lows=lows, highs=highs,
                                       randomize=self.randvar.get())
        ws.columns = list(ws.columns[:4]) + names + ['Y']
        write_back(self.parent, ws)
        self.app.print('设计生成完成: %s' % info.get('type', ''))
        self.app.print('  因子数: %d    试验次数: %d    中心点: %d' % (
            k, len(ws), info.get('center_points', 0)))
        if 'alpha' in info:
            self.app.print('  α(轴点位置) = %.4f   轴点实际值 = 中点 ± α×半跨度' % info['alpha'])
        self.app.print('  已随机化运行序: %s' % ('是' if self.randvar.get() else '否'))
        self.app.print('在 Y 列填写响应数据后，选择【分析响应曲面】。')
        return


# =====================================================================
# 三、创建混料设计（Minitab 风格）
# =====================================================================

class MixtureDesignDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='设计类型')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.dtype = tk.StringVar(value='单纯形质心')
        for t in ['单纯形质心', '单纯形格点', '极端顶点']:
            tk.Radiobutton(f, text=t, variable=self.dtype, value=t,
                           anchor='w').pack(side=TOP, fill=X)

        f = tk.LabelFrame(m, text='分量设置（逗号分隔）')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r1, text='分量名', width=8, anchor='w').pack(side=LEFT)
        self.fnamevar = tk.StringVar(value='A,B,C')
        tk.Entry(r1, textvariable=self.fnamevar).pack(side=LEFT, fill=X, expand=1)
        r2 = tk.Frame(f); r2.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r2, text='下限', width=8, anchor='w').pack(side=LEFT)
        self.lowvar = tk.StringVar(value='0,0,0')
        tk.Entry(r2, textvariable=self.lowvar).pack(side=LEFT, fill=X, expand=1)
        r3 = tk.Frame(f); r3.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r3, text='上限', width=8, anchor='w').pack(side=LEFT)
        self.highvar = tk.StringVar(value='1,1,1')
        tk.Entry(r3, textvariable=self.highvar).pack(side=LEFT, fill=X, expand=1)

        f = tk.LabelFrame(m, text='设计选项')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r4 = tk.Frame(f); r4.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r4, text='格点阶数 m').pack(side=LEFT)
        self.mvar = tk.StringVar(value='2')
        tk.Entry(r4, textvariable=self.mvar, width=4).pack(side=LEFT)
        self.randvar = tk.BooleanVar(value=True)
        tk.Checkbutton(r4, text='随机化运行序', variable=self.randvar).pack(side=LEFT, padx=6)

    def apply(self):
        names = [x.strip() for x in self.fnamevar.get().split(',') if x.strip()]
        q = len(names)
        dtype = self.dtype.get()
        if q < 2:
            self.error(msg='至少需要 2 个分量。')
            return
        try:
            if dtype == '单纯形质心':
                ddf, info = simplex_centroid(q)
            elif dtype == '单纯形格点':
                m = int(self.mvar.get())
                ddf, info = simplex_lattice(q, m)
            else:
                low = _num_list(self.lowvar)
                high = _num_list(self.highvar)
                if len(low) != q or len(high) != q:
                    raise ValueError('上下限数量须等于分量数')
                ddf, info = extreme_vertices(q, low=low, high=high)
        except ValueError as e:
            self.error(msg=str(e))
            return
        # 混料工作表：PtType 全 1，保持比例值
        ws, winfo = make_doe_worksheet(ddf, randomize=self.randvar.get(),
                                       pttype_all=1)
        ws.columns = list(ws.columns[:4]) + names + ['Y']
        write_back(self.parent, ws)
        self.app.print('设计生成完成: %s' % info.get('type', ''))
        self.app.print('  分量数: %d    试验次数: %d' % (q, len(ws)))
        self.app.print('  已随机化运行序: %s' % ('是' if self.randvar.get() else '否'))
        self.app.print('注意: 混料设计中每行分量之和恒为 1。在 Y 列填写响应后选择【分析混料设计】。')
        return


# =====================================================================
# 四、创建田口设计（Minitab 风格）
# =====================================================================

class TaguchiDesignDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='正交表')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.arrvar = tk.StringVar(value='L8')
        names = ['L8(2^7)', 'L9(3^4)', 'L12(2^11)', 'L16(2^15)',
                 'L18(2^1×3^7)', 'L27(3^13)', 'L32(2^31)', 'L64(2^63)']
        for t in names:
            tk.Radiobutton(f, text=t, variable=self.arrvar, value=t.split('(')[0],
                           anchor='w').pack(side=TOP, fill=X)
        f2 = tk.LabelFrame(m, text='因子分配（逗号分隔列名）')
        f2.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.fnamevar = tk.StringVar(value='')
        tk.Entry(f2, textvariable=self.fnamevar).pack(side=TOP, fill=X, padx=2, pady=2)
        f3 = tk.LabelFrame(m, text='选项')
        f3.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.randvar = tk.BooleanVar(value=True)
        tk.Checkbutton(f3, text='随机化运行序', variable=self.randvar).pack(side=LEFT, padx=4)
        tk.Label(f3, text='（不填因子名时默认 A,B,C...）', fg='gray').pack(side=LEFT)

    def apply(self):
        arr = self.arrvar.get()
        try:
            ddf, info = taguchi_design(arr)
        except ValueError as e:
            self.error(msg=str(e))
            return
        # 田口工作表：PtType 全 1
        ws, winfo = make_doe_worksheet(ddf, randomize=self.randvar.get(),
                                       pttype_all=1)
        names = [x.strip() for x in self.fnamevar.get().split(',') if x.strip()]
        if len(names) == len(ddf.columns):
            ws.columns = list(ws.columns[:4]) + names + ['Y']
        else:
            ws.columns = list(ws.columns[:4]) + list(ddf.columns) + ['Y']
        write_back(self.parent, ws)
        self.app.print('设计生成完成: %s' % info.get('type', ''))
        self.app.print('  试验次数: %d    列数: %d' % (len(ws), len(ddf.columns)))
        self.app.print('  已随机化运行序: %s' % ('是' if self.randvar.get() else '否'))
        self.app.print('正交表每行是一个试验组合；对每个组合可重复测量，Y 列填写响应，'
                      '然后选择【分析田口设计】。')
        return


# =====================================================================
# 五、创建最优设计（Minitab 风格）
# =====================================================================

class OptimalDesignDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='因子设置（逗号分隔）')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r1, text='因子名', width=8, anchor='w').pack(side=LEFT)
        self.fnamevar = tk.StringVar(value='A,B,C')
        tk.Entry(r1, textvariable=self.fnamevar).pack(side=LEFT, fill=X, expand=1)
        r2 = tk.Frame(f); r2.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r2, text='低水平', width=8, anchor='w').pack(side=LEFT)
        self.lowvar = tk.StringVar(value='-1,-1,-1')
        tk.Entry(r2, textvariable=self.lowvar).pack(side=LEFT, fill=X, expand=1)
        r3 = tk.Frame(f); r3.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r3, text='高水平', width=8, anchor='w').pack(side=LEFT)
        self.highvar = tk.StringVar(value='1,1,1')
        tk.Entry(r3, textvariable=self.highvar).pack(side=LEFT, fill=X, expand=1)

        f = tk.LabelFrame(m, text='设计选项')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r4 = tk.Frame(f); r4.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r4, text='试验次数').pack(side=LEFT)
        self.nvar = tk.StringVar(value='11')
        tk.Entry(r4, textvariable=self.nvar, width=5).pack(side=LEFT)
        tk.Label(r4, text='  模型').pack(side=LEFT)
        self.modelvar = tk.StringVar(value='quadratic')
        c = ttk.Combobox(r4, textvariable=self.modelvar, width=11,
                         values=['linear', 'interaction', 'quadratic'], state='readonly')
        c.pack(side=LEFT, padx=2)
        tk.Label(r4, text='  准则').pack(side=LEFT)
        self.critvar = tk.StringVar(value='D')
        c2 = ttk.Combobox(r4, textvariable=self.critvar, width=4,
                          values=['D', 'A', 'I', 'G'], state='readonly')
        c2.pack(side=LEFT, padx=2)
        r5 = tk.Frame(f); r5.pack(side=TOP, fill=X, padx=2, pady=1)
        tk.Label(r5, text='候选网格每维点数').pack(side=LEFT)
        self.gvar = tk.StringVar(value='5')
        tk.Entry(r5, textvariable=self.gvar, width=5).pack(side=LEFT)
        self.randvar = tk.BooleanVar(value=True)
        tk.Checkbutton(r5, text='随机化运行序', variable=self.randvar).pack(side=LEFT, padx=6)

    def apply(self):
        names = [x.strip() for x in self.fnamevar.get().split(',') if x.strip()]
        k = len(names)
        try:
            n = int(self.nvar.get())
            g = int(self.gvar.get())
            lows = _num_list(self.lowvar)
            highs = _num_list(self.highvar)
        except ValueError:
            self.error(msg='数值输入无效。')
            return
        if k < 1 or len(lows) != k or len(highs) != k:
            self.error(msg='因子名/低水平/高水平数量必须一致。')
            return
        try:
            grid = np.linspace(-1, 1, g)
            C = np.array(list(__import__('itertools').product(*[grid] * k)))
            if n > len(C):
                raise ValueError('试验次数不能超过候选点数 %d' % len(C))
            ddf, info = d_optimal_design(C, n, model=self.modelvar.get(),
                                         criterion=self.critvar.get(),
                                         nstart=8, seed=42)
        except ValueError as e:
            self.error(msg=str(e))
            return
        ws, winfo = make_doe_worksheet(ddf, lows=lows, highs=highs,
                                       randomize=self.randvar.get())
        ws.columns = list(ws.columns[:4]) + names + ['Y']
        write_back(self.parent, ws)
        self.app.print('设计生成完成: %s' % info.get('type', ''))
        self.app.print('  因子数: %d    试验次数: %d    模型: %s' % (
            k, len(ws), info.get('model', '')))
        self.app.print('  已随机化运行序: %s' % ('是' if self.randvar.get() else '否'))
        self.app.print('在 Y 列填写响应数据后，选择【分析响应曲面】。')
        return


# =====================================================================
# 六、分析因子设计
# =====================================================================

class AnalyzeFactorialDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='输入列')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=2)
        tk.Label(r1, text='响应列').pack(side=LEFT)
        self.yvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.yvar, width=12).pack(side=LEFT, padx=2)
        tk.Label(r1, text='  因子列(多选)').pack(side=LEFT)
        self.fvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.fvar, width=20).pack(side=LEFT, padx=2)

        r2 = tk.Frame(f); r2.pack(side=TOP, fill=X, padx=2, pady=2)
        tk.Label(r2, text='因子列可写为 "A,B,C" 逗号分隔').pack(side=LEFT)

        f2 = tk.LabelFrame(m, text='选项')
        f2.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.incint = tk.BooleanVar(value=True)
        tk.Checkbutton(f2, text='包含交互作用', variable=self.incint).pack(side=LEFT)
        self.doPareto = tk.BooleanVar(value=True)
        tk.Checkbutton(f2, text='绘制 Pareto 图', variable=self.doPareto).pack(side=LEFT)
        self.doNorm = tk.BooleanVar(value=True)
        tk.Checkbutton(f2, text='绘制效应正态概率图', variable=self.doNorm).pack(side=LEFT)

    def apply(self):
        y = self.yvar.get()
        fs = [x.strip() for x in self.fvar.get().split(',') if x.strip()]
        if not y or len(fs) < 2:
            self.error(msg='请选择响应列和至少 2 个因子列。')
            return
        try:
            fit = factorial_analysis(self.df, fs, y,
                                     include_interactions=self.incint.get(),
                                     max_order=2,
                                     print_out=True, print_port=self.app.print)
        except ValueError as e:
            self.error(msg=str(e))
            return
        _store_fit(self.app, 'factorial', fit)
        # 图形
        if self.doPareto.get():
            pf = self.app.showPlotViewer()
            plots_doe.pareto_plot(fit, ax=pf.fig.add_subplot(111))
        if self.doNorm.get():
            pf = self.app.showPlotViewer()
            plots_doe.normal_prob_effects(fit, ax=pf.fig.add_subplot(111))
        return


# =====================================================================
# 七、分析响应曲面
# =====================================================================

class AnalyzeRSMDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='输入列')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=2)
        tk.Label(r1, text='响应列').pack(side=LEFT)
        self.yvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.yvar, width=12).pack(side=LEFT, padx=2)
        tk.Label(r1, text='  因子列(逗号分隔)').pack(side=LEFT)
        self.fvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.fvar, width=20).pack(side=LEFT, padx=2)

        f2 = tk.LabelFrame(m, text='模型')
        f2.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.modelvar = tk.StringVar(value='quadratic')
        for t in ['linear', 'interaction', 'quadratic']:
            tk.Radiobutton(f2, text=t, variable=self.modelvar, value=t).pack(side=LEFT, padx=3)

    def apply(self):
        y = self.yvar.get()
        fs = [x.strip() for x in self.fvar.get().split(',') if x.strip()]
        if not y or len(fs) < 1:
            self.error(msg='请选择响应列和因子列。')
            return
        try:
            fit = rsm_analysis(self.df, fs, y, model=self.modelvar.get(),
                               print_out=True, print_port=self.app.print)
        except ValueError as e:
            self.error(msg=str(e))
            return
        _store_fit(self.app, 'rsm', fit)
        return


# =====================================================================
# 八、分析混料设计
# =====================================================================

class AnalyzeMixtureDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='输入列')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=2)
        tk.Label(r1, text='响应列').pack(side=LEFT)
        self.yvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.yvar, width=12).pack(side=LEFT, padx=2)
        tk.Label(r1, text='  分量列(逗号分隔)').pack(side=LEFT)
        self.fvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.fvar, width=20).pack(side=LEFT, padx=2)

        f2 = tk.LabelFrame(m, text='Scheffé 模型')
        f2.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.modelvar = tk.StringVar(value='linear')
        for t in ['linear', 'quadratic', 'special-cubic']:
            tk.Radiobutton(f2, text=t, variable=self.modelvar, value=t).pack(side=LEFT, padx=3)

    def apply(self):
        y = self.yvar.get()
        fs = [x.strip() for x in self.fvar.get().split(',') if x.strip()]
        if not y or len(fs) < 2:
            self.error(msg='请选择响应列和至少 2 个分量列。')
            return
        try:
            fit = mixture_analysis(self.df, fs, y, model=self.modelvar.get(),
                                   print_out=True, print_port=self.app.print)
        except ValueError as e:
            self.error(msg=str(e))
            return
        _store_fit(self.app, 'mixture', fit)
        return


# =====================================================================
# 九、分析田口设计
# =====================================================================

class AnalyzeTaguchiDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='输入列')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=2)
        tk.Label(r1, text='响应列').pack(side=LEFT)
        self.yvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.yvar, width=12).pack(side=LEFT, padx=2)
        tk.Label(r1, text='  因子列(逗号分隔)').pack(side=LEFT)
        self.fvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.fvar, width=20).pack(side=LEFT, padx=2)

        f2 = tk.LabelFrame(m, text='信噪比类型')
        f2.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.sntype = tk.StringVar(value='larger')
        for t, lab in [('larger', '望大'), ('smaller', '望小'), ('nominal', '望目')]:
            tk.Radiobutton(f2, text=lab, variable=self.sntype, value=t).pack(side=LEFT, padx=4)

        f3 = tk.LabelFrame(m, text='图形')
        f3.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.doMain = tk.BooleanVar(value=True)
        tk.Checkbutton(f3, text='绘制 S/N 主效应图', variable=self.doMain).pack(side=LEFT)

    def apply(self):
        y = self.yvar.get()
        fs = [x.strip() for x in self.fvar.get().split(',') if x.strip()]
        if not y or len(fs) < 1:
            self.error(msg='请选择响应列和因子列。')
            return
        try:
            fit = taguchi_analysis(self.df, fs, y, sn_type=self.sntype.get(),
                                   print_out=True, print_port=self.app.print)
        except ValueError as e:
            self.error(msg=str(e))
            return
        _store_fit(self.app, 'taguchi', fit)
        if self.doMain.get():
            pf = self.app.showPlotViewer()
            plots_doe.taguchi_main_effects(fit, which='sn', ax=pf.fig.add_subplot(111))
        return


# =====================================================================
# 十、因子图（主效应 / 交互 / 立方 / 残差）
# =====================================================================

class FactorialPlotsDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='输入列')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=2)
        tk.Label(r1, text='响应列').pack(side=LEFT)
        self.yvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.yvar, width=12).pack(side=LEFT, padx=2)
        tk.Label(r1, text='  因子列(逗号分隔)').pack(side=LEFT)
        self.fvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.fvar, width=20).pack(side=LEFT, padx=2)

        f2 = tk.LabelFrame(m, text='图形')
        f2.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.doMain = tk.BooleanVar(value=True)
        tk.Checkbutton(f2, text='主效应图', variable=self.doMain).pack(side=LEFT, padx=3)
        self.doInt = tk.BooleanVar(value=False)
        tk.Checkbutton(f2, text='交互作用图', variable=self.doInt).pack(side=LEFT, padx=3)
        self.doCube = tk.BooleanVar(value=False)
        tk.Checkbutton(f2, text='立方图', variable=self.doCube).pack(side=LEFT, padx=3)
        self.doRes = tk.BooleanVar(value=False)
        tk.Checkbutton(f2, text='残差图', variable=self.doRes).pack(side=LEFT, padx=3)

    def apply(self):
        y = self.yvar.get()
        fs = [x.strip() for x in self.fvar.get().split(',') if x.strip()]
        if not y or len(fs) < 2:
            self.error(msg='请选择响应列和至少 2 个因子列。')
            return
        try:
            fit = factorial_analysis(self.df, fs, y, max_order=2,
                                     print_out=False)
        except ValueError as e:
            self.error(msg=str(e))
            return
        _store_fit(self.app, 'factorial', fit)
        if self.doMain.get():
            pf = self.app.showPlotViewer(figsize=(8, 5))
            plots_doe.main_effects_plot(fit, ax=pf.fig.add_subplot(111))
        if self.doInt.get():
            pf = self.app.showPlotViewer(figsize=(8, 5))
            plots_doe.interaction_plot(fit, ax=pf.fig.add_subplot(111))
        if self.doCube.get():
            if len(fs) < 3:
                self.error(msg='立方图需要至少 3 个因子。')
            else:
                pf = self.app.showPlotViewer(figsize=(7, 6))
                plots_doe.cube_plot(fit, ax=pf.fig.add_subplot(111, projection='3d'))
        if self.doRes.get():
            pf = self.app.showPlotViewer(figsize=(10, 3.5))
            plots_doe.residual_plots(fit, fig=pf.fig)
        return


# =====================================================================
# 十一、等值线 / 曲面图
# =====================================================================

class ContourSurfaceDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='输入列')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=2)
        tk.Label(r1, text='响应列').pack(side=LEFT)
        self.yvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.yvar, width=12).pack(side=LEFT, padx=2)
        tk.Label(r1, text='  因子列(逗号分隔)').pack(side=LEFT)
        self.fvar = tk.StringVar(value='')
        ttk.Combobox(r1, values=self.cols, textvariable=self.fvar, width=20).pack(side=LEFT, padx=2)

        f2 = tk.LabelFrame(m, text='图形')
        f2.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.doCont = tk.BooleanVar(value=True)
        tk.Checkbutton(f2, text='等值线图', variable=self.doCont).pack(side=LEFT, padx=3)
        self.doSurf = tk.BooleanVar(value=False)
        tk.Checkbutton(f2, text='曲面图', variable=self.doSurf).pack(side=LEFT, padx=3)
        tk.Label(f2, text='   (对前两个因子绘制)').pack(side=LEFT)

    def apply(self):
        y = self.yvar.get()
        fs = [x.strip() for x in self.fvar.get().split(',') if x.strip()]
        if not y or len(fs) < 2:
            self.error(msg='请选择响应列和至少 2 个因子列。')
            return
        try:
            fit = rsm_analysis(self.df, fs, y, model='quadratic', print_out=False)
        except ValueError as e:
            self.error(msg=str(e))
            return
        _store_fit(self.app, 'rsm', fit)
        if self.doCont.get():
            pf = self.app.showPlotViewer(figsize=(7, 6))
            plots_doe.contour_plot(fit, ix=0, iy=1, ax=pf.fig.add_subplot(111))
        if self.doSurf.get():
            pf = self.app.showPlotViewer(figsize=(7, 6))
            plots_doe.surface_plot(fit, ix=0, iy=1, ax=pf.fig.add_subplot(111, projection='3d'))
        return


# =====================================================================
# 十二、响应优化器
# =====================================================================

class ResponseOptimizerDialog(Dialogs):
    def createWidgets(self, m):
        f = tk.LabelFrame(m, text='说明')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        tk.Label(f, text='请先完成【分析响应曲面】或【分析因子设计】，\n'
                        '本对话框使用最近一次拟合结果。',
                 justify=LEFT, anchor='w').pack(side=TOP, fill=X, padx=2, pady=2)

        f = tk.LabelFrame(m, text='优化目标')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        self.goalvar = tk.StringVar(value='larger')
        for t, lab in [('larger', '望大'), ('smaller', '望小'), ('target', '望目')]:
            tk.Radiobutton(f, text=lab, variable=self.goalvar, value=t).pack(side=LEFT, padx=4)

        f = tk.LabelFrame(m, text='边界（逗号分隔，顺序对应因子）')
        f.pack(side=TOP, fill=BOTH, padx=2, pady=2)
        r1 = tk.Frame(f); r1.pack(side=TOP, fill=X, padx=2, pady=2)
        tk.Label(r1, text='下限').pack(side=LEFT)
        self.lowvar = tk.StringVar(value='-1,-1,-1')
        tk.Entry(r1, textvariable=self.lowvar, width=18).pack(side=LEFT, padx=2)
        tk.Label(r1, text='  上限').pack(side=LEFT)
        self.highvar = tk.StringVar(value='1,1,1')
        tk.Entry(r1, textvariable=self.highvar, width=18).pack(side=LEFT, padx=2)

        r2 = tk.Frame(f); r2.pack(side=TOP, fill=X, padx=2, pady=2)
        tk.Label(r2, text='目标值 T').pack(side=LEFT)
        self.tgtvar = tk.StringVar(value='')
        tk.Entry(r2, textvariable=self.tgtvar, width=10).pack(side=LEFT, padx=2)
        tk.Label(r2, text='  下限 L').pack(side=LEFT)
        self.lvar = tk.StringVar(value='')
        tk.Entry(r2, textvariable=self.lvar, width=10).pack(side=LEFT, padx=2)
        tk.Label(r2, text='  上限 U').pack(side=LEFT)
        self.uvar = tk.StringVar(value='')
        tk.Entry(r2, textvariable=self.uvar, width=10).pack(side=LEFT, padx=2)

    def apply(self):
        if not hasattr(self.app, 'doe_fits'):
            self.error(msg='请先完成响应曲面或因子分析。')
            return
        fit = self.app.doe_fits.get('rsm') or self.app.doe_fits.get('factorial')
        if fit is None:
            self.error(msg='未找到拟合结果，请先分析。')
            return
        k = fit['k']
        try:
            lo = [float(x) for x in self.lowvar.get().split(',')]
            hi = [float(x) for x in self.highvar.get().split(',')]
            if len(lo) != k or len(hi) != k:
                raise ValueError('边界数量须等于因子数 %d' % k)
        except ValueError as e:
            self.error(msg=str(e))
            return
        goal = self.goalvar.get()
        low = float(self.lvar.get()) if self.lvar.get() else None
        high = float(self.uvar.get()) if self.uvar.get() else None
        target = float(self.tgtvar.get()) if self.tgtvar.get() else None
        try:
            from .optimize import ResponseSpec, optimize, optimization_plot
            spec = ResponseSpec(fit['response'], fit, goal, low=low,
                                target=target, high=high)
            bounds = list(zip(lo, hi))
            result = optimize([spec], bounds, print_out=True,
                              print_port=self.app.print)
            # 优化图
            pf = self.app.showPlotViewer(figsize=(3.2 * k, 3.0))
            optimization_plot(result, [spec], bounds, fig=pf.fig)
        except Exception as e:
            self.error(msg='优化失败: %s' % e)
        return
