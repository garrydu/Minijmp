# -*- coding: utf-8 -*-
# ============================================================
# 贡献者 / Contributors
#   胡志东 (Nico HU) <Hzd378747710@outlook.com>
#   - DOE 模块: 响应优化器 (2026-08)
# ============================================================
"""响应优化器（意愿函数 Desirability）
=========================================================
复刻 Minitab 响应优化器。公式：
  Derringer & Suich (1980) 个体意愿函数
  复合意愿 = 加权几何平均: D = (Π dᵢ^wᵢ)^(1/Σwᵢ)
搜索：网格粗搜 + 局部精化（Nelder-Mead）+ 多起点
=========================================================
"""
import numpy as np
from scipy.optimize import minimize


def individual_desirability(y, goal, low=None, target=None, high=None, weight=1.0):
    """个体意愿函数 d (0~1)
    goal: 'larger'(望大) | 'smaller'(望小) | 'target'(望目)
    low: 下限(L); target: 目标(T); high: 上限(U); weight: 权重 r
    望大: d=0 (y<=L); ((y-L)/(T-L))^r (L<y<T); 1 (y>=T)
    望小: d=1 (y<=T); ((y-U)/(T-U))^r (T<y<U); 0 (y>=U)
    望目: 0 (y<=L 或 y>=U); ((y-L)/(T-L))^r1 (L<y<T); ((y-U)/(T-U))^r2 (T<y<U)
    """
    y = float(y)
    if goal == 'larger':
        if low is None or target is None:
            raise ValueError("望大需指定 下限 和 目标")
        if y <= low:
            return 0.0
        if y >= target:
            return 1.0
        if abs(target - low) < 1e-12:
            return 1.0
        return ((y - low) / (target - low)) ** weight
    elif goal == 'smaller':
        if high is None or target is None:
            raise ValueError("望小需指定 上限 和 目标")
        if y <= target:
            return 1.0
        if y >= high:
            return 0.0
        if abs(high - target) < 1e-12:
            return 0.0
        return ((y - high) / (target - high)) ** weight
    elif goal == 'target':
        if low is None or high is None or target is None:
            raise ValueError("望目需指定 下限、目标、上限")
        if y <= low or y >= high:
            return 0.0
        if y <= target:
            if abs(target - low) < 1e-12:
                return 1.0
            return ((y - low) / (target - low)) ** weight
        else:
            if abs(high - target) < 1e-12:
                return 0.0
            return ((y - high) / (target - high)) ** weight
    raise ValueError("goal 须为 larger/smaller/target")


def composite_desirability(ds, weights):
    """复合意愿 D = (Π dᵢ^wᵢ)^(1/Σwᵢ)"""
    ds = np.asarray(ds, dtype=float)
    ws = np.asarray(weights, dtype=float)
    # 任一 d=0 则整体为 0
    if np.any(ds <= 0):
        return 0.0
    return float(np.prod(ds ** ws) ** (1.0 / np.sum(ws)))


class ResponseSpec:
    """单个响应的优化规格"""
    def __init__(self, name, fit, goal, low=None, target=None, high=None,
                 weight=1.0, importance=1.0):
        self.name = name
        self.fit = fit                      # 拟合结果 dict (来自 analyze)
        self.goal = goal
        self.low = low
        self.target = target
        self.high = high
        self.weight = weight                # 意愿权重 r
        self.importance = importance        # 重要性 w (复合权重)


def _predict(fit, x):
    """统一预测入口：根据 fit['type'] 调用对应预测"""
    t = fit.get('type')
    if t == 'rsm':
        from .analyze import predict_rsm
        return predict_rsm(fit, x)
    elif t == 'factorial':
        from .analyze import predict_factorial
        return predict_factorial(fit, x)
    elif t == 'mixture':
        # 混料：x 为分量比例，直接模型矩阵
        Xc = fit['Xc']
        row = [1.0]
        for term in fit['terms']:
            val = 1.0
            for s in term:
                val *= x[int(s[1:])]
            row.append(val)
        return float(np.array(row) @ fit['coef'])
    return float(fit['coef'][0])


