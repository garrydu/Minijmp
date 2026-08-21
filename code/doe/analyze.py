# -*- coding: utf-8 -*-
# ============================================================
# 贡献者 / Contributors
#   胡志东 (Nico HU) <Hzd378747710@outlook.com>
#   - DOE 模块: 分析引擎 (2026-08)
# ============================================================
"""DOE 分析引擎
=========================================================
复刻 Minitab DOE 模块的分析功能。输出与 Minitab 一致。
公式标准：
  - Montgomery《Design and Analysis of Experiments》
  - Minitab 帮助文档《Methods and formulas》
  - Scheffé 混料多项式
  - 田口信噪比（望大/望小/望目）
=========================================================
"""
import numpy as np
import pandas as pd
from scipy import stats
from itertools import combinations

_EPS = 1e-12


# =====================================================================
# 一、通用 OLS 回归（编码/未编码统一入口）
# =====================================================================

class OLSResult:
    """OLS 回归结果容器"""
    def __init__(self):
        self.coef = None          # 系数
        self.se = None            # 系数标准误
        self.t = None             # t 值
        self.p = None             # p 值
        self.names = None         # 项名
        self.df_error = None
        self.mse = None
        self.yhat = None
        self.resid = None
        self.r2 = None
        self.r2_adj = None
        self.r2_pred = None
        self.press = None
        self.ss_reg = None
        self.ss_res = None
        self.ss_tot = None
        self.df_model = None


