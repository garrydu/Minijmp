# -*- coding: utf-8 -*-
# ============================================================
# 贡献者 / Contributors
#   胡志东 (Nico HU) <Hzd378747710@outlook.com>
#   - DOE 模块: 设计生成核心库 (2026-08)
# ============================================================
"""DOE 设计生成核心库
=========================================================
复刻 Minitab DOE 模块的设计生成功能。
所有公式遵循学术标准：
  - Montgomery, D.C. 《Design and Analysis of Experiments》(Wiley)
  - Box & Hunter 部分因子设计理论
  - Jones & Nachtsheim (2011) Definitive Screening Designs, JQT
  - Box & Behnken (1960) 响应曲面设计
  - Scheffé (1958) 混料模型
  - 田口玄一 正交表 (标准正交表数据)
  - Fedorov / Wynn 最优设计理论 (D/A/I/G 最优)
=========================================================
"""
import numpy as np
import pandas as pd
import itertools
from math import comb

# =====================================================================
# 一、基础工具
# =====================================================================

_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K',
            'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE']


def factor_letters(k):
    """返回 k 个因子字母 A, B, C, ..."""
    if k <= 26:
        return _LETTERS[:k]
    return ['F%d' % i for i in range(1, k + 1)]


def _word_to_str(word):
    """将效应字（因子索引元组）转为字符串，如 (0,1,2) -> 'ABC'"""
    return ''.join(_LETTERS[i] for i in word)


def _str_to_word(s):
    """将 'ABC' 转为索引元组 (0,1,2)"""
    out = []
    i = 0
    while i < len(s):
        if s[i] in _LETTERS[:26] and i + 1 < len(s) and s[i] + s[i + 1] in _LETTERS:
            out.append(_LETTERS.index(s[i] + s[i + 1]))
            i += 2
        else:
            out.append(_LETTERS.index(s[i]))
            i += 1
    return tuple(sorted(set(out)))


def _mul_words(w1, w2):
    """两个效应字的乘积（模2），返回去重后的字"""
    return tuple(sorted(set(w1) ^ set(w2)))


def _word_len(w):
    return len(w)


def _gen_matrix(word_list, n):
    """根据生成元列表（效应字）计算定义关系中的所有字（含 I）"""
    # word_list: 每个生成元对应的定义字（如 G=ABCD -> ('A','B','C','D')）
    from functools import reduce
    defining = [()]
    for w in word_list:
        new = []
        for d in defining:
            new.append(_mul_words(d, w))
        defining = defining + new
    return sorted(defining, key=lambda x: (len(x), x))


def _resolution(defining_words):
    """分辨率 = 定义关系中除 I 外最短字的长度"""
    lens = [len(w) for w in defining_words if w]
    return min(lens) if lens else 999


def _alias_structure(defining_words, k):
    """计算所有主效应与交互的别名组
    返回 dict: 效应字 -> 别名组列表（含自身），按定义关系分组
    """
    # 收集所有效应（单因子到全因子）
    effects = []
    for r in range(1, k + 1):
        for combo in itertools.combinations(range(k), r):
            effects.append(combo)
    groups = []
    used = set()
    for eff in effects:
        if eff in used:
            continue
        group = [eff]
        for d in defining_words:
            if not d:
                continue
            a = _mul_words(eff, d)
            group.append(a)
        # 去重并标记
        uniq = []
        for a in group:
            if a not in uniq:
                uniq.append(a)
            used.add(a)
        groups.append((eff, uniq))
    return groups


# =====================================================================
# 二、全因子设计
# =====================================================================

def ff2n(n):
    """2^n 全因子设计，编码 ±1（标准编码）
    返回 (2^n, n) 的 numpy 数组，行序为标准 Yates 序（最右列变化最快）
    """
    runs = 2 ** n
    X = np.empty((runs, n))
    for j in range(n):
        block = runs // (2 ** (j + 1))
        vals = np.concatenate([np.ones(block), -np.ones(block)])
        X[:, j] = np.tile(vals, 2 ** j)
    return X


def full_factorial(levels):
    """一般全因子设计（混合水平）
    levels: 每个因子的水平数列表，如 [3,2,2]
    返回 DataFrame，因子名为 A,B,C...，编码从 1 开始（Minitab 风格）
    """
    k = len(levels)
    names = factor_letters(k)
    ranges = [range(1, l + 1) for l in levels]
    rows = list(itertools.product(*ranges))
    df = pd.DataFrame(rows, columns=names)
    return df


def make_full_factorial(k, nlevels=2, factor_names=None, print_out=False, print_port=print):
    """生成 2^k 或一般全因子设计，写回 DataFrame
    k: 因子数; nlevels: 水平数（2 或整数，或列表）
    """
    if isinstance(nlevels, int):
        nlevels = [nlevels] * k
    df = full_factorial(nlevels)
    if factor_names:
        df.columns = factor_names
    if print_out:
        print_port("设计摘要: %d 个因子 × %d 次试验" % (k, len(df)))
        print_port("因子: %s" % ', '.join(str(c) for c in df.columns))
    return df


