# -*- coding: utf-8 -*-
# ============================================================
# 贡献者 / Contributors
#   胡志东 (Nico HU) <Hzd378747710@outlook.com>
#   - DOE 模块: 图形 (2026-08)
# ============================================================
"""DOE 图形模块（matplotlib）
=========================================================
复刻 Minitab DOE 图形：
  主效应图 / 交互作用图 / 立方图 / Pareto 图 / 效应正态概率图
  等值线图 / 曲面图 / 残差图 / 优化图 / 田口主效应图
所有图在传入的 ax 上绘制，由调用方（对话框）负责显示。
=========================================================
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')   # 仅保证可导入；实际由 GUI 环境渲染
import matplotlib.pyplot as plt
from matplotlib import cm


def _setup_ax(ax, title, xlabel, ylabel):
    if title:
        ax.set_title(title, fontsize=12)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)


# =====================================================================
# 一、主效应图
# =====================================================================

def main_effects_plot(fit, ax=None, factors=None):
    """主效应图：每个因子在其各水平上的响应均值"""
    if ax is None:
        ax = plt.gca()
    Xc = fit['Xc']
    y = fit['y']
    letters = fit['letters'] if 'letters' in fit else fit['factors']
    nf = Xc.shape[1]
    if factors is None:
        factors = range(nf)
    _setup_ax(ax, '主效应图（数据均值）', '因子', '响应均值')
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    for fi, j in enumerate(factors):
        col = Xc[:, j]
        u = np.unique(np.round(col, 6))
        means = [y[np.abs(col - lv) < 1e-6].mean() for lv in u]
        lname = letters[j] if isinstance(letters, list) else str(letters)
        ax.plot(u, means, marker='o', ls='-', color=colors[fi % len(colors)],
                label=lname)
    ax.legend(loc='best', fontsize=9)
    return ax


# =====================================================================
# 二、交互作用图
# =====================================================================

def interaction_plot(fit, ax=None, pair=None):
    """交互作用图：两个因子的各水平组合均值
    pair: (i, j) 因子索引；None 时显示第一个交互
    """
    if ax is None:
        ax = plt.gca()
    Xc = fit['Xc']
    y = fit['y']
    letters = fit['letters'] if 'letters' in fit else fit['factors']
    nf = Xc.shape[1]
    if pair is None:
        if nf < 2:
            return ax
        pair = (0, 1)
    i, j = pair
    li = np.unique(np.round(Xc[:, i], 6))
    lj = np.unique(np.round(Xc[:, j], 6))
    _setup_ax(ax, '交互作用图（%s × %s）' % (letters[i], letters[j]),
              letters[i], '响应均值')
    for lvj in lj:
        sel = np.abs(Xc[:, j] - lvj) < 1e-6
        means = [y[sel & (np.abs(Xc[:, i] - lvi) < 1e-6)].mean() for lvi in li]
        ax.plot(li, means, marker='o', ls='-', label='%s = %g' % (letters[j], lvj))
    ax.legend(loc='best', fontsize=9)
    return ax


# =====================================================================
# 三、立方图（3 因子）
# =====================================================================

def cube_plot(fit, ax=None):
    """立方图：三维显示 3 因子各组合的响应均值"""
    if ax is None:
        ax = plt.gca(projection='3d')
    Xc = fit['Xc']
    y = fit['y']
    letters = fit['letters'] if 'letters' in fit else fit['factors']
    # 取 3 因子（或前 3 个）
    nf = Xc.shape[1]
    idx = [0, 1, 2]
    L = [np.unique(np.round(Xc[:, j], 6)) for j in idx]
    # 在立方体角点标注响应
    from mpl_toolkits.mplot3d import Axes3D  # noqa
    verts = [(l0, l1, l2) for l0 in L[0] for l1 in L[1] for l2 in L[2]]
    pts = np.array(verts)
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], c='b', s=20)
    for v in verts:
        sel = (np.abs(Xc[:, 0] - v[0]) < 1e-6) & \
              (np.abs(Xc[:, 1] - v[1]) < 1e-6) & \
              (np.abs(Xc[:, 2] - v[2]) < 1e-6)
        m = y[sel].mean() if sel.sum() else np.nan
        ax.text(v[0], v[1], v[2], '%.2f' % m, fontsize=8, ha='center')
    ax.set_xlabel(letters[0]); ax.set_ylabel(letters[1]); ax.set_zlabel(letters[2])
    ax.set_title('立方图（响应均值）')
    return ax


# =====================================================================
# 四、Pareto 图（标准化效应）
# =====================================================================

def pareto_plot(fit, ax=None, alpha=0.05):
    """Pareto 图：标准化效应的绝对值排序（与 Minitab 一致）"""
    if ax is None:
        ax = plt.gca()
    # 标准化效应 = 效应 / se_effect；Minitab 用 t 值
    names = fit['names']
    tvals = fit['t']
    letters = fit.get('letters', [])
    items = [(names[i], abs(tvals[i])) for i in range(1, len(tvals))]
    items.sort(key=lambda x: -x[1])
    labels = [it[0] for it in items]
    vals = [it[1] for it in items]
    _setup_ax(ax, 'Pareto 图（标准化效应）', '项', '标准化效应')
    ax.barh(range(len(vals)), vals, color='#4472C4', align='center')
    ax.set_yticks(range(len(vals)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    # 参考线（t 临界值）
    from scipy import stats
    df = fit.get('df_error')
    if df and df > 0:
        tcrit = stats.t.ppf(1 - alpha / 2, df)
        ax.axvline(tcrit, color='red', ls='--', lw=1)
        ax.axvline(-tcrit, color='red', ls='--', lw=1)
        ax.text(tcrit, len(vals) - 0.5, '%.2f' % tcrit, fontsize=8, color='red')
    return ax


# =====================================================================
# 五、效应正态概率图
# =====================================================================

def normal_prob_effects(fit, ax=None):
    """效应（绝对值）正态概率图：显著效应偏离直线（与 Minitab 一致）"""
    if ax is None:
        ax = plt.gca()
    from scipy import stats
    effects = []
    labels = []
    letters = fit.get('letters', [])
    for t in fit['terms']:
        if not t:
            continue
        eff = 2 * fit['coef'][fit['terms'].index(t)]
        effects.append(abs(eff))
        labels.append(''.join(letters[i] for i in t))
    effects = np.array(effects)
    n = len(effects)
    # 半正态概率位置（Minitab 用调整秩）
    ranks = np.argsort(np.argsort(effects)) + 1
    probs = (ranks - 0.5) / n
    zscores = stats.norm.ppf(0.5 + 0.5 * probs)
    ax.scatter(effects, zscores, marker='o', color='#4472C4')
    for i, lb in enumerate(labels):
        ax.annotate(lb, (effects[i], zscores[i]), fontsize=8,
                    textcoords='offset points', xytext=(4, 2))
    ax.axhline(0, color='gray', lw=0.5)
    ax.set_xlabel('标准化效应绝对值')
    ax.set_ylabel('正态得分')
    ax.set_title('效应的正态概率图')
    return ax


# =====================================================================
# 六、等值线图
# =====================================================================

def contour_plot(fit, ix=0, iy=1, ax=None, n=100, other=None):
    """等值线图：两因子响应曲面等值线（其他因子固定在最优/中心）"""
    if ax is None:
        ax = plt.gca()
    Xcs = fit['Xcs']
    letters = fit.get('letters', fit['factors'])
    k = Xcs.shape[1]
    if other is None:
        other = [0.0] * k
    # 两因子范围
    vx = Xcs[:, ix]
    vy = Xcs[:, iy]
    x = np.linspace(vx.min(), vx.max(), n)
    y = np.linspace(vy.min(), vy.max(), n)
    Xg, Yg = np.meshgrid(x, y)
    Z = np.zeros_like(Xg)
    terms = fit['terms']
    for a in range(n):
        for b in range(n):
            row = [1.0]
            xs = [0.0] * k
            xs[ix] = Xg[a, b]
            xs[iy] = Yg[a, b]
            for j in range(k):
                if j != ix and j != iy:
                    xs[j] = other[j]
            for t in terms:
                if not t:
                    continue
                val = 1.0
                for j in t:
                    val *= xs[j]
                row.append(val)
            Z[a, b] = np.array(row) @ fit['coef']
    cs = ax.contour(Xg, Yg, Z, levels=12, cmap='viridis')
    ax.clabel(cs, inline=True, fontsize=8, fmt='%.1f')
    ax.set_xlabel(letters[ix])
    ax.set_ylabel(letters[iy])
    ax.set_title('等值线图: %s' % fit['response'])
    ax.grid(True, alpha=0.3)
    return ax


# =====================================================================
# 七、曲面图
# =====================================================================

def surface_plot(fit, ix=0, iy=1, ax=None, n=50, other=None):
    """曲面图：两因子响应曲面 3D"""
    from mpl_toolkits.mplot3d import Axes3D  # noqa
    if ax is None:
        ax = plt.gca(projection='3d')
    Xcs = fit['Xcs']
    letters = fit.get('letters', fit['factors'])
    k = Xcs.shape[1]
    if other is None:
        other = [0.0] * k
    vx = Xcs[:, ix]
    vy = Xcs[:, iy]
    x = np.linspace(vx.min(), vx.max(), n)
    y = np.linspace(vy.min(), vy.max(), n)
    Xg, Yg = np.meshgrid(x, y)
    Z = np.zeros_like(Xg)
    terms = fit['terms']
    for a in range(n):
        for b in range(n):
            row = [1.0]
            xs = [0.0] * k
            xs[ix] = Xg[a, b]
            xs[iy] = Yg[a, b]
            for j in range(k):
                if j != ix and j != iy:
                    xs[j] = other[j]
            for t in terms:
                if not t:
                    continue
                val = 1.0
                for j in t:
                    val *= xs[j]
                row.append(val)
            Z[a, b] = np.array(row) @ fit['coef']
    ax.plot_surface(Xg, Yg, Z, cmap=cm.coolwarm, alpha=0.9)
    ax.set_xlabel(letters[ix])
    ax.set_ylabel(letters[iy])
    ax.set_zlabel(fit['response'])
    ax.set_title('曲面图: %s' % fit['response'])
    return ax


# =====================================================================
# 八、残差图（正态概率 + 拟合值 + 顺序）
# =====================================================================

def residual_plots(fit, fig=None):
    """残差图组合：正态概率图、残差 vs 拟合值、残差 vs 顺序"""
    if fig is None:
        fig = plt.figure(figsize=(10, 3.2))
    resid = fit['resid']
    yhat = fit['yhat']
    from scipy import stats
    # 1) 残差正态概率图
    ax1 = fig.add_subplot(131)
    sr = np.sort(resid)
    p = (np.arange(1, len(sr) + 1) - 0.5) / len(sr)
    ax1.scatter(sr, stats.norm.ppf(p), s=15, color='#4472C4')
    ax1.set_title('残差的正态概率图')
    ax1.set_xlabel('残差'); ax1.set_ylabel('百分数')
    ax1.grid(True, alpha=0.3)
    # 2) 残差 vs 拟合值
    ax2 = fig.add_subplot(132)
    ax2.axhline(0, color='gray', lw=0.8)
    ax2.scatter(yhat, resid, s=15, color='#4472C4')
    ax2.set_title('残差与拟合值')
    ax2.set_xlabel('拟合值'); ax2.set_ylabel('残差')
    ax2.grid(True, alpha=0.3)
    # 3) 残差 vs 顺序
    ax3 = fig.add_subplot(133)
    ax3.axhline(0, color='gray', lw=0.8)
    ax3.plot(range(1, len(resid) + 1), resid, marker='o', ls='-',
             ms=3, color='#4472C4')
    ax3.set_title('残差与观测顺序')
    ax3.set_xlabel('观测顺序'); ax3.set_ylabel('残差')
    ax3.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


# =====================================================================
# 九、优化图
# =====================================================================

def optimization_plot(opt_result, specs, bounds, ax=None, fig=None):
    """优化图：每个因子对预测响应与复合意愿的影响
    fig: 可选外部 Figure（挂在 plot_viewer 上）
    """
    from .optimize import optimize_plot_data
    data = optimize_plot_data(specs, bounds, opt_result['best_x'])
    k = len(bounds)
    nrows = len(specs) + 1
    if fig is None:
        fig = plt.figure(figsize=(3.2 * k, 2.6 * nrows))
    fig.clf()
    axs = fig.subplots(nrows, k, sharex='col')
    if k == 1:
        axs = axs.reshape(-1, 1)
    # 每行一个响应 + 最后一行复合意愿
    for r, spec in enumerate(specs):
        for j in range(k):
            a = axs[r, j]
            a.axvline(opt_result['best_x'][j], color='red', lw=1.2, ls='--')
            a.plot(data[j]['x'], data[j]['preds'][spec.name], color='#4472C4')
            if r == 0:
                a.set_title('因子 %d' % (j + 1), fontsize=9)
            if j == 0:
                a.set_ylabel(spec.name, fontsize=8)
            a.tick_params(labelsize=7)
    # 最后一行：复合意愿
    for j in range(k):
        a = axs[len(specs), j]
        a.axvline(opt_result['best_x'][j], color='red', lw=1.2, ls='--')
        a.plot(data[j]['x'], data[j]['D'], color='#2ca02c')
        if j == 0:
            a.set_ylabel('复合意愿', fontsize=8)
        a.tick_params(labelsize=7)
    fig.tight_layout()
    return fig


# =====================================================================
# 十、田口主效应图（S/N 与均值）
# =====================================================================

def taguchi_main_effects(fit, which='sn', ax=None):
    """田口主效应图：各因子水平平均 S/N（或均值）"""
    if ax is None:
        ax = plt.gca()
    d = fit['sn_vals'] if which == 'sn' else fit['mean_vals']
    factors = fit['factors']
    combos = fit['combos']
    _setup_ax(ax, '主效应图（%s）' % ('信噪比' if which == 'sn' else '均值'),
              '水平', '信噪比' if which == 'sn' else '均值')
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for fi, f in enumerate(factors):
        lv_means = {}
        for key in combos:
            lv = key[fi]
            lv_means.setdefault(lv, []).append(d[key])
        xs = sorted(lv_means.keys(), key=lambda x: str(x))
        means = [float(np.mean(lv_means[x])) for x in xs]
        ax.plot(range(1, len(xs) + 1), means, marker='o', ls='-',
                color=colors[fi % len(colors)], label=f)
    ax.set_xticks(range(1, 4))
    ax.legend(loc='best', fontsize=8)
    return ax
