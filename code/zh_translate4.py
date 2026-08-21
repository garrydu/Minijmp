# -*- coding: utf-8 -*-
"""Minijmp 汉化脚本（第4批）：统计输出表头/消息（安全替换：仅限 field_names 数组与 print 消息，不碰字典 key）"""
import io
import re
import shutil

FILES = [
    'control_chart.py', 'chi_sq.py', 'proportion_test.py',
    'one_way_ANOVA.py', 'two_way_anova.py', 'linear_fit.py',
    'ortho_fit.py', 'binomial.py', 'poisson.py', 'ti.py',
    'nonpara_cor.py', 'dist_fit.py',
]

MAPPINGS = [
    (" CI of Mean", "均值置信区间"),
    (" CI of std", "标准差置信区间"),
    ("* H0 s==s0, H1 s!=s0", "* 原假设 H0: s==s0, 备择假设 H1: s!=s0"),
    ("-2*LogLikelihood", "-2×对数似然"),
    ("1-Alpha", "1-α"),
    ("A-sq", "A-sq（AD检验统计量）"),
    ("AICc Weight", "AICc 权重"),
    ("Adj MS", "校正均方 (Adj MS)"),
    ("Adj SS", "校正平方和 (Adj SS)"),
    ("Adj. MS", "校正均方 (Adj. MS)"),
    ("Adj. SS", "校正平方和 (Adj. SS)"),
    ("Algo", "算法"),
    ("Approx. p-value", "近似 P 值"),
    ("Bonett", "Bonett"),
    ("Chi Sq", "卡方"),
    ("Chi sq", "卡方"),
    ("DF", "自由度 DF"),
    ("Distribution", "分布"),
    ("Error: Check input values.", "错误：请检查输入值。"),
    ("Est.", "估计值"),
    ("Estimate", "估计值"),
    ("Event", "事件"),
    ("Events", "事件数"),
    ("F Ratio", "F 值"),
    ("F-value", "F 值"),
    ("Factor", "因子"),
    ("Grouping", "分组"),
    ("H0: The data is from the distribution. Small p-value rejects H0.",
     "原假设 H0: 数据服从该分布。P 值越小越拒绝 H0。"),
    ("H0: The model correctly specified the relationship.",
     "原假设 H0: 模型正确描述了该关系。"),
    ("H0: The two variables are independent.",
     "原假设 H0: 两个变量相互独立。"),
    ("Item", "项目"),
    ("Level", "水平"),
    ("Levels", "水平"),
    ("Lower Bound", "下限"),
    ("Lower TI", "公差区间下限"),
    ("MAD to Mean", "均值绝对差 (MAD to Mean)"),
    ("MAD to Median", "中位数绝对差 (MAD to Median)"),
    ("Mean", "均值"),
    ("Mean Sq.", "均方"),
    ("Measures", "度量"),
    ("Minimum Value of the Function:", "函数最小值："),
    ("N", "样本量 N"),
    ("Note: The AICc weight is the probability that a given model is the best model among a set of candidate models.",
     "说明：AICc 权重是给定模型在一组候选模型中为最佳模型的概率。"),
    ("Note: The algo is same to Minitab 20, not JMP 17.",
     "说明：算法与 Minitab 20 一致，而非 JMP 17。"),
    ("Obs", "观测"),
    ("Optimized Parameters:", "优化参数："),
    ("P > ChiSq", "P > 卡方"),
    ("P Value", "P 值"),
    ("P ratio", "比例 P"),
    ("Parameter", "参数"),
    ("Prob > |t|", "概率 > |t|"),
    ("Proportion", "比例"),
    ("Resid", "残差"),
    ("SD", "标准差"),
    ("SE Mean", "均值标准误"),
    ("Sample", "样本"),
    ("Sample P Ratio", "样本比例"),
    ("Source", "来源"),
    ("Std Error", "标准误差"),
    ("Std Resid", "标准化残差"),
    ("Sum of Sq.", "平方和"),
    ("Summary of Fit", "拟合汇总"),
    ("Test", "检验"),
    ("The Bonett method is valid for any continuous distribution.",
     "Bonett 方法适用于任意连续分布。"),
    ("The chi-square method is valid only for the normal distribution.",
     "卡方方法仅适用于正态分布。"),
    ("Upper Bound", "上限"),
    ("Upper TI", "公差区间上限"),
    ("X Fit", "X 拟合"),
    ("Y Fit", "Y 拟合"),
    ("Z porportion test", "Z 比例检验"),
    ("mr", "移动极差 mr"),
    ("p value is the probability of slope == 0.", "P 值是斜率等于 0 的概率。"),
    ("p value is the probability of the true relationship is linear.",
     "P 值是真实关系为线性的概率。"),
    ("p values above are the probabilities of each term == 0.",
     "以上 P 值是各项等于 0 的概率。"),
    ("p values are the probabilities of true dist is normal.",
     "P 值是真实分布为正态的概率。"),
    ("p-value", "P 值"),
    ("t Ratio", "t 值"),
    ("t test p value matrix, H0: u1 == u2, H1: u1 != u2",
     "t 检验 P 值矩阵，H0: u1 == u2, H1: u1 != u2"),
]


def safe_replace(path):
    with io.open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    total = 0
    for old, new in MAPPINGS:
        # 仅替换 field_names=[...] 数组内的
        pat1 = re.compile(
            r"(field_names\s*=\s*\[[^\]]*?)['\"]%s['\"]" % re.escape(old))
        c1 = len(pat1.findall(content))
        if c1:
            content = pat1.sub(lambda m: m.group(1) + "'" + new + "'", content)
            total += c1
        # 仅替换 print('...') / print("...") 纯消息内的
        pat2 = re.compile(
            r"(print\s*\(\s*)(['\"])%s\2" % re.escape(old))
        c2 = len(pat2.findall(content))
        if c2:
            content = pat2.sub(lambda m: m.group(1) + "'" + new + "'", content)
            total += c2
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("%s 完成，共替换 %d 处" % (path, total))


for f in FILES:
    shutil.copy(f, f + '.zhbak')
    safe_replace(f)
