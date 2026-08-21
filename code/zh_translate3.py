# -*- coding: utf-8 -*-
"""Minijmp 汉化脚本（第3批）：图表图例/标题"""
import io
import shutil


def translate(path, mappings):
    shutil.copy(path, path + '.zhbak')  # 备份
    with io.open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    total = 0
    for old, new in mappings:
        for kw in ('label', 'title', 'ylabel', 'xlabel'):
            for q in ("'", '"'):
                pat = "%s=%s%s%s" % (kw, q, old, q)
                c = content.count(pat)
                if c > 0:
                    content = content.replace(pat, "%s=%s%s%s" % (kw, q, new, q))
                    total += c
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("%s 完成，共替换 %d 处" % (path, total))


translate('linear_plot.py', [
    ("Data points", "数据点"),
    ("Orthogonal Regression", "正交回归"),
    ("Linear Regression", "线性回归"),
    ("PI", "预测区间(PI)"),
    ("CI", "置信区间(CI)"),
])

translate('cont_plot.py', [
    ("Equal Tail", "等尾"),
    ("Left Tail", "左尾"),
    ("Right Tail", "右尾"),
])

translate('sb_histo.py', [
    ("Fitted Dist.", "拟合分布"),
])

translate('grr_plot.py', [
    ("OP=", "操作员 OP="),
])

# control_chart.py 两处 ylabel="P" 上下文不同，需精确替换
with io.open('control_chart.py', 'r', encoding='utf-8') as f:
    cc = f.read()
shutil.copy('control_chart.py', 'control_chart.py.zhbak')
cc = cc.replace('ylabel="P", NP=False', 'ylabel="比例 P", NP=False')
cc = cc.replace('ylabel="P", C=False', 'ylabel="每单位缺陷数", C=False')
with io.open('control_chart.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(cc)
print('control_chart.py 完成（ylabel 精确替换）')
