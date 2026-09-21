"""统一的路径定义。所有脚本从这里取路径，禁止写死绝对路径。

用法::

    from common.paths import RAW, FIGURES   # 在 code/q1/main.py 中这样导入
    # 若直接运行 main.py 报 ModuleNotFoundError，在文件开头加：
    # import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]      # 仓库根目录

DATA = ROOT / "data"
RAW = DATA / "raw"                              # 官方原始数据，只读
INTERIM = DATA / "interim"                      # 中间结果
PROCESSED = DATA / "processed"                  # 建模可直接使用的数据

OUTPUT = ROOT / "output"
FIGURES = OUTPUT / "figures"                    # 论文用图
TABLES = OUTPUT / "tables"                      # 结果表
RESULTS = OUTPUT / "results"                    # 数值结果 / 日志

PAPER = ROOT / "paper"

for _d in (RAW, INTERIM, PROCESSED, FIGURES, TABLES, RESULTS):
    _d.mkdir(parents=True, exist_ok=True)

