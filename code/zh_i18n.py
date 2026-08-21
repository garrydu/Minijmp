# -*- coding: utf-8 -*-
# ============================================================
# 贡献者 / Contributors
#   胡志东 (Nico HU) <Hzd378747710@outlook.com>
#   - 简体中文汉化: 全项目菜单/对话框/统计输出/图表 (2026-08)
# ============================================================
"""
Minijmp 简体中文汉化支持模块
================================
1. 配置 matplotlib 中文字体（默认 DejaVu Sans 不含中文字符，会显示方框）
2. 本模块必须在所有其他模块导入之前被导入（放在 MiniJMP.py 顶部）
"""
import matplotlib

# 配置 matplotlib 使用中文字体（微软雅黑优先，兼容中文字体兜底）
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = [
    'Microsoft YaHei',      # 微软雅黑（Win7+ 自带）
    'SimHei',               # 黑体
    'SimSun',               # 宋体
    'DengXian',             # 等线
    'Arial Unicode MS',     # Mac 兜底
    'DejaVu Sans',          # 最后兜底
]
# 关闭 Unicode 负号问题（否则负号显示为方块）
matplotlib.rcParams['axes.unicode_minus'] = False

# Tkinter 界面字体（Windows 下默认 Segoe UI 已支持中文，此处确保兜底）
import tkinter.font as tkfont
try:
    _default_font = tkfont.nametofont('TkDefaultFont')
    _default_font.configure(family='Microsoft YaHei UI', size=9)
    _text_font = tkfont.nametofont('TkTextFont')
    _text_font.configure(family='Microsoft YaHei UI', size=9)
    _menu_font = tkfont.nametofont('TkMenuFont')
    _menu_font.configure(family='Microsoft YaHei UI', size=9)
    _heading_font = tkfont.nametofont('TkHeadingFont')
    _heading_font.configure(family='Microsoft YaHei UI', size=9)
except Exception:
    pass

# 若本机缺少微软雅黑，打印提示（不阻断程序）
import os
_win_fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
if not os.path.exists(os.path.join(_win_fonts_dir, 'msyh.ttc')):
    print('[zh_i18n] 提示: 未检测到微软雅黑字体(msyh.ttc)，图表中文可能显示为方框')