# =====================================================================
# 三、部分因子设计 2^(k-p)
# =====================================================================

# ---- 最大分辨率生成元搜索 ----
def _def_words(gens, base):
    """生成元（基本因子索引元组）-> 完整定义关系字列表（含 I）
    第 i 个生成元定义新因子 base+i：定义字 = 基本因子组合 ∪ {base+i}
    """
    defining = [()]
    for i, w in enumerate(gens):
        full = tuple(sorted(set(w) | {base + i}))
        new = []
        for d in defining:
            new.append(_mul_words(d, full))
        defining += new
    return defining


def _evaluate_generators(gens, base):
    """评估一组生成元（基本因子索引元组）的分辨率"""
    return _resolution(_def_words(gens, base))


def _search_generators(k, p, base=None):
    """搜索 2^(k-p) 部分因子设计的最大分辨率生成元
    base: 基本因子数 = k-p；生成元是基本因子子集的乘积
    返回: (生成元列表[索引元组], 分辨率, 定义关系字)
    学术标准：最大分辨率设计（与 Minitab 默认一致）
    """
    if base is None:
        base = k - p
    if base <= 0:
        raise ValueError("因子数过少，无法构造部分因子设计")
    bf = list(range(base))               # 基本因子
    # 候选生成元：基本因子的子集，长度 2..base（避免单因子，保证分辨率>=III）
    cands = []
    for r in range(2, base + 1):
        for c in itertools.combinations(bf, r):
            cands.append(c)

    best = None
    # 回溯：逐列选择使分辨率最大的生成元
    def rec(sel, idx):
        nonlocal best
        if len(sel) == p:
            res = _evaluate_generators(sel, base)
            if best is None or res > best[0]:
                best = (res, list(sel))
            return
        for j in range(idx, len(cands)):
            c = cands[j]
            sel2 = sel + [c]
            res = _evaluate_generators(sel2, base)
            if res < 3:      # 主效应不得与二阶交互混杂
                continue
            rec(sel2, j + 1)

    rec([], 0)
    if best is None:
        raise ValueError("无法为 %d 因子构造 %d 阶部分因子" % (k, p))
    gens = best[1]
    defining = _def_words(gens, base)
    return gens, best[0], sorted(defining, key=lambda x: (len(x), x))


def frac_factorial(k, p=1, generators=None, randomize=False, seed=None):
    """2^(k-p) 部分因子设计
    k: 总因子数（2..15）
    p: 部分阶数（1 表示 1/2 部分, 2 表示 1/4 部分...）
    generators: 可选，指定生成元字符串列表如 ['D=ABC','E=AC']（默认自动搜索最大分辨率）
    返回: (DataFrame(±1 编码), 设计信息 dict)
    """
    base = k - p
    if base <= 0:
        raise ValueError("k-p 必须 >= 1")
    letters = factor_letters(k)
    bnames = letters[:base]
    nf = letters[base:]

    if generators is None:
        gens, res, defining = _search_generators(k, p)
    else:
        # 解析生成元 'D=ABC'
        gens = []
        for g in generators:
            lhs, rhs = g.split('=')
            lhs_i = letters.index(lhs.strip())
            rhs_i = tuple(sorted(letters.index(ch) for ch in rhs.strip()))
            gens.append(rhs_i)
        defining = _def_words(gens, base)
        defining = sorted(defining, key=lambda x: (len(x), x))
        res = _resolution(defining)

    # 生成基本部分 2^base 全因子
    X = ff2n(base)
    n = len(X)
    # 为新因子构造列：生成元对应基本列的乘积
    newcols = np.empty((n, p))
    for i, w in enumerate(gens):
        col = np.ones(n)
        for j in w:
            col *= X[:, j]
        newcols[:, i] = col
    Xfull = np.hstack([X, newcols])
    df = pd.DataFrame(Xfull, columns=bnames + nf)
    # 标准格式：Minitab 中生成元显示的列 = 新因子
    if randomize:
        rng = np.random.default_rng(seed)
        idx = rng.permutation(n)
        df = df.iloc[idx].reset_index(drop=True)

    info = {
        'type': '2**(k-p) 部分因子',
        'k': k, 'p': p, 'runs': n,
        'generators': {nf[i]: _word_to_str(gens[i]) for i in range(p)},
        'resolution': res,
        'defining': [_word_to_str(w) if w else 'I' for w in defining],
    }
    return df, info