def optimize(specs, bounds, n_grid=21, n_start=8, seed=42, print_out=True, print_port=print):
    """响应优化器
    specs: [ResponseSpec, ...]
    bounds: 每个因子的 (下限, 上限) 列表（原始尺度）
    n_grid: 网格粗搜每维点数
    n_start: 多起点数
    返回 dict: {'best_x': [...], 'predicted': [...], 'desirability': [...],
                'composite': D, 'history': [...]}
    """
    k = len(bounds)
    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([b[1] for b in bounds], dtype=float)

    def D(x):
        x = np.clip(np.asarray(x, dtype=float), lo, hi)
        ds = []
        for s in specs:
            yp = _predict(s.fit, x)
            ds.append(individual_desirability(
                yp, s.goal, s.low, s.target, s.high, s.weight))
        return composite_desirability(ds, [s.importance for s in specs])

    def negD(x):
        return -D(x)

    rng = np.random.default_rng(seed)
    # 1) 网格粗搜
    best_x = None
    best_D = -1
    grid_pts = [np.linspace(lo[j], hi[j], n_grid) for j in range(k)]
    import itertools
    # 网格点数过多时随机采样
    total = int(np.prod([n_grid] * k))
    if total <= 20000:
        for pt in itertools.product(*grid_pts):
            d = D(pt)
            if d > best_D:
                best_D = d
                best_x = np.array(pt, dtype=float)
    else:
        for _ in range(20000):
            pt = lo + rng.random(k) * (hi - lo)
            d = D(pt)
            if d > best_D:
                best_D = d
                best_x = pt

    # 2) 局部精化（Nelder-Mead 多起点）
    starts = [best_x]
    for _ in range(n_start - 1):
        starts.append(lo + rng.random(k) * (hi - lo))
    for s0 in starts:
        res = minimize(negD, s0, method='Nelder-Mead',
                       bounds=[(b[0], b[1]) for b in bounds],
                       options={'xatol': 1e-8, 'fatol': 1e-10, 'maxiter': 2000})
        d = D(res.x)
        if d > best_D:
            best_D = d
            best_x = np.clip(res.x, lo, hi)

    # 3) 输出
    preds = [_predict(s.fit, best_x) for s in specs]
    ds = [individual_desirability(
        preds[i], specs[i].goal, specs[i].low, specs[i].target, specs[i].high,
        specs[i].weight) for i in range(len(specs))]
    comp = composite_desirability(ds, [s.importance for s in specs])

    if print_out:
        print_port("=" * 62)
        print_port("响应优化器结果")
        print_port("=" * 62)
        print_port("")
        print_port("最优因子设置:")
        for j in range(k):
            print_port("  %s = %s" % (specs[0].fit.get('letters', ['F%d' % (j + 1)])[j] if isinstance(specs[0].fit.get('letters'), list) and len(specs[0].fit.get('letters')) > j else 'F%d' % (j + 1),
                                      ('%.6f' % best_x[j]).rstrip('0').rstrip('.')))
        print_port("")
        print_port("预测响应与意愿:")
        print_port("  %-14s %-12s %-12s %-10s" % ('响应', '预测值', '个体意愿', '目标'))
        for i, s in enumerate(specs):
            print_port("  %-14s %-12s %-12s %-10s" % (
                s.name, ('%.6f' % preds[i]).rstrip('0').rstrip('.'),
                ('%.6f' % ds[i]).rstrip('0').rstrip('.'),
                {'larger': '望大', 'smaller': '望小', 'target': '望目'}[s.goal]))
        print_port("")
        print_port("复合意愿 D = %s" % ('%.6f' % comp).rstrip('0').rstrip('.'))
        print_port("")

    return {'best_x': best_x, 'predicted': preds, 'desirability': ds,
            'composite': comp}


def optimize_plot_data(specs, bounds, best_x, n_pts=31):
    """生成优化图数据：固定其他因子在最优值，单因子扫描预测与复合意愿
    返回: (因子名列表, 每个因子的 {x轴, 预测[y1..ym], 意愿}), 复合意愿序列
    """
    k = len(bounds)
    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([b[1] for b in bounds], dtype=float)
    result = []
    for j in range(k):
        xs = np.linspace(lo[j], hi[j], n_pts)
        preds = {s.name: [] for s in specs}
        Ds = []
        for xv in xs:
            x = np.array(best_x, dtype=float)
            x[j] = xv
            for s in specs:
                preds[s.name].append(_predict(s.fit, x))
            ds = [individual_desirability(preds[s.name][-1], s.goal, s.low, s.target, s.high, s.weight)
                  for s in specs]
            Ds.append(composite_desirability(ds, [s.importance for s in specs]))
        result.append({'factor': j, 'x': xs, 'preds': preds, 'D': Ds})
    return result
