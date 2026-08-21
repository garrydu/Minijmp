# -*- coding: utf-8 -*-
"""Minijmp 汉化辅助脚本：对指定文件做精确 GUI 文本替换（仅替换 text=/label= 字面量）"""
import io
import shutil


def translate(path, replacements):
    shutil.copy(path, path + '.zhbak')  # 备份
    with io.open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    total = 0
    for old, new in replacements:
        c = content.count(old)
        if c > 0:
            content = content.replace(old, new)
            total += c
            print("  [%d] %s -> %s" % (c, old, new))
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("%s 完成，共替换 %d 处" % (path, total))


# ============ sample_test_dialog.py 翻译映射 ============
sample_test = [
    # 组框标题
    ("text='Sample Values'", "text='样本值'"),
    ("text='Summarized Data (Overriding)'", "text='汇总数据（覆盖输入）'"),
    ("text='Hypothesis Test'", "text='假设检验'"),
    ("text='Known Value'", "text='已知值'"),
    ("text='Hypothesized mean of the differences'", "text='差值的假设均值'"),
    ("text='Variables'", "text='变量'"),
    # 标签
    ('text="N"', 'text="样本量 N"'),
    ('text="Std Dev"', 'text="标准差"'),
    ('text="Mean"', 'text="均值"'),
    ('text="Mean (u1)"', 'text="均值 (μ1)"'),
    ('text="Mean (u2)"', 'text="均值 (μ2)"'),
    ('text="Sample 1"', 'text="样本1"'),
    ('text="Sample 2"', 'text="样本2"'),
    ("text='Sample 1'", "text='样本1'"),
    ("text='Sample 2'", "text='样本2'"),
    ('text="u2 - u1 = "', 'text="μ2 - μ1 = "'),
    ("text=' Assume Equal Variances'", "text=' 假设等方差'"),
    ('text="Sample 1 - Sample 2"', 'text="样本1 - 样本2"'),
    ('text="Sample"', 'text="样本"'),
    ('text="Name of Event"', 'text="事件名称"'),
    ('text="Number of events"', 'text="事件数量"'),
    ('text="Number of trials"', 'text="试验次数"'),
    ('text="Hypothesized proportion"', 'text="假设比例"'),
    ('text="Col."', 'text="列"'),
    ("label='columns'", "label='列'"),
    # 错误消息
    ('self.error(msg="Invalid sample values received.")',
     'self.error(msg="收到无效的样本值。")'),
]

translate('sample_test_dialog.py', sample_test)
