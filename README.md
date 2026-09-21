# 2026 全国研究生数学建模竞赛 · 参赛仓库

> 一句话：本仓库是 **【A 题：题目名称】** 的「代码 + 数据 + 论文」协作仓库，所有约定以本文件为准。

**本 README 是唯一入口。**环境、命令、分工、进度、文件放哪儿，都在这里找；群里只讨论模型，不刷屏找信息。

## 0. 队伍信息

| 项目 | 内容 |
| --- | --- |
| 竞赛 | 2026 全国研究生数学建模竞赛（华为杯） |
| 题号 / 题目 | 【A 题：XXXXXXXXXX】 |
| 队伍编号 | 【2026XXXXXX】 |
| 分工 | 【张三】建模 / 队长　【李四】编程 / 结果　【王五】论文 / 图表 |
| 赛程 | 【2026-09-18 08:00 ~ 2026-09-22 12:00】 |
| 当前状态 | 🟡 进行中（完成时改成 ✅ 已提交，并打 tag） |

## 1. 目录结构

```
.
├── README.md            # 唯一入口：信息、进度、约定
├── CONTRIBUTING.md      # 协作规则：分支、提交、PR
├── requirements.txt     # Python 依赖清单（按需增减）
├── requirements.lock.txt# 已验证的精确版本（队友装这个，结果才一致）
├── setup/
│   ├── 一键装环境.bat     # 队友双击这个就行
│   ├── setup_env.ps1    # 一键装环境：建 .venv + 装依赖 + 自检
│   └── smoke_test.py    # 环境自检：依赖是否齐全、中文绘图是否正常
├── code/
│   ├── common/          # 公共代码：路径、绘图样式、数据读取
│   ├── q1/main.py       # 每个问题的唯一入口，统一叫 main.py
│   ├── q2/main.py
│   ├── q3/main.py
│   └── run_all.py       # 一键复现：按顺序跑完所有问题
├── data/
│   ├── raw/             # 官方原始数据（只读，永不修改，不进 git）
│   ├── interim/         # 中间清洗结果（不进 git）
│   └── processed/       # 直接喂给模型的最终数据（不进 git）
├── output/
│   ├── figures/         # 论文用图，文件名与论文图号一致（不进 git）
│   ├── tables/          # 结果表（不进 git）
│   └── results/         # 数值结果、日志（不进 git）
├── paper/               # 论文 LaTeX / Word 源文件
└── docs/
    ├── task-board.md    # 分工与进度看板（每天更新）
    ├── data.md          # 数据来源与字段说明
    └── artifacts.md     # 图表 ↔ 脚本 ↔ 论文位置 对应表
```

> 数据、图片、结果都不进 git（体积大且可复现）；仓库只放**代码、文档、论文**。

## 2. 快速开始

### 2.1 装环境（每人做一次，约 3~10 分钟）

Windows 用户：克隆仓库后，**双击 `setup\一键装环境.bat`**，然后等它跑完。

它会自动完成：找 Python（优先 3.12）→ 建 `.venv` → 装依赖 → 跑自检并生成一张中文测试图。
脚本是幂等的，环境坏了、换电脑了，再双击一次就行。

命令行等价写法：

```powershell
git clone https://github.com/pp18511/work.git
cd work
powershell -ExecutionPolicy Bypass -File setup\setup_env.ps1

# 可选参数
#   -Python 3.10   指定 Python 版本
#   -Official      不用清华镜像，改用官方 PyPI
#   -Recreate      删掉旧 .venv 重建
```