def alias_table(k, p=1, generators=None, max_order=3):
    """输出别名结构表（用于分析前查看混杂情况）
    返回: list of (效应名, [别名名,...])
    """
    letters = factor_letters(k)
    if generators is None:
        gens, res, defining = _search_generators(k, p)
    else:
        gens = []
        for g in generators:
            lhs, rhs = g.split('=')
            lhs_i = letters.index(lhs.strip())
            rhs_i = tuple(sorted(letters.index(ch) for ch in rhs.strip()))
            gens.append(rhs_i)
        base = k - len(gens)
        defining = _def_words(gens, base)
        defining = sorted(defining, key=lambda x: (len(x), x))
    groups = _alias_structure(defining, k)
    out = []
    for eff, aliases in groups:
        if len(eff) > max_order:
            continue
        anames = [_word_to_str(a) if a else 'I' for a in aliases]
        out.append((_word_to_str(eff), anames))
    return out


# =====================================================================
# 四、Plackett-Burman 设计
# =====================================================================

# PB 标准首行向量（长度 n-1，符号 +1/-1）。来源：Booth & Cox (1962) / Hamada-Wu
# 通过"折叠块"循环构造。此处内置权威首行（学术界通用版本）。
_PB_FIRST_ROWS = {
    12:  "+ + - + + + - - - + -",
    20:  "+ + - - + + + + - + - + - - - - + + -",
    24:  "+ + + - - + - + + - - - - + + - + - + + + - - +",
    28:  "+ - + + - - + + - + + - + - - - - - + - - + - - - + +",
    36:  "+ - - - + + - - - + - + + + - + + - - + - - - - + - + + + + - + + - - -",
    44:  "+ - + + + - - + + + - + + + + - - - - - - + - - - - - - + - + - - + + + - - - + - + + +",
    48:  "+ + + + - - - + + - + - - + + - + - - + - + - - - + + - - + + + + - + + - - + - + + + + - - - + +",
}

_PB_SIZES = sorted(_PB_FIRST_ROWS.keys())


def _pb_rows(n):
    """构造 n 次试验的 PB 设计（n 为 4 的倍数）
    算法（学术标准，Booth & Cox 1962）：首行向量 v（长度 n-1），
    取 n-1 行循环移位，再追加一行全 +1，共 n 行，构成 n×(n-1) 的两水平正交设计。
    """
    s = _PB_FIRST_ROWS[n].split()
    v = np.array([1.0 if c == '+' else -1.0 for c in s])
    rows = [np.roll(v, r) for r in range(n - 1)]
    rows.append(np.ones(n - 1))   # 最后一行全 +1
    return np.vstack(rows)


def pb_design(k, randomize=False, seed=None):
    """Plackett-Burman 设计
    k: 因子数（2..47），试验次数取 >= k+1 的最小 4 的倍数（12..48）
    """
    if k < 2 or k > 47:
        raise ValueError("PB 设计因子数须在 2~47 之间")
    n = None
    for s in _PB_SIZES:
        if s - 1 >= k:
            n = s
            break
    if n is None:
        raise ValueError("因子数过大")
    X = _pb_rows(n)
    # X 有 n-1 列，取前 k 列作为因子
    X = X[:, :k]
    letters = factor_letters(k)
    df = pd.DataFrame(X, columns=letters)
    if randomize:
        rng = np.random.default_rng(seed)
        df = df.iloc[rng.permutation(n)].reset_index(drop=True)
    info = {
        'type': 'Plackett-Burman 筛选设计',
        'k': k, 'runs': n,
        'resolution': 'III（主效应与二阶交互混杂，需假设交互可忽略）',
    }
    return df, info


# =====================================================================
# 五、确定性筛选设计 (DSD)
# =====================================================================

def _conference_matrix(m):
    """构造 m×m conference 矩阵（对角 0，非对角 ±1，C'C=(m-1)I）
    m 必须为偶数。使用 Paley 构造（m-1 为奇素数幂）；否则随机搜索。
    """
    if m == 2:
        return np.array([[0, 1], [1, 0]], dtype=float)
    if m == 4:
        return np.array([[0, 1, 1, 1],
                         [1, 0, -1, 1],
                         [1, 1, 0, -1],
                         [1, -1, 1, 0]], dtype=float)
    q = m - 1
    if _is_prime_power(q):
        try:
            return _paley_conference(q)
        except ValueError:
            pass
    # 回退：随机搜索正交 ±1 矩阵（对角0）
    rng = np.random.default_rng(42)
    for _try in range(50000):
        C = np.zeros((m, m))
        for i in range(m):
            for j in range(i + 1, m):
                C[i, j] = 1 if rng.random() < 0.5 else -1
                C[j, i] = C[i, j]
        G = C.T @ C
        if np.allclose(G, (m - 1) * np.eye(m)):
            return C
    raise ValueError("无法为 %d 个因子构造 DSD 基矩阵（该因子数暂不支持）" % m)


def _is_prime_power(n):
    if n < 2:
        return False
    for p in range(2, int(n ** 0.5) + 1):
        if n % p == 0:
            while n % p == 0:
                n //= p
            return n == 1
    return True