def ols(X, y, names=None):
    """标准最小二乘回归
    X: 设计矩阵（含截距列）
    y: 响应
    names: 各列名称
    返回 OLSResult
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    n, p = X.shape
    XtX = X.T @ X
    XtXinv = np.linalg.pinv(XtX)
    coef = XtXinv @ (X.T @ y)
    yhat = X @ coef
    resid = y - yhat
    df_model = p - 1
    df_error = n - p
    ss_reg = float(np.sum((yhat - y.mean()) ** 2))
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    mse = ss_res / df_error if df_error > 0 else np.nan
    se = np.sqrt(np.diag(XtXinv) * mse) if df_error > 0 else np.full(p, np.nan)
    t = coef / se if df_error > 0 else np.full(p, np.nan)
    p = 2 * (1 - stats.t.cdf(np.abs(t), df_error)) if df_error > 0 else np.full(p, np.nan)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    r2_adj = 1 - (1 - r2) * (n - 1) / df_error if df_error > 0 else np.nan
    # PRESS 与预测 R²（逐点留一）
    press = 0.0
    try:
        H = X @ XtXinv @ X.T
        h = np.diag(H)
        for i in range(n):
            if 1 - h[i] > 1e-12:
                press += (resid[i] / (1 - h[i])) ** 2
    except Exception:
        press = np.nan
    r2_pred = 1 - press / ss_tot if ss_tot > 0 and not np.isnan(press) else np.nan
    res = OLSResult()
    res.coef = coef
    res.se = se
    res.t = t
    res.p = p
    res.names = names if names else ['x%d' % i for i in range(p)]
    res.df_error = df_error
    res.mse = mse
    res.yhat = yhat
    res.resid = resid
    res.r2 = r2
    res.r2_adj = r2_adj
    res.r2_pred = r2_pred
    res.press = press
    res.ss_reg = ss_reg
    res.ss_res = ss_res
    res.ss_tot = ss_tot
    res.df_model = df_model
    return res


def fmt_num(x, nd=6):
    """数值格式化（对齐 Minitab 风格）"""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ''
    return ('%%.%df' % nd) % float(x)


# =====================================================================
# 二、因子设计分析（2^k / 部分因子）
# =====================================================================

def encode2(vals):
    """两水平数值列转 ±1 编码（支持含中心点：两极端→±1，中点→0）"""
    v = np.asarray(vals, dtype=float)
    u = np.unique(v)
    if len(u) == 2:
        lo, hi = u[0], u[1]
        return np.where(np.abs(v - lo) < 1e-12, -1.0, 1.0), lo, hi
    elif len(u) == 3:
        # 含中心点（中间水平编码为 0，与 Minitab 一致）
        lo, mid, hi = u[0], u[1], u[2]
        out = np.zeros(len(v))
        out[np.abs(v - lo) < 1e-12] = -1.0
        out[np.abs(v - hi) < 1e-12] = 1.0
        out[np.abs(v - mid) < 1e-12] = 0.0
        return out, lo, hi
    raise ValueError("两水平因子必须恰好有 2 个不同水平（或含中心点的 3 水平）")


def _effect_terms(k, include_interactions=True, max_order=None):
    """生成因子模型项（索引元组列表）"""
    terms = [()]
    if include_interactions:
        maxo = max_order if max_order else k
        for r in range(1, maxo + 1):
            for c in combinations(range(k), r):
                terms.append(c)
    else:
        for j in range(k):
            terms.append((j,))
    return terms


def _term_name(term, letters):
    if not term:
        return '常量'
    return ''.join(letters[i] for i in term)


def factorial_analysis(df, factor_names, response, include_interactions=True,
                       max_order=2, alpha=0.05, print_out=True, print_port=print):
    """因子设计分析（已编码单位，与 Minitab 一致）
    df: 数据 DataFrame
    factor_names: 因子列名列表（两水平）
    response: 响应列名
    返回: dict（系数/效应/ANOVA/残差等，供图形使用）
    """
    k = len(factor_names)
    letters = [str(f) for f in factor_names]
    y = df[response].astype(float).values
    n = len(y)
    # 编码因子列
    Xc = np.column_stack([encode2(df[f].values)[0] for f in factor_names])
    # 模型矩阵（±1 编码 + 交互）
    terms = _effect_terms(k, include_interactions, max_order)
    Xm = np.column_stack([np.prod([Xc[:, j] for j in t], axis=0) if t else np.ones(n)
                          for t in terms])
    # 回归（正交时等价于效应分解）
    res = ols(Xm, y, names=[_term_name(t, letters) for t in terms])
    effects = {t: 2.0 * res.coef[i] for i, t in enumerate(terms) if t}
    coefs = {t: res.coef[i] for i, t in enumerate(terms)}

    # ---- 方差分析 ----
    # 主效应与交互的 SS（正交设计）
    rows = []
    ss_model = 0.0
    df_model = 0
    for i, t in enumerate(terms):
        if not t:
            continue
        ss = float((Xm[:, i] ** 2).sum()) * (res.coef[i] ** 2)   # SS = Σx²·b²（含中心点时列平方和）
        ss_model += ss
        df_model += 1
        rows.append({'term': _term_name(t, letters), 'type': 'effect',
                     'ss': ss, 'df': 1, 'idx': i})
    # 残差
    ss_resid = res.ss_res
    df_resid = res.df_error
    # 纯误差（重复试验）：按设计点分组
    ss_pe = 0.0
    df_pe = 0
    try:
        Xdf = pd.DataFrame(Xc, columns=factor_names)
        g = Xdf.groupby(list(factor_names))[response]
        # 手动计算组内平方和
        grp = Xdf[factor_names].copy()
        grp['__y'] = y
        for _, sub in grp.groupby(list(factor_names)):
            if len(sub) > 1:
                ss_pe += float(np.sum((sub['__y'].values - sub['__y'].mean()) ** 2))
                df_pe += len(sub) - 1
    except Exception:
        pass
    ss_curv = 0.0
    if df_pe > 0:
        ss_lof = max(ss_resid - ss_pe, 0.0)
        df_lof = df_resid - df_pe
    else:
        ss_lof = 0.0
        df_lof = 0

    # ANOVA 文本
    lines = []
    lines.append("=" * 62)
    lines.append("拟合因子: %s 与 %s" % (response, ', '.join(factor_names)))
    lines.append("=" * 62)
    lines.append("")
    lines.append("效应和系数的估计（已编码单位）")
    hdr = "%-14s %9s %10s %10s %8s %8s" % ('项', '效应', '系数', '系数标准误', 'T', 'P')
    lines.append(hdr)
    lines.append("-" * len(hdr))
    lines.append("%-14s %9s %10s %10s %8s %8s" % (
        '常量', '', fmt_num(res.coef[0]), fmt_num(res.se[0]),
        fmt_num(res.t[0]), fmt_num(res.p[0])))
    for i, t in enumerate(terms):
        if not t:
            continue
        eff = 2 * res.coef[i]
        lines.append("%-14s %9s %10s %10s %8s %8s" % (
            _term_name(t, letters), fmt_num(eff), fmt_num(res.coef[i]),
            fmt_num(res.se[i]), fmt_num(res.t[i]), fmt_num(res.p[i])))
    lines.append("")
    # 方差分析
    lines.append("方差分析（已编码单位）")
    hdr2 = "%-14s %7s %12s %12s %10s %8s %8s" % ('来源', '自由度', 'Seq SS', 'Adj SS', 'Adj MS', 'F', 'P')
    lines.append(hdr2)
    lines.append("-" * len(hdr2))
    # 主效应合并行
    if include_interactions:
        # 按阶数分组：主效应 / 2因子交互 / 3因子交互
        groups = {}
        for r in rows:
            if r['type'] == 'effect':
                groups.setdefault(r['term'], r)
        # 简化：逐项列出（Minitab 主效应/2因子交互分组）
        grp_rows = {}
        for t in terms:
            if not t:
                continue
            if len(t) == 1:
                grp_rows.setdefault('主效应', []).append(t)
            elif len(t) == 2:
                grp_rows.setdefault('2因子交互', []).append(t)
            elif len(t) == 3:
                grp_rows.setdefault('3因子交互', []).append(t)
        for gname, tlist in grp_rows.items():
            ss_g = sum(float((Xm[:, terms.index(t)] ** 2).sum()) * res.coef[terms.index(t)] ** 2 for t in tlist)
            df_g = len(tlist)
            ms_g = ss_g / df_g
            f_g = ms_g / res.mse if res.mse and res.mse > 0 else np.nan
            p_g = stats.f.sf(f_g, df_g, df_resid) if res.mse and res.mse > 0 else np.nan
            lines.append("%-14s %7d %12s %12s %10s %8s %8s" % (
                gname, df_g, fmt_num(ss_g), fmt_num(ss_g), fmt_num(ms_g),
                fmt_num(f_g), fmt_num(p_g)))
            for t in tlist:
                i = terms.index(t)
                ss_t = float((Xm[:, i] ** 2).sum()) * res.coef[i] ** 2
                f_t = (ss_t / 1) / res.mse if res.mse and res.mse > 0 else np.nan
                p_t = stats.f.sf(f_t, 1, df_resid) if res.mse and res.mse > 0 else np.nan
                lines.append("  %-12s %7d %12s %12s %10s %8s %8s" % (
                    _term_name(t, letters), 1, fmt_num(ss_t), fmt_num(ss_t),
                    fmt_num(ss_t), fmt_num(f_t), fmt_num(p_t)))
    else:
        for r in rows:
            f_t = (r['ss'] / 1) / (res.mse) if res.mse and res.mse > 0 else np.nan
            p_t = stats.f.sf(f_t, 1, df_resid) if res.mse and res.mse > 0 else np.nan
            lines.append("%-14s %7d %12s %12s %10s %8s %8s" % (
                r['term'], 1, fmt_num(r['ss']), fmt_num(r['ss']),
                fmt_num(r['ss']), fmt_num(f_t), fmt_num(p_t)))
    # 残差
    lines.append("残差误差      %7d %12s %12s %10s" % (
        df_resid, fmt_num(ss_resid), fmt_num(ss_resid),
        fmt_num(ss_resid / df_resid if df_resid else np.nan)))
    if df_pe > 0:
        ms_pe = ss_pe / df_pe
        f_lof = (ss_lof / df_lof) / ms_pe if (df_lof > 0 and ms_pe > 1e-15) else np.nan
        p_lof = stats.f.sf(f_lof, df_lof, df_pe) if (df_lof > 0 and ms_pe > 1e-15) else np.nan
        lines.append("  失拟        %7d %12s %12s %10s %8s %8s" % (
            df_lof, fmt_num(ss_lof), fmt_num(ss_lof),
            fmt_num(ss_lof / df_lof if df_lof else np.nan),
            fmt_num(f_lof), fmt_num(p_lof)))
        lines.append("  纯误差      %7d %12s %12s %10s" % (
            df_pe, fmt_num(ss_pe), fmt_num(ss_pe), fmt_num(ms_pe)))
    lines.append("合计          %7d %12s" % (n - 1, fmt_num(res.ss_tot)))
    lines.append("")
    lines.append("模型汇总")
    lines.append("S = %s    R-sq = %s%%    R-sq(调整) = %s%%    R-sq(预测) = %s%%" % (
        fmt_num(np.sqrt(res.mse) if res.mse else np.nan, 6),
        fmt_num(100 * res.r2, 2), fmt_num(100 * res.r2_adj, 2),
        fmt_num(100 * res.r2_pred if not np.isnan(res.r2_pred) else np.nan, 2)))
    lines.append("")
    if df_resid <= 0:
        lines.append("注意: 模型饱和，无误差项。请使用 Pareto 图和正态概率图判断显著性。")

    if print_out:
        for ln in lines:
            print_port(ln)

    # 结构化结果（供图形）
    res2 = {
        'type': 'factorial',
        'factors': factor_names,
        'response': response,
        'n': n, 'k': k,
        'terms': terms,
        'names': [_term_name(t, letters) for t in terms],
        'coef': res.coef, 'effects': effects, 'se': res.se,
        't': res.t, 'p': res.p,
        'letters': letters,
        'Xc': Xc, 'y': y,
        'mse': res.mse, 'df_error': res.df_error,
        'r2': res.r2, 'r2_adj': res.r2_adj, 'r2_pred': res.r2_pred,
        'resid': res.resid, 'yhat': res.yhat,
        'ss_resid': ss_resid, 'ss_tot': res.ss_tot,
        'alpha': alpha,
    }
    return res2


# =====================================================================
# 三、响应曲面分析（二次模型）
# =====================================================================

def _rsm_terms(k, model='quadratic'):
    """响应曲面模型项
    model: 'linear'(主效应) | 'interaction'(主效应+交互) | 'quadratic'(主效应+平方+交互)
    """
    terms = [()]
    for j in range(k):
        terms.append((j,))
    if model in ('quadratic',):
        for j in range(k):
            terms.append((j, j))
    if model in ('interaction', 'quadratic'):
        for i in range(k):
            for j in range(i + 1, k):
                terms.append((i, j))
    return terms


def _auto_encode_column(v):
    """因子列自动编码（与 Minitab 一致）
    - 列已含 ±1（设计编码，如 CCD 的 -α/-1/0/1/α、BBD 的 -1/0/1）: 直接用
    - 否则线性编码到 [-1,1]（实际尺度 -> 编码）
    """
    v = np.asarray(v, dtype=float)
    u = np.unique(np.round(v, 10))
    if -1.0 in u and 1.0 in u:
        return v.astype(float)      # 已编码
    lo, hi = v.min(), v.max()
    if abs(hi - lo) < _EPS:
        return np.zeros_like(v)
    return 2.0 * (v - lo) / (hi - lo) - 1.0


def _seq_ss(Xm, y):
    """QR 顺序分解计算各列顺序平方和（修正 Gram-Schmidt，学术标准）
    返回每列贡献的 Seq SS（第 0 列=常量）
    """
    n = len(y)
    p = Xm.shape[1]
    Q = np.zeros((n, p))
    contrib = np.zeros(p)
    for j in range(p):
        v = Xm[:, j].copy().astype(float)
        for i in range(j):
            if np.linalg.norm(Q[:, i]) > 1e-12:
                v = v - (Q[:, i] @ v) * Q[:, i]
        nrm = np.linalg.norm(v)
        if nrm > 1e-12:
            Q[:, j] = v / nrm
            contrib[j] = (Q[:, j] @ y) ** 2
        else:
            contrib[j] = 0.0
    return contrib


def rsm_analysis(df, factor_names, response, model='quadratic',
                 alpha=0.05, print_out=True, print_port=print):
    """响应曲面分析（已编码单位二次回归 + 失拟检验，与 Minitab 一致）"""
    k = len(factor_names)
    letters = [str(f) for f in factor_names]
    y = df[response].astype(float).values
    n = len(y)
    # 因子编码：已编码(含±1)则保持设计编码，否则线性编码到 [-1,1]
    Xc = np.column_stack([df[f].astype(float).values for f in factor_names])
    enc = []
    Xcs_cols = []
    for j in range(k):
        v = Xc[:, j]
        u = np.unique(np.round(v, 10))
        if -1.0 in u and 1.0 in u:
            enc.append('asis')
            Xcs_cols.append(v.astype(float))
        else:
            lo, hi = float(v.min()), float(v.max())
            enc.append((lo, hi))
            Xcs_cols.append(_auto_encode_column(v))
    Xcs = np.column_stack(Xcs_cols)
    terms = _rsm_terms(k, model)
    Xm = np.column_stack([
        np.prod([Xcs[:, j] for j in t], axis=0) if t else np.ones(n) for t in terms])
    res = ols(Xm, y, names=[_term_name(t, letters) for t in terms])
    # QR 顺序 SS（每项）
    seq = _seq_ss(Xm, y)

    # ---- ANOVA ----
    lines = []
    lines.append("=" * 62)
    lines.append("响应曲面回归: %s 与 %s" % (response, ', '.join(factor_names)))
    lines.append("=" * 62)
    lines.append("")
    lines.append("系数估计（已编码单位）")
    hdr = "%-16s %10s %12s %10s %8s %8s" % ('项', '系数', '系数标准误', 'T', 'P', 'VIF')
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for i, t in enumerate(terms):
        lines.append("%-16s %10s %12s %10s %8s" % (
            _term_name(t, letters), fmt_num(res.coef[i]), fmt_num(res.se[i]),
            fmt_num(res.t[i]), fmt_num(res.p[i])))
    lines.append("")
    # 方差分析
    lines.append("方差分析")
    hdr2 = "%-16s %7s %12s %12s %10s %8s %8s" % ('来源', '自由度', 'Seq SS', 'Adj SS', 'Adj MS', 'F', 'P')
    lines.append(hdr2)
    lines.append("-" * len(hdr2))
    # 回归分解
    ss_reg = res.ss_reg
    df_reg = res.df_model
    f_reg = (ss_reg / df_reg) / res.mse if res.mse and res.mse > 0 else np.nan
    p_reg = stats.f.sf(f_reg, df_reg, res.df_error) if res.mse and res.mse > 0 else np.nan
    lines.append("%-16s %7d %12s %12s %10s %8s %8s" % (
        '回归', df_reg, fmt_num(ss_reg), fmt_num(ss_reg),
        fmt_num(ss_reg / df_reg), fmt_num(f_reg), fmt_num(p_reg)))
    # 线性/平方/交互分解（QR 顺序 SS，与 Minitab Seq SS 一致）
    groups = {'线性': 1, '平方': 2, '交互': 3}
    for gname, glen in groups.items():
        idxs = []
        for i, t in enumerate(terms):
            if not t:
                continue
            if glen == 1 and len(t) == 1:
                idxs.append(i)
            elif glen == 2 and len(t) == 2 and t[0] == t[1]:
                idxs.append(i)
            elif glen == 3 and len(t) == 2 and t[0] != t[1]:
                idxs.append(i)
        if not idxs:
            continue
        ss_g = float(sum(seq[i] for i in idxs))
        df_g = len(idxs)
        ms_g = ss_g / df_g
        f_g = ms_g / res.mse if res.mse and res.mse > 0 else np.nan
        p_g = stats.f.sf(f_g, df_g, res.df_error) if res.mse and res.mse > 0 else np.nan
        lines.append("  %-14s %7d %12s %12s %10s %8s %8s" % (
            gname, df_g, fmt_num(ss_g), fmt_num(ss_g), fmt_num(ms_g),
            fmt_num(f_g), fmt_num(p_g)))
    # 残差与失拟
    lines.append("%-16s %7d %12s %12s %10s" % (
        '残差误差', res.df_error, fmt_num(res.ss_res), fmt_num(res.ss_res),
        fmt_num(res.mse)))
    # 纯误差与失拟
    ss_pe, df_pe = _pure_error(df, factor_names, response, Xcs)
    if df_pe > 0:
        ss_lof = max(res.ss_res - ss_pe, 0.0)
        df_lof = res.df_error - df_pe
        ms_pe = ss_pe / df_pe
        f_lof = (ss_lof / df_lof) / ms_pe if (df_lof > 0 and ms_pe > 1e-15) else np.nan
        p_lof = stats.f.sf(f_lof, df_lof, df_pe) if (df_lof > 0 and ms_pe > 1e-15) else np.nan
        lines.append("  失拟        %7d %12s %12s %10s %8s %8s" % (
            df_lof, fmt_num(ss_lof), fmt_num(ss_lof),
            fmt_num(ss_lof / df_lof if df_lof else np.nan), fmt_num(f_lof), fmt_num(p_lof)))
        lines.append("  纯误差      %7d %12s %12s %10s" % (
            df_pe, fmt_num(ss_pe), fmt_num(ss_pe), fmt_num(ms_pe)))
    lines.append("合计          %7d %12s" % (n - 1, fmt_num(res.ss_tot)))
    lines.append("")
    lines.append("模型汇总")
    lines.append("S = %s    R-sq = %s%%    R-sq(调整) = %s%%    R-sq(预测) = %s%%" % (
        fmt_num(np.sqrt(res.mse) if res.mse else np.nan, 6),
        fmt_num(100 * res.r2, 2), fmt_num(100 * res.r2_adj, 2),
        fmt_num(100 * res.r2_pred if not np.isnan(res.r2_pred) else np.nan, 2)))
    lines.append("")

    if print_out:
        for ln in lines:
            print_port(ln)

    return {
        'type': 'rsm', 'factors': factor_names, 'response': response,
        'n': n, 'k': k, 'terms': terms,
        'names': [_term_name(t, letters) for t in terms],
        'coef': res.coef, 'se': res.se, 't': res.t, 'p': res.p,
        'letters': letters, 'Xcs': Xcs, 'y': y, 'enc': enc,
        'mse': res.mse, 'df_error': res.df_error,
        'r2': res.r2, 'r2_adj': res.r2_adj, 'r2_pred': res.r2_pred,
        'resid': res.resid, 'yhat': res.yhat,
        'ss_resid': res.ss_res, 'ss_tot': res.ss_tot,
        'alpha': alpha,
    }


def _pure_error(df, factor_names, response, Xcs=None):
    """计算纯误差 SS 与自由度（重复试验点）"""
    y = df[response].astype(float).values
    ss_pe = 0.0
    df_pe = 0
    grp = df[factor_names].copy()
    grp['__y'] = y
    try:
        for _, sub in grp.groupby(list(factor_names)):
            if len(sub) > 1:
                ss_pe += float(np.sum((sub['__y'].values - sub['__y'].mean()) ** 2))
                df_pe += len(sub) - 1
    except Exception:
        pass
    return ss_pe, df_pe


# =====================================================================
# 四、混料设计分析（Scheffé 多项式）
# =====================================================================

def mixture_analysis(df, comp_names, response, model='linear',
                     print_out=True, print_port=print):
    """混料设计分析（Scheffé 多项式，无截距，与 Minitab 一致）
    model: 'linear'(q项) | 'quadratic'(线性+二元) | 'special-cubic'(二次+三元)
    """
    q = len(comp_names)
    y = df[response].astype(float).values
    n = len(y)
    Xc = np.column_stack([df[c].astype(float).values for c in comp_names])
    # Scheffé 项
    terms = [('x%d' % i,) for i in range(q)]
    names = ['%s' % comp_names[i] for i in range(q)]
    if model in ('quadratic', 'special-cubic'):
        for i in range(q):
            for j in range(i + 1, q):
                terms.append(('x%d' % i, 'x%d' % j))
                names.append('%s*%s' % (comp_names[i], comp_names[j]))
    if model == 'special-cubic':
        for i in range(q):
            for j in range(i + 1, q):
                for l in range(j + 1, q):
                    terms.append(('x%d' % i, 'x%d' % j, 'x%d' % l))
                    names.append('%s*%s*%s' % (comp_names[i], comp_names[j], comp_names[l]))
    # 模型矩阵（无截距）
    Xm = []
    for t in terms:
        col = np.ones(n)
        for s in t:
            col *= Xc[:, int(s[1:])]
        Xm.append(col)
    Xm = np.column_stack(Xm)
    # 无截距 OLS（含截距列做回归后去截距；此处直接用 Xm 无截距）
    coef, _, _, _ = np.linalg.lstsq(Xm, y, rcond=None)
    yhat = Xm @ coef
    resid = y - yhat
    df_model = len(terms)
    df_error = n - df_model
    ss_reg = float(np.sum((yhat - y.mean()) ** 2))
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    mse = ss_res / df_error if df_error > 0 else np.nan
    XtX = Xm.T @ Xm
    XtXinv = np.linalg.pinv(XtX)
    se = np.sqrt(np.diag(XtXinv) * mse) if df_error > 0 else np.full(len(terms), np.nan)
    t = coef / se if df_error > 0 else np.full(len(terms), np.nan)
    p = 2 * (1 - stats.t.cdf(np.abs(t), df_error)) if df_error > 0 else np.full(len(terms), np.nan)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    r2_adj = 1 - (1 - r2) * (n - 1) / df_error if df_error > 0 else np.nan
    f_reg = (ss_reg / df_model) / mse if mse and mse > 0 else np.nan
    p_reg = stats.f.sf(f_reg, df_model, df_error) if mse and mse > 0 else np.nan

    lines = []
    lines.append("=" * 62)
    lines.append("混料回归: %s 与 %s" % (response, ', '.join(comp_names)))
    lines.append("=" * 62)
    lines.append("")
    lines.append("系数估计（Scheffé 模型: %s）" % model)
    hdr = "%-18s %12s %14s %10s %8s" % ('项', '系数', '系数标准误', 'T', 'P')
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for i, nm in enumerate(names):
        lines.append("%-18s %12s %14s %10s %8s" % (
            nm, fmt_num(coef[i]), fmt_num(se[i]), fmt_num(t[i]), fmt_num(p[i])))
    lines.append("")
    lines.append("方差分析")
    hdr2 = "%-18s %7s %12s %12s %10s %8s %8s" % ('来源', '自由度', 'Seq SS', 'Adj SS', 'Adj MS', 'F', 'P')
    lines.append(hdr2)
    lines.append("-" * len(hdr2))
    lines.append("%-18s %7d %12s %12s %10s %8s %8s" % (
        '回归', df_model, fmt_num(ss_reg), fmt_num(ss_reg),
        fmt_num(ss_reg / df_model), fmt_num(f_reg), fmt_num(p_reg)))
    lines.append("%-18s %7d %12s %12s %10s" % (
        '残差误差', df_error, fmt_num(ss_res), fmt_num(ss_res), fmt_num(mse)))
    lines.append("合计          %7d %12s" % (n - 1, fmt_num(ss_tot)))
    lines.append("")
    lines.append("模型汇总")
    lines.append("S = %s    R-sq = %s%%    R-sq(调整) = %s%%" % (
        fmt_num(np.sqrt(mse) if mse else np.nan, 6),
        fmt_num(100 * r2, 2), fmt_num(100 * r2_adj, 2)))
    lines.append("")

    if print_out:
        for ln in lines:
            print_port(ln)

    return {
        'type': 'mixture', 'comps': comp_names, 'response': response,
        'n': n, 'q': q, 'terms': terms, 'names': names,
        'coef': coef, 'se': se, 't': t, 'p': p,
        'Xc': Xc, 'y': y, 'mse': mse, 'df_error': df_error,
        'r2': r2, 'r2_adj': r2_adj, 'resid': resid, 'yhat': yhat,
        'ss_resid': ss_res, 'ss_tot': ss_tot, 'model': model,
    }


# =====================================================================
# 五、田口设计分析（S/N 比）
# =====================================================================

def sn_ratio(values, sn_type='larger'):
    """信噪比 S/N (dB)
    sn_type: 'larger'(望大) | 'smaller'(望小) | 'nominal'(望目)
    望大: S/N = -10·log10( Σ(1/y²)/n )
    望小: S/N = -10·log10( Σ(y²)/n )
    望目: S/N = 10·log10( ȳ² / s² )
    """
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    n = len(v)
    if n == 0:
        return np.nan
    if sn_type == 'larger':
        if np.any(v <= 0):
            return np.nan
        return -10.0 * np.log10(np.sum(1.0 / (v ** 2)) / n)
    elif sn_type == 'smaller':
        return -10.0 * np.log10(np.sum(v ** 2) / n)
    elif sn_type == 'nominal':
        m = v.mean()
        s2 = v.var(ddof=1)
        if s2 <= 0 or m == 0:
            return np.nan
        return 10.0 * np.log10(m ** 2 / s2)
    raise ValueError("sn_type 须为 larger/smaller/nominal")


def taguchi_analysis(df, factor_names, response, sn_type='larger',
                     print_out=True, print_port=print):
    """静态田口分析：S/N 比 + 均值/标准差 + 响应表"""
    k = len(factor_names)
    y = df[response].astype(float).values
    n = len(y)
    # 按因子组合分组计算 S/N
    grp = df[factor_names].copy()
    grp['__y'] = y
    sn_vals = {}
    mean_vals = {}
    std_vals = {}
    combos = []
    for key, sub in grp.groupby(list(factor_names)):
        yy = sub['__y'].values
        combos.append(key)
        sn_vals[key] = sn_ratio(yy, sn_type)
        mean_vals[key] = float(np.mean(yy))
        std_vals[key] = float(np.std(yy, ddof=1)) if len(yy) > 1 else np.nan

    sn_label = {'larger': '望大', 'smaller': '望小', 'nominal': '望目'}[sn_type]
    lines = []
    lines.append("=" * 62)
    lines.append("田口分析: %s（信噪比: %s）" % (response, sn_label))
    lines.append("=" * 62)
    lines.append("")
    # 响应表 for S/N
    lines.append("信噪比响应表（S/N 比, %s）" % sn_label)
    hdr = "%-10s" % '水平'
    for f in factor_names:
        hdr += " %-12s" % f
    lines.append(hdr)
    for lv in ['1', '2', '3']:
        row = "%-10s" % lv
        for f in factor_names:
            vals = [sn_vals[key] for key in combos
                    if str(key[factor_names.index(f)]) == lv]
            if vals:
                row += " %-12s" % fmt_num(float(np.mean(vals)), 4)
            else:
                row += " %-12s" % ''
        lines.append(row)
    # 极差
    row = "%-10s" % 'Delta'
    for f in factor_names:
        lvs = []
        for lv in ['1', '2', '3']:
            vals = [sn_vals[key] for key in combos
                    if str(key[factor_names.index(f)]) == lv]
            if vals:
                lvs.append(float(np.mean(vals)))
        if lvs:
            row += " %-12s" % fmt_num(max(lvs) - min(lvs), 4)
        else:
            row += " %-12s" % ''
    lines.append(row)
    lines.append("")
    # 响应表 for 均值
    lines.append("均值响应表")
    hdr = "%-10s" % '水平'
    for f in factor_names:
        hdr += " %-12s" % f
    lines.append(hdr)
    for lv in ['1', '2', '3']:
        row = "%-10s" % lv
        for f in factor_names:
            vals = [mean_vals[key] for key in combos
                    if str(key[factor_names.index(f)]) == lv]
            if vals:
                row += " %-12s" % fmt_num(float(np.mean(vals)), 4)
            else:
                row += " %-12s" % ''
        lines.append(row)
    row = "%-10s" % 'Delta'
    for f in factor_names:
        lvs = []
        for lv in ['1', '2', '3']:
            vals = [mean_vals[key] for key in combos
                    if str(key[factor_names.index(f)]) == lv]
            if vals:
                lvs.append(float(np.mean(vals)))
        if lvs:
            row += " %-12s" % fmt_num(max(lvs) - min(lvs), 4)
        else:
            row += " %-12s" % ''
    lines.append(row)
    lines.append("")
    lines.append("各试验组合的 S/N 比与均值：")
    hdr3 = "%-4s" % '试验'
    for f in factor_names:
        hdr3 += " %-6s" % f
    hdr3 += " %-10s %-10s %-10s" % ('S/N', '均值', '标准差')
    lines.append(hdr3)
    for i, key in enumerate(combos, 1):
        row = "%-4d" % i
        for f in factor_names:
            row += " %-6s" % str(key[factor_names.index(f)])
        row += " %-10s %-10s %-10s" % (
            fmt_num(sn_vals[key], 4), fmt_num(mean_vals[key], 4),
            fmt_num(std_vals[key], 4))
        lines.append(row)
    lines.append("")

    if print_out:
        for ln in lines:
            print_port(ln)

    return {
        'type': 'taguchi', 'factors': factor_names, 'response': response,
        'sn_type': sn_type, 'sn_vals': sn_vals, 'mean_vals': mean_vals,
        'std_vals': std_vals, 'combos': combos, 'n': n,
    }


# =====================================================================
# 六、响应优化器辅助：预测函数
# =====================================================================

def predict_rsm(fit, x_vec):
    """按拟合结果预测（编码空间/原始尺度由 fit['enc'] 决定）
    fit: rsm_analysis 返回值; x_vec: 因子值（与建模输入同尺度）
    """
    k = fit['k']
    enc = fit.get('enc')
    x = np.array(x_vec, dtype=float)
    xs = np.zeros(k)
    for j in range(k):
        if enc is None:
            xs[j] = x[j]
        elif enc[j] == 'asis':
            xs[j] = x[j]          # 已是编码
        else:
            lo, hi = enc[j]
            if abs(hi - lo) < 1e-12:
                xs[j] = 0.0
            else:
                xs[j] = 2 * (x[j] - lo) / (hi - lo) - 1
    terms = fit['terms']
    row = [1.0]
    for t in terms:
        if not t:
            continue
        val = 1.0
        for j in t:
            val *= xs[j]
        row.append(val)
    row = np.array(row)
    return float(row @ fit['coef'])


def predict_factorial(fit, x_vec):
    """按因子分析拟合预测"""
    k = fit['k']
    Xc = fit['Xc']
    x = np.array(x_vec, dtype=float)
    xs = np.zeros(k)
    for j in range(k):
        v = Xc[:, j]
        xs[j] = x[j]  # 已编码
    terms = fit['terms']
    row = [1.0]
    for t in terms:
        if not t:
            continue
        val = 1.0
        for j in t:
            val *= xs[j]
        row.append(val)
    return float(np.array(row) @ fit['coef'])