macOS / Linux：

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.lock.txt
.venv/bin/python setup/smoke_test.py
```

### 2.2 每天开工

```bash
git pull                        # 先拉别人今天的改动
.venv\Scripts\activate          # 激活环境（命令行前面出现 (.venv)）
python code\run_all.py          # 跑全部；只跑某题：python code\run_all.py q1 q3
```

用 VS Code 的话，`Ctrl+Shift+P → Python: Select Interpreter` 选 `.venv\Scripts\python.exe`，之后直接按运行键就行。

### 2.3 数据

把官方数据放进 `data/raw/`（从网盘取，不要 git push）。

**复现约定**：任何结果都必须能由 `python code/run_all.py` 在干净环境下重新生成。跑不出来的结果 = 不存在的结果。

**依赖改动约定**：谁要加新库（如 `pulp`、`cvxpy`），先改 `requirements.txt`，装好后执行 `.venv\Scripts\pip freeze > requirements.lock.txt` 并提交，队友 `git pull` 后重跑一次装环境脚本即可对齐版本。

## 3. 数据说明

数据来源、字段含义、清洗规则见 [docs/data.md](docs/data.md)。

- `data/raw/` 只读，任何清洗都输出到 `interim/` 或 `processed/`，**不要就地改原始数据**。
- 大文件（>10MB）走网盘 / 群文件，或执行 `git lfs install` 后用 LFS；禁止直接 commit 到普通仓库。
- 路径统一用 `code/common/paths.py` 里的变量，禁止在脚本里写死绝对路径。

## 4. 分工与协作规则

详细规则见 [CONTRIBUTING.md](CONTRIBUTING.md)，核心就四条：

1. **main 永远能跑**：谁都不直接往 main 推，各自开分支 `feat/<姓名>-<模块>`（如 `feat/li-q2-遗传算法`）。
2. **小组件立即合**：一个模型、一张图、一段论文就发 PR，别攒一整天。
3. **提交信息统一格式**：`feat(q2): 加入遗传算法求解并输出图2`，方便回溯谁改了什么。
4. **每天 22:00 同步 15 分钟**：更新下面的进度表 + 关掉已完成的 issue。

### 队员首次加入

1. 队长在 GitHub 仓库 `Settings → Collaborators` 邀请队员（输入 GitHub 用户名）。
2. 队员接受邮件邀请后按第 2 节克隆并配置身份。
3. 队长确认仓库可见性：比赛期间数据涉密就设为 **Private**（`Settings → General → Change visibility`）。

## 5. 进度看板

实时进度见 [docs/task-board.md](docs/task-board.md)。每行一个任务，**开工前先认领，完成后当天更新状态**。

| 问题 | 模型 / 方法 | 负责人 | 状态 | 产出物 |
| --- | --- | --- | --- | --- |
| 问题一 | 【】 | 【】 | ⬜ 未开始 / 🟡 进行中 / ✅ 完成 | 【】 |
| 问题二 | 【】 | 【】 | ⬜ | 【】 |
| 问题三 | 【】 | 【】 | ⬜ | 【】 |
| 论文 | 【】 | 【】 | 🟡 | 【】 |

## 6. 图表与结果对应表

论文里的每一张图、每一张表，都必须能追溯到生成它的脚本，见 [docs/artifacts.md](docs/artifacts.md)。

**铁律**：图只能由脚本生成，不允许手改 Excel / 截图贴进论文。否则改一个参数，全篇图表对不上。

## 7. 提交物清单

截止前逐项打勾：

- [ ] 论文 PDF（按官方模板排版，含摘要页、页码、附录）
- [ ] 支撑材料：`code/`、`data/`（脱敏后）、`output/` 一起打包
- [ ] 承诺书 / 编号页按官方要求填写
- [ ] `python code/run_all.py` 在干净环境跑通，结果与论文一致
- [ ] 代码里没有硬编码路径、没有明文密钥
- [ ] 打 tag 冻结版本：`git tag -a v1.0 -m "最终提交版" && git push --tags`
- [ ] 论文与代码的图表编号逐一对齐（见第 6 节）

## 8. 常见问题

- **推送报错 / 提示登录**：第一次 `git push` 会弹 GitHub 授权页，点 Authorize 即可，凭据会存进 Windows 凭据管理器。
- **误提交了大文件**：先别慌，别继续 commit，立刻在群里说，由队长用 `git rm --cached` + `git commit --amend` 处理。
- **两个人改了同一个文件冲突了**：`git pull --rebase`，冲突处保留两边内容一起讨论，不确定就问，别硬选一边。
- **数据算出来和队友不一样**：先对齐随机种子（`np.random.seed(...)`）和数据版本，再看代码版本（`git log -1`）。
- **终端里中文输出乱码**：用 `python -X utf8 code/run_all.py`，或把终端换成 Windows Terminal / VS Code 内置终端（默认 UTF-8）。