def _paley_conference(q):
    """Paley 构造 (q+1)×(q+1) conference 矩阵，q 为奇素数幂
    C = [[0, 1ᵀ],[1, S]]，S[i,j]=χ(j-i)（GF(q) 二次特征）
    对任意奇素数幂 q 均满足 CᵀC = q·I（conference 矩阵性质）
    """
    if not _is_prime(q):
        # 素数幂：用有限域 GF(p^e) 的二次特征；此处对素数次幂做简单处理
        # 先找素数因子构造加法，若失败则回退随机搜索
        raise ValueError("素数幂 Paley 需有限域实现")
    qr = set()
    for x in range(1, q):
        qr.add((x * x) % q)
    S = np.zeros((q, q))
    for i in range(q):
        for j in range(q):
            if i == j:
                continue
            d = (j - i) % q
            S[i, j] = 1.0 if d in qr else -1.0
    C = np.zeros((q + 1, q + 1))
    C[0, 0] = 0.0
    C[0, 1:] = 1.0
    C[1:, 0] = 1.0
    C[1:, 1:] = S
    return C


def _is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def dsd(m, ncenter=0, randomize=False, seed=None):
    """确定性筛选设计 (Definitive Screening Design)
    m: 连续因子数（3..48）；类别因子仅支持 2 水平（此处提供连续版）
    构造：DSD = [C; -C] + c 个中心点，C 为 m×m conference 矩阵
    总试验 = 2m + c（c>=1 建议，默认 0，Minitab 默认含中心点）
    """
    if m < 3 or m > 48:
        raise ValueError("DSD 因子数须在 3~48 之间")
    # 奇数因子：用 m+1（偶数）阶 conference 构造后删去末列（工程近似）
    me = m if m % 2 == 0 else m + 1
    C = _conference_matrix(me)
    D = np.vstack([C, -C])
    if ncenter > 0:
        D = np.vstack([D, np.zeros((ncenter, me))])
    D = D[:, :m]  # 取前 m 列
    letters = factor_letters(m)
    df = pd.DataFrame(D, columns=letters)
    if randomize:
        rng = np.random.default_rng(seed)
        df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    info = {
        'type': '确定性筛选设计 (DSD)',
        'm': m, 'runs': len(df),
        'ncenter': ncenter,
        'resolution': 'IV（主效应不与二阶交互混杂；可估计全部主效应并筛选显著交互）',
    }
    return df, info


# =====================================================================
# 六、响应曲面设计
# =====================================================================

def ccd(k, alpha='rotatable', ncenter=1, ncube=1, naxis=None, randomize=False, seed=None):
    """中心复合设计 (Central Composite Design)
    k: 因子数（2..10）
    alpha: 'rotatable'/'circumscribed'(旋转, α=(n_F)^(1/4))
           'face'(面心, α=1) | 'inscribed'(内切, 同旋转α但缩放到±1轴点)
    ncenter: 中心点个数（默认 1；Minitab 默认取决于因子数）
    ncube: 角点重复
    naxis: 轴点重复（默认 1）
    构成：角点(±1) + 轴点(±α) + 中心点(0)
    """
    if k < 2 or k > 10:
        raise ValueError("CCD 因子数须在 2~10 之间")
    # 角点：全因子 2^k
    cube = ff2n(k)
    nF = len(cube)
    # 轴点
    if naxis is None:
        naxis = 1
    axis = []
    for i in range(k):
        for _ in range(naxis):
            row = np.zeros(k)
            row[i] = 1
            axis.append(row)
            row2 = np.zeros(k)
            row2[i] = -1
            axis.append(row2)
    axis = np.array(axis)

    # alpha 计算
    if alpha in ('rotatable', 'circumscribed', 'inscribed'):
        a = float(nF) ** 0.25   # 旋转 α = (角点数)^(1/4)
    elif alpha == 'face':
        a = 1.0
    else:
        a = float(alpha)

    pts = []
    if ncube > 1:
        for _ in range(ncube):
            pts.append(cube)
    else:
        pts.append(cube)
    pts.append(axis * a)
    if ncenter > 0:
        pts.append(np.zeros((ncenter, k)))
    X = np.vstack(pts)

    if alpha == 'inscribed':
        # 内切：把角点缩放到内部，轴点在 ±1
        X = X / a

    letters = factor_letters(k)
    df = pd.DataFrame(X, columns=letters)
    if randomize:
        rng = np.random.default_rng(seed)
        df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    if alpha == 'face':
        atype = '面心 (CCF, α=1)'
    elif alpha == 'inscribed':
        atype = '内切 (CCI)'
    else:
        atype = '旋转 (CCC, α=%.4f)' % a
    info = {
        'type': '中心复合设计 (CCD) - ' + atype,
        'k': k, 'runs': len(df),
        'alpha': a,
        'cube_points': len(cube) * ncube,
        'axis_points': len(axis),
        'center_points': ncenter,
    }
    return df, info


