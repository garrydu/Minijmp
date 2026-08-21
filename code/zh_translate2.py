# -*- coding: utf-8 -*-
"""Minijmp 汉化脚本（第2批）：回归/方差/卡方/绘图对话框"""
import io
import shutil


def translate(path, mappings):
    shutil.copy(path, path + '.zhbak')  # 备份
    with io.open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    total = 0
    for old, new in mappings:
        # 同时处理 text=/label=/title= 的单双引号形式
        for kw in ('text', 'label', 'title'):
            for q in ("'", '"'):
                pat = "%s=%s%s%s" % (kw, q, old, q)
                c = content.count(pat)
                if c > 0:
                    content = content.replace(pat, "%s=%s%s%s" % (kw, q, new, q))
                    total += c
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("%s 完成，共替换 %d 处" % (path, total))


# ============ 通用翻译（跨文件） ============
common = [
    ("columns", "列"),
    ("Data Col.", "数据列"),
    ("Overriding selections above", "覆盖以上选择"),
    ("Plot Setting", "图表设置"),
    ("Show Grid", "显示网格"),
    ("Show Legend", "显示图例"),
    ("Label", "标签"),
    ("Group Col.", "分组列"),
    ("Data in its own column", "数据在独立列中"),
    ("Data in one column", "数据在单列中"),
    ("Show Plot", "显示图表"),
    ("X Axis", "X 轴"),
    ("Horizontal ref lines (optional)", "水平参考线（可选）"),
    ("Y positions (sep by ,)", "Y位置（逗号分隔）"),
]

# ============ fit_dialog.py 回归/相关 ============
fit_dialog = common + [
    ("45-degree X-labels", "45度X轴标签"),
    ("45-degree X-ticks", "45度X轴刻度"),
    ("Alpha", "α"),
    ("Box Width", "箱宽"),
    ("Confidence Interval", "置信区间"),
    ("Correlation Ellipse", "相关性椭圆"),
    ("Correlation Select", "相关性选择"),
    ("Error varaince ratio (y/x)", "误差方差比 (y/x)"),
    ("Ellipse Outline", "椭圆轮廓"),
    ("Hoeffding's D: independent or not", "Hoeffding D：独立性检验"),
    ("Hoeffding's D: independent or not (Slow, O(n^2))", "Hoeffding D：独立性检验（较慢，O(n²)）"),
    ("Horizontal Y-labels", "水平Y轴标签"),
    ("Kendall's tau: monotonic relationship", "Kendall τ：单调关系"),
    ("Linear Regression", "线性回归"),
    ("Margin (0.1=10%% of data range)", "边距 (0.1=数据范围的10%%)"),
    ("Orthogonal Regression", "正交回归"),
    ("Pearson's Correlation Only", "仅皮尔逊相关"),
    ("Pearson: linear relationship", "Pearson：线性关系"),
    ("Prediction Interval", "预测区间"),
    ("Residual Table", "残差表"),
    ("Residual plots are only available for linear regressions.", "残差图仅适用于线性回归。"),
    ("Scatter Dots", "散点"),
    ("Scatter Plot", "散点图"),
    ("Show Fit", "显示拟合"),
    ("Spearman's rho: monotonic relationship", "Spearman ρ：单调关系"),
    ("Will only include rows ", "将仅包含行 "),
    ("X Y Values", "X Y 值"),
    ("Variables", "变量"),
]

# ============ chi2_dialog.py 卡方 ============
chi2_dialog = common + [
    ("Columns", "列"),
    ("Counts", "计数"),
    ("Hypoth Prob (Need add to 1)", "假设概率（需合计为1）"),
    ("Levels", "水平"),
    ("Raw Data (categorical values)", "原始数据（分类值）"),
    ("Row labels (optional col.)", "行标签（可选列）"),
    ("Rows", "行"),
    ("Sample", "样本"),
    ("Summarized counts (overriding)", "汇总计数（覆盖输入）"),
    ("Summarized in a 2 way table (overriding)", "以二维表汇总（覆盖输入）"),
]

