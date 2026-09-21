"""环境自检：确认依赖装齐、能画中文图、结果能写到 output/。

由 setup_env.ps1 自动调用，也可以手动运行：
    .venv\\Scripts\\python.exe setup\\smoke_test.py
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

REQUIRED = ["numpy", "pandas", "scipy", "matplotlib", "sklearn"]
OPTIONAL = ["statsmodels", "seaborn", "openpyxl", "jupyter"]


def check(modules: list[str]) -> list[tuple[str, str, bool]]:
    rows = []
    for name in modules:
        try:
            mod = importlib.import_module(name)
            rows.append((name, getattr(mod, "__version__", "已安装"), True))
        except Exception as exc:  # noqa: BLE001 - 自检脚本要显示任何导入错误
            rows.append((name, f"{type(exc).__name__}: {exc}", False))
    return rows


def make_figure() -> Path:
    import numpy as np

    from common.plot_style import save_fig, set_style
    import matplotlib.pyplot as plt

    font = set_style()
    x = np.linspace(0, 2 * np.pi, 300)
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.plot(x, np.sin(x), label="sin(x)")
    ax.plot(x, np.cos(x), label="cos(x)", linestyle="--")
    ax.set_title("环境自检图：中文标题、负号 -1 显示正常即合格")
    ax.set_xlabel("x 轴")
    ax.set_ylabel("y 轴")
    ax.legend()
    if font:
        ax.text(0.02, 0.92, f"中文字体：{font}", transform=ax.transAxes, fontsize=9)
    else:
        ax.text(0.02, 0.92, "未找到中文字体，图中中文可能显示为方块",
                transform=ax.transAxes, fontsize=9, color="red")
    return save_fig(fig, "env_check")


def main() -> int:
    print(f"Python  ：{sys.version.split()[0]}")
    print(f"解释器  ：{sys.executable}")
    print(f"仓库根目录：{ROOT}")
    print()

    required = check(REQUIRED)
    optional = check(OPTIONAL)

    print("必需依赖：")
    for name, ver, ok in required:
        print(f"  [{'OK' if ok else '!!'}] {name:<12} {ver}")
    print("可选依赖：")
    for name, ver, ok in optional:
        print(f"  [{'OK' if ok else '--'}] {name:<12} {ver}")
    print()

    missing = [name for name, _, ok in required if not ok]
    if missing:
        print(f"[失败] 缺少必需依赖：{', '.join(missing)}")
        print("       请重新运行 setup\\setup_env.ps1")
        return 1

    try:
        path = make_figure()
    except Exception as exc:  # noqa: BLE001
        print(f"[失败] 绘图或写文件失败：{type(exc).__name__}: {exc}")
        return 1

    print(f"[通过] 依赖齐全，测试图已生成：{path.relative_to(ROOT)}")
    print("       打开这张图，中文和负号显示正常就说明环境没问题。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