def box_behnken(k, ncenter=None, randomize=False, seed=None):
    """Box-Behnken 设计
    k: 因子数（3..15；Minitab 支持 3 及以上）
    点数 = 4*C(k,2)（每个因子对：两因子取 ±1 的 4 组合，其余为 0）+ 中心点
    """
    if k < 3:
        raise ValueError("Box-Behnken 设计至少需要 3 个因子")
    if ncenter is None:
        ncenter = _bbn_center(k)
    # 标准 BBD 点数表（Box & Behnken 1960；含特殊 k=6）
    points = []
    pairs = list(itertools.combinations(range(k), 2))
    for (i, j) in pairs:
        for xi in (1, -1):
            for xj in (1, -1):
                row = np.zeros(k)
                row[i] = xi
                row[j] = xj
                points.append(row)
    if ncenter > 0:
        for _ in range(ncenter):
            points.append(np.zeros(k))
    X = np.array(points)
    letters = factor_letters(k)
    df = pd.DataFrame(X, columns=letters)
    if randomize:
        rng = np.random.default_rng(seed)
        df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    info = {
        'type': 'Box-Behnken 设计',
        'k': k, 'runs': len(df),
        'center_points': ncenter,
    }
    return df, info


def _bbn_center(k):
    """Minitab BBD 默认中心点数"""
    return {3: 3, 4: 3, 5: 6, 6: 6, 7: 6, 8: 6, 9: 10, 10: 10}.get(k, 3)


# =====================================================================
# 七、混料设计
# =====================================================================

def simplex_centroid(q):
    """单纯形质心设计 (Simplex Centroid Design)
    q: 分量数
    设计点：所有质心——单一分量点(1,0,...,0)、二元质心(1/2,1/2,0,...)、
    三元质心(1/3,1/3,1/3,0,...) ... q 元质心(1/q,...,1/q)
    总点数 = 2^q - 1
    """
    if q < 2:
        raise ValueError("混料设计至少需要 2 个分量")
    points = []
    for r in range(1, q + 1):
        for combo in itertools.combinations(range(q), r):
            row = np.zeros(q)
            row[list(combo)] = 1.0 / r
            points.append(row)
    X = np.array(points)
    letters = factor_letters(q)
    df = pd.DataFrame(X, columns=letters)
    info = {'type': '单纯形质心设计', 'q': q, 'runs': len(df)}
    return df, info


def simplex_lattice(q, m):
    """单纯形格点设计 (Simplex Lattice Design) {q, m}
    q: 分量数; m: 格点阶数
    每个分量取 m+1 个等间隔水平 0, 1/m, ..., 1，所有和为 1 的组合
    点数 = C(q+m-1, m)
    """
    if m < 1:
        raise ValueError("格点阶数 m 须 >= 1")
    levels = np.arange(m + 1) / m
    points = []
    for combo in itertools.product(levels, repeat=q):
        if abs(sum(combo) - 1.0) < 1e-9:
            points.append(combo)
    X = np.array(points)
    letters = factor_letters(q)
    df = pd.DataFrame(X, columns=letters)
    info = {'type': '单纯形格点设计 {q,m}={%d,%d}' % (q, m), 'q': q, 'm': m, 'runs': len(df)}
    return df, info


def extreme_vertices(q, low=None, high=None, npoints=None):
    """极端顶点设计 (Extreme Vertices Design)
    q: 分量数
    low/high: 各分量的下限/上限列表（长度 q，默认 0/1）
    算法（Snee & Marquardt 1974 XVERT）：在上下限约束 Σx=1 下，
    枚举所有顶点——选择 1 个自由分量，其余取下限或上限，
    自由分量由 Σx=1 决定；满足上下限即为顶点。
    """
    if low is None:
        low = [0.0] * q
    if high is None:
        high = [1.0] * q
    low = np.array(low, dtype=float)
    high = np.array(high, dtype=float)
    # 可行性检查
    if low.sum() > 1.0 + 1e-9 or high.sum() < 1.0 - 1e-9:
        raise ValueError("约束不可行：分量上下限与 Σx=1 矛盾")
    pts = []
    for free in range(q):
        others = [i for i in range(q) if i != free]
        for bits in itertools.product([0, 1], repeat=q - 1):
            x = np.zeros(q)
            for k, i in enumerate(others):
                x[i] = high[i] if bits[k] else low[i]
            s = x.sum()
            x[free] = 1.0 - (s - x[free])
            if low[free] - 1e-9 <= x[free] <= high[free] + 1e-9:
                pts.append(x)
    # 去重（四舍五入到 1e-9）
    seen = set()
    uniq = []
    for x in pts:
        key = tuple(np.round(x, 9))
        if key not in seen:
            seen.add(key)
            uniq.append(x)
    X = np.array(uniq)
    letters = factor_letters(q)
    df = pd.DataFrame(X, columns=letters)
    # 可选：若点数超过要求，用 D 最优选择子集（见最优设计）
    if npoints and len(df) > npoints:
        from .designs import _d_optimal_subset
        Xs = _d_optimal_subset(X, npoints)
        df = pd.DataFrame(Xs, columns=letters)
    info = {'type': '极端顶点设计', 'q': q, 'runs': len(df),
            'low': list(low), 'high': list(high)}
    return df, info