# ============ anova_dialog.py 方差分析 ============
anova_dialog = common + [
    ("Each Pair, Student's t", "各对比较，Student t"),
    ("Factors", "因子"),
    ("Data in separated columns", "数据在独立列中"),
    ("Interval Plot Setting", "区间图设置"),
    ("Interval plot of %.1f%% CI of mean", "均值 %.1f%% 置信区间的区间图"),
    ("Mean Comparison", "均值比较"),
    ("Options", "选项"),
    ("Response", "响应变量"),
    ("Stacked Data", "堆叠数据"),
    ("With Interaction", "含交互作用"),
    ("Variables", "变量"),
]

# ============ dist_plot_dialog.py 概率分布图 ============
dist_plot_dialog = common + [
    ("A specified probability", "指定的概率"),
    ("A specified x value (overriding)", "指定的X值（覆盖输入）"),
    ("Distribution", "分布"),
    ("Distribution 1", "分布1"),
    ("Distribution 2", "分布2"),
    ("Show the area corresponding to the following", "显示以下对应的区域"),
]

# ============ sb_hist_dialog.py 直方图 ============
sb_hist_dialog = common + [
    ("Bin Width", "组距"),
    ("Bins", "组数"),
    ("Data", "数据"),
    ("Data Column", "数据列"),
    ("Distribution", "分布"),
    ("Distribution Fit", "分布拟合"),
    ("Element", "元素"),
    ("Extended Features", "扩展功能"),
    ("Grouping Data (Optional)", "分组数据（可选）"),
    ("Histogram Setting", "直方图设置"),
    ("Hue Data Column", "色调数据列 (Hue)"),
    ("KDE", "KDE（核密度估计）"),
    ("KDE Only", "仅KDE"),
    ("Multiple", "多个"),
    ("Show Fit", "显示拟合"),
    ("Stats.", "统计量"),
    ("X Data Column", "X数据列"),
    ("Y Data Column", "Y数据列"),
]

# ============ sb_box_dialog.py 箱线图 ============
sb_box_dialog = common + [
    ("Box Width", "箱宽"),
    ("Data have to be stacked", "数据必须为堆叠格式"),
    ("Extended Features", "扩展功能"),
    ("Hide Fliers", "隐藏离群点"),
    ("Log Y", "Y轴对数"),
    ("Log Y Scale", "Y轴对数刻度"),
    ("Native X Scale", "原始X刻度"),
    ("Professional Settings", "专业设置"),
    ("Seperate", "分开"),
    ("Show Label", "显示标签"),
    ("Size", "大小"),
    ("Subgrouping", "子分组"),
    ("Subgrouping Col. (Hue)", "子分组列 (Hue)"),
    ("Swarm Dots", "蜂群点"),
    ("Swarm Dots Setting", "蜂群点设置"),
    ("Swarm Only", "仅蜂群点"),
    ("Whisker Length or Percentiles", "须线长度或百分位数"),
]

# ============ sb_misc_dialog.py 计数/线/点图 ============
sb_misc_dialog = common + [
    ("Group Col.(optional)", "分组列（可选）"),
    ("Plot Settings", "图表设置"),
    ("Stats.", "统计量"),
    ("X Data", "X数据"),
    ("X Data Col.", "X数据列"),
    ("Y Data Col.", "Y数据列"),
    ("Y Data in its own column", "Y数据在独立列中"),
    ("Y Data in one column", "Y数据在单列中"),
]

# ============ sbplot_dialog.py 绘图向导 ============
sbplot_dialog = common + [
    ("Close", "关闭"),
    ("Color Palettes", "颜色调色板"),
    ("Done", "完成"),
    ("Help", "帮助"),
    ("Palettes", "调色板"),
    ("Plot", "图表"),
    ("Show Label", "显示标签"),
]

translate('fit_dialog.py', fit_dialog)
translate('chi2_dialog.py', chi2_dialog)
translate('anova_dialog.py', anova_dialog)
translate('dist_plot_dialog.py', dist_plot_dialog)
translate('sb_hist_dialog.py', sb_hist_dialog)
translate('sb_box_dialog.py', sb_box_dialog)
translate('sb_misc_dialog.py', sb_misc_dialog)
translate('sbplot_dialog.py', sbplot_dialog)
