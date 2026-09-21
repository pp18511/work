"""绘图统一风格：中文字体、分辨率、统一保存到 output/figures。

用法::

    from common.plot_style import set_style, save_fig

    set_style()
    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.plot(x, y)
    save_fig(fig, "fig3_result")        # 自动存到 output/figures/fig3_result.png

约定：论文里的每一张图都用 save_fig 保存，文件名和论文图号一致（fig1_xxx、fig2_xxx…），
这样 docs/artifacts.md 的对应表才查得动。
"""

from __future__ import annotations

from pathlib import Path

from matplotlib import rcParams

# 常见中文字体，按优先级排列（Windows 前两个基本必中）
CJK_FONTS = [
    "Microsoft YaHei",   # 微软雅黑
    "SimHei",            # 黑体
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "PingFang SC",
    "WenQuanYi Zen Hei",
    "Arial Unicode MS",
]

try:  # 正常作为包导入时走这里
    from common.paths import FIGURES as _FIGURES
except ImportError:  # 直接运行单文件时的兜底
    _FIGURES = Path(__file__).resolve().parents[2] / "output" / "figures"


def set_style(dpi: int = 300) -> str | None:
    """统一图表风格，返回实际用上的中文字体名（没找到则返回 None）。"""
    from matplotlib import font_manager

    installed = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((name for name in CJK_FONTS if name in installed), None)

    if chosen:
        rcParams["font.sans-serif"] = [chosen, "DejaVu Sans"]
    rcParams["font.family"] = "sans-serif"
    rcParams["axes.unicode_minus"] = False   # 解决负号显示成方块

    rcParams["figure.dpi"] = 120             # 屏幕预览
    rcParams["savefig.dpi"] = dpi            # 论文插图分辨率
    rcParams["savefig.bbox"] = "tight"
    rcParams["font.size"] = 10.5
    rcParams["axes.titlesize"] = 12
    rcParams["axes.grid"] = True
    rcParams["grid.alpha"] = 0.3
    rcParams["legend.frameon"] = False
    return chosen


def save_fig(fig, name: str, subdir: str | None = None, fmt: str = "png", close: bool = True) -> Path:
    """保存图片到 output/figures/（或它的子目录），返回文件路径。"""
    target_dir = _FIGURES / subdir if subdir else _FIGURES
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{name}.{fmt}"
    fig.savefig(path, dpi=rcParams["savefig.dpi"], bbox_inches="tight")
    if close:
        import matplotlib.pyplot as plt

        plt.close(fig)
    return path