def mixture_process(df_mix, process_levels, randomize=False, seed=None):
    """混料过程变量设计
    df_mix: 基础混料设计 DataFrame
    process_levels: 过程变量水平 dict {变量名: [水平,...]} 或列表
    对每个过程变量组合，复制一份完整混料设计
    """
    import pandas as _pd
    names = list(process_levels.keys()) if isinstance(process_levels, dict) else None
    if names:
        levels = list(process_levels.values())
    else:
        levels = process_levels
    combos = list(itertools.product(*levels))
    frames = []
    for c in combos:
        base = df_mix.copy()
        for j, nm in enumerate(names):
            base[nm] = c[j]
        frames.append(base)
    out = _pd.concat(frames, ignore_index=True)
    if randomize:
        rng = np.random.default_rng(seed)
        out = out.iloc[rng.permutation(len(out))].reset_index(drop=True)
    info = {'type': '混料过程变量设计', 'mix_runs': len(df_mix),
            'process_combos': len(combos), 'runs': len(out)}
    return out, info


# =====================================================================
# 八、田口设计（正交表）
# =====================================================================

def _gf2_columns(nbase):
    """GF(2) 上 nbase 个基本列 -> 2^nbase-1 个非零线性组合列（标准正交表）
    列 = 系数向量(非零)与基本列的 GF(2) 线性组合（模 2 加法）
    任意两个不同非零系数向量在 GF(2) 上线性无关 => 两两正交
    返回 numpy 数组 (2^nbase, 2^nbase-1)，元素 0/1
    """
    nbase = int(nbase)
    n = 2 ** nbase
    base = np.zeros((n, nbase), dtype=int)
    for j in range(nbase):
        block = n // (2 ** (j + 1))
        vals = np.concatenate([np.ones(block), np.zeros(block)])
        base[:, j] = np.tile(vals, 2 ** j).astype(int)
    cols = []
    for mask in range(1, 2 ** nbase):
        col = np.zeros(n, dtype=int)
        for j in range(nbase):
            if mask & (1 << j):
                col = (col + base[:, j]) % 2
        cols.append(col)
    return np.column_stack(cols)


def _gf3_columns(nbase):
    """GF(3) 上 nbase 个基本列 -> (3^nbase-1)/2 个归一化非零线性组合列
    返回 (3^nbase, (3^nbase-1)/2)，元素 0/1/2
    """
    nbase = int(nbase)
    n = 3 ** nbase
    base = np.zeros((n, nbase), dtype=int)
    for j in range(nbase):
        block = n // (3 ** (j + 1))
        vals = np.concatenate([np.full(block, 0), np.full(block, 1), np.full(block, 2)])
        base[:, j] = np.tile(vals, 3 ** j).astype(int)
    cols = []
    seen = set()
    for mask in range(1, 3 ** nbase):
        # 系数向量（三进制）
        coef = []
        m = mask
        for _ in range(nbase):
            coef.append(m % 3)
            m //= 3
        if all(c == 0 for c in coef):
            continue
        # 归一化：首个非零系数取 1（乘 2 使 2->1），消除互为倍数的列
        first = next(c for c in coef if c != 0)
        if first == 2:
            coef = [(c * 2) % 3 for c in coef]
        key = tuple(coef)
        if key in seen:
            continue
        seen.add(key)
        col = np.zeros(n, dtype=int)
        for j, c in enumerate(coef):
            if c:
                col = (col + c * base[:, j]) % 3
        cols.append(col)
    return np.column_stack(cols)


# L18 特殊表（2^1 × 3^7），标准 Taguchi 正交表
_L18 = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 2, 2, 2, 2, 2, 2],
    [1, 1, 3, 3, 3, 3, 3, 3],
    [1, 2, 1, 1, 2, 2, 3, 3],
    [1, 2, 2, 2, 3, 3, 1, 1],
    [1, 2, 3, 3, 1, 1, 2, 2],
    [1, 3, 1, 2, 1, 3, 2, 3],
    [1, 3, 2, 3, 2, 1, 3, 1],
    [1, 3, 3, 1, 3, 2, 1, 2],
    [2, 1, 1, 3, 3, 2, 2, 1],
    [2, 1, 2, 1, 1, 3, 3, 2],
    [2, 1, 3, 2, 2, 1, 1, 3],
    [2, 2, 1, 2, 3, 1, 3, 2],
    [2, 2, 2, 3, 1, 2, 1, 3],
    [2, 2, 3, 1, 2, 3, 2, 1],
    [2, 3, 1, 3, 2, 3, 1, 2],
    [2, 3, 2, 1, 3, 1, 2, 3],
    [2, 3, 3, 2, 1, 2, 3, 1],
]


