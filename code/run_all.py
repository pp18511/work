"""一键复现入口：按顺序执行各问题的求解脚本。

用法::

    python code/run_all.py            # 跑全部问题
    python code/run_all.py q1 q3      # 只跑问题一和三

约定（很重要）：
  1. 每个问题的入口固定为 code/<问题>/main.py；
  2. 脚本必须能在仓库根目录下直接运行；
  3. 读数据只从 data/ 读，写结果只往 output/ 写；
  4. 任何结果都要能由本命令在干净环境下重新生成。
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROBLEMS = ["q1", "q2", "q3", "q4"]


def main(argv: list[str]) -> int:
    targets = argv or DEFAULT_PROBLEMS
    failed: list[str] = []

    for name in targets:
        entry = ROOT / "code" / name / "main.py"
        if not entry.exists():
            print(f"[跳过] {name}：未找到 {entry.relative_to(ROOT)}")
            continue

        print(f"\n{'=' * 60}\n运行 {name}  ->  {entry.relative_to(ROOT)}\n{'=' * 60}")
        start = time.time()
        result = subprocess.run([sys.executable, str(entry)], cwd=ROOT)
        elapsed = time.time() - start

        status = "成功" if result.returncode == 0 else f"失败(退出码 {result.returncode})"
        print(f"--- {name} {status}，耗时 {elapsed:.1f}s ---")
        if result.returncode != 0:
            failed.append(name)

    if failed:
        print(f"\n[失败] {', '.join(failed)}")
        return 1

    print("\n[完成] 全部跑通，结果见 output/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