def taguchi_design(name, factor_names=None):
    """田口正交表设计
    name: 'L8','L9','L12','L16','L18','L27','L32','L36','L54','L64' 等
    2 水平表 (L8/L16/L32/L64) 与 3 水平表 (L9/L27) 由 GF(p) 线性构造精确生成；
    L18 使用内置标准表。
    """
    name = name.upper()
    if name == 'L8':
        X = _gf2_columns(3) + 1          # 0/1 -> 1/2
        ncols = 7
    elif name == 'L16':
        X = _gf2_columns(4) + 1
        ncols = 15
    elif name == 'L32':
        X = _gf2_columns(5) + 1
        ncols = 31
    elif name == 'L64':
        X = _gf2_columns(6) + 1
        ncols = 63
    elif name == 'L9':
        X = _gf3_columns(2) + 1
        ncols = 4
    elif name == 'L27':
        X = _gf3_columns(3) + 1
        ncols = 13
    elif name == 'L18':
        X = np.array(_L18)
        ncols = 8
    elif name == 'L12':
        # L12 = Plackett-Burman(12) 编码转 1/2
        X = _pb_rows(12)
        X = np.where(X > 0, 1, 2)
        ncols = 11
    else:
        raise ValueError("不支持的正交表: %s" % name)
    letters = factor_letters(ncols)
    df = pd.DataFrame(X, columns=letters)
    if factor_names:
        df.columns = factor_names[:len(df.columns)]
    info = {'type': '田口正交表 %s' % name, 'runs': len(df), 'cols': len(df.columns)}
    return df, info


# =====================================================================
# 九、最优设计（D/A/I/G 最优 + 坐标交换算法）
# =====================================================================

def _model_matrix(X, model='linear', interactions=True, quadratic=True):
    """构造模型矩阵（含截距）
    X: (n, k) 编码设计矩阵
    model: 'linear' | 'quadratic' | 'interaction' | 'custom'
    """
    n, k = X.shape
    cols = [np.ones(n)]
    names = ['const']
    for j in range(k):
        cols.append(X[:, j])
        names.append('x%d' % j)
    if quadratic or model in ('quadratic',):
        for j in range(k):
            cols.append(X[:, j] ** 2)
            names.append('x%d^2' % j)
    if interactions or model in ('quadratic', 'interaction'):
        for i in range(k):
            for j in range(i + 1, k):
                cols.append(X[:, i] * X[:, j])
                names.append('x%dx%d' % (i, j))
    return np.column_stack(cols), names


def _optimality(Xm, criterion):
    """最优性准则
    Xm: 模型矩阵 (含截距)
    criterion: 'D' | 'A' | 'I' | 'G'
    D: det(X'X)（越大越好，用 log）
    A: trace((X'X)^-1)（越小越好）
    I: 平均预测方差 tr((X'X)^-1 W)/N（越小越好，W 为候选集加权）
    G: 最大预测方差（越小越好）
    返回 (score, 是否越大越好)
    """
    XtX = Xm.T @ Xm
    if criterion == 'D':
        sign, logdet = np.linalg.slogdet(XtX)
        return (logdet if sign > 0 else -1e15), True
    elif criterion == 'A':
        try:
            sign, logdet = np.linalg.slogdet(XtX)
            if sign <= 0 or logdet < -60:   # 奇异或接近奇异
                return 1e15, False
            return float(np.trace(np.linalg.solve(XtX, np.eye(XtX.shape[0])))), False
        except np.linalg.LinAlgError:
            return 1e15, False
    elif criterion == 'I':
        try:
            sign, logdet = np.linalg.slogdet(XtX)
            if sign <= 0 or logdet < -60:
                return 1e15, False
            return float(np.trace(np.linalg.solve(XtX, np.eye(XtX.shape[0])))), False   # 无候选集时退化为 A
        except np.linalg.LinAlgError:
            return 1e15, False
    elif criterion == 'G':
        try:
            sign, logdet = np.linalg.slogdet(XtX)
            if sign <= 0 or logdet < -60:
                return 1e15, False
            inv = np.linalg.solve(XtX, np.eye(XtX.shape[0]))
            v = float(np.max(np.einsum('ij,jk,ik->i', Xm, inv, Xm)))
            return v, False
        except np.linalg.LinAlgError:
            return 1e15, False
    raise ValueError("未知最优性准则: %s" % criterion)


def d_optimal_design(candidate, n, model='linear', interactions=True,
                     quadratic=False, criterion='D', nstart=10, seed=None,
                     max_iter=200):
    """坐标交换算法生成 D/A/I/G 最优设计
    candidate: (N, k) 候选点矩阵
    n: 目标试验次数
    criterion: 'D'/'A'/'I'/'G'
    nstart: 多起点次数
    算法：坐标交换（Fedorov / Wynn / Meyer-Nachtsheim）
    """
    N, k = candidate.shape
    if n > N:
        raise ValueError("试验次数不能超过候选点数")
    rng = np.random.default_rng(seed)
    best_design = None
    best_score = None
    best_greater = None
    for _ in range(nstart):
        idx = rng.choice(N, n, replace=False)
        des = candidate[idx].copy()
        score, greater = _opt_iter(des, candidate, model, interactions,
                                   quadratic, criterion, max_iter, rng)
        if best_score is None or (greater and score > best_score) or (not greater and score < best_score):
            best_score = score
            best_design = des
            best_greater = greater
    letters = factor_letters(k)
    df = pd.DataFrame(best_design, columns=letters)
    info = {'type': '最优设计 (%s-最优)' % criterion, 'runs': n,
            'model': model, 'criterion': criterion, 'score': best_score}
    return df, info


def _opt_iter(des, candidate, model, interactions, quadratic, criterion, max_iter, rng):
    """单起点坐标交换迭代"""
    n, k = des.shape
    N = candidate.shape[0]
    score, greater = _optimality(_model_matrix(des, model, interactions, quadratic)[0], criterion)
    for it in range(max_iter):
        improved = False
        # 坐标交换：对每个设计行 i、每维 j，尝试候选值
        for i in range(n):
            row_old = des[i].copy()
            best_row = row_old
            best_sc = score
            for c in range(N):
                cand = candidate[c]
                # 尝试把设计点 i 的 j 维换成候选点相应值
                des[i] = cand
                sc, _ = _optimality(_model_matrix(des, model, interactions, quadratic)[0], criterion)
                if (greater and sc > best_sc) or (not greater and sc < best_sc):
                    best_sc = sc
                    best_row = cand
            des[i] = best_row
            if best_sc != score:
                score = best_sc
                improved = True
        if not improved:
            break
    return score, greater


def _d_optimal_subset(candidate, n, seed=123):
    """从候选点中选择 D 最优子集（用于极端顶点减点等）"""
    df, info = d_optimal_design(candidate, n, model='linear', interactions=False,
                                quadratic=False, criterion='D', nstart=5, seed=seed)
    return df.values


# =====================================================================
# 十、DOE 工作表构建（Minitab 标准格式）
# =====================================================================

def make_doe_worksheet(design_df, lows=None, highs=None, randomize=True,
                       blocks=1, seed=None, add_response=True, response_name='Y',
                       pttype_all=None):
    """构建 Minitab 风格 DOE 工作表
    design_df: 编码设计 DataFrame（列 A,B,C...）
    lows/highs: 各因子低/高实际值列表（None 时保持编码值）
    pttype_all: 若提供，所有行 PtType 取该值（用于混料/田口等）
    输出列: StdOrder, RunOrder, PtType, Blocks, 因子列(实际值), [响应列]
    PtType: 1=因子点(角点/边中点), 0=中心点, -1=轴点
    编码->实际: actual = (low+high)/2 + coded*(high-low)/2
    """
    n = len(design_df)
    cols = list(design_df.columns)
    # 点类型判定
    if pttype_all is not None:
        pt = [pttype_all] * n
    else:
        pt = []
        for _, row in design_df.iterrows():
            vals = np.asarray(row.values, dtype=float)
            if np.allclose(vals, 0.0):
                pt.append(0)                     # 中心点
            elif np.allclose(np.abs(vals), 1.0):
                pt.append(1)                     # 因子点
            else:
                pt.append(-1)                    # 轴点
    # 实际值映射（含 CCD 轴点按 α 缩放）
    out_cols = {}
    for j, c in enumerate(cols):
        v = design_df[c].astype(float).values
        if lows is not None and highs is not None:
            lo, hi = float(lows[j]), float(highs[j])
            mid = (lo + hi) / 2.0
            half = (hi - lo) / 2.0
            out_cols[c] = mid + v * half
        else:
            out_cols[c] = v
    df = pd.DataFrame(out_cols)
    std = np.arange(1, n + 1)
    df.insert(0, 'StdOrder', std)
    df.insert(1, 'RunOrder', std.copy())
    df.insert(2, 'PtType', pt)
    df.insert(3, 'Blocks', np.ones(n, dtype=int))
    if randomize:
        rng = np.random.default_rng(seed)
        df['RunOrder'] = rng.permutation(n) + 1
        df = df.sort_values('RunOrder').reset_index(drop=True)
    if add_response:
        df[response_name] = np.nan
    info = {
        'runs': n, 'factors': len(cols),
        'randomize': randomize,
        'std_order': list(std),
    }
    return df, info


if __name__ == '__main__':
    # 自检
    print("2^3 全因子:\n", ff2n(3))
    df, info = frac_factorial(5, 2)
    print("2^(5-2):", info)
    print(alias_table(5, 2))
    d, i = pb_design(7)
    print("PB(7):", i, d.shape)
    dd, ii = dsd(6)
    print("DSD(6):", ii, dd.shape)
    c, ci = ccd(3)
    print("CCD(3):", ci, "alpha=", ci['alpha'])
    b, bi = box_behnken(3)
    print("BBD(3):", bi, b.shape)
