<#
.SYNOPSIS
    一键配置本仓库的 Python 环境（Windows）。

.DESCRIPTION
    1. 自动挑选 Python（优先 3.12，其次 3.11 / 3.13 / 3.10）
    2. 在仓库根目录创建 .venv 虚拟环境
    3. 安装依赖（有 requirements.lock.txt 就用它，保证版本和队友一致）
    4. 跑一遍自检：确认 numpy / pandas / matplotlib 可用，并生成一张中文测试图

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File setup\setup_env.ps1

.EXAMPLE
    # 指定版本、改用官方源、重建环境
    powershell -ExecutionPolicy Bypass -File setup\setup_env.ps1 -Python 3.10 -Official -Recreate
#>
[CmdletBinding()]
param(
    [string]$Python = "",
    [switch]$Official,
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"

# 让 PowerShell 与 Python 统一用 UTF-8，避免中文提示乱码
# （Windows PowerShell 5.1 默认按 GBK 解码子进程输出，会把 Python 的 UTF-8 中文显示成乱码）
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $env:PYTHONIOENCODING = "utf-8"
} catch { }

$Root       = Split-Path -Parent $PSScriptRoot
$VenvDir    = Join-Path $Root ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$Index      = if ($Official) { "https://pypi.org/simple" } else { "https://pypi.tuna.tsinghua.edu.cn/simple" }

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok  ($msg) { Write-Host "[完成] $msg" -ForegroundColor Green }
function Write-Note($msg) { Write-Host "[提示] $msg" -ForegroundColor Yellow }
function Write-Bad ($msg) { Write-Host "[失败] $msg" -ForegroundColor Red }

# ---------- 1. 找 Python ----------
function Find-PythonExe {
    param([string]$Requested)

    $versions = if ($Requested) { @($Requested) } else { @("3.12", "3.11", "3.13", "3.10") }
    $saved = $ErrorActionPreference
    $ErrorActionPreference = "Continue"   # py 启动器找不到版本时会往 stderr 写，别让它中断脚本
    try {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            foreach ($v in $versions) {
                $exe = $null
                try { $exe = & py "-$v" -c "import sys;print(sys.executable)" 2>$null } catch { $exe = $null }
                if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
            }
        }
    } finally {
        $ErrorActionPreference = $saved
    }
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

Write-Step "检测 Python"
$PyExe = Find-PythonExe -Requested $Python
if (-not $PyExe) {
    Write-Bad "没找到 Python。请先安装 Python 3.12：https://www.python.org/downloads/release/python-31210/"
    Write-Note "安装时务必勾选 Add python.exe to PATH，装完关掉再打开终端重跑本脚本。"
    exit 1
}

$PyVer = & $PyExe -c "import sys;print('%d.%d.%d' % sys.version_info[:3])"
Write-Ok "使用 Python $PyVer （$PyExe）"

$verParts = (& $PyExe -c "import sys;print(sys.version_info[0], sys.version_info[1])") -split '\s+'
$major = [int]$verParts[0]
$minor = [int]$verParts[1]
if ($major -ne 3 -or $minor -lt 9) {
    Write-Bad "需要 Python 3.10 及以上，当前是 $PyVer。"
    exit 1
}
if ($minor -ge 14) {
    Write-Note "Python $PyVer 太新，个别科学计算库可能还没有预编译包，建议改用 3.12。"
}

# ---------- 2. 创建虚拟环境 ----------
if ($Recreate -and (Test-Path $VenvDir)) {
    if (-not ($VenvDir.StartsWith($Root) -and (Split-Path -Leaf $VenvDir) -eq ".venv")) {
        Write-Bad "拒绝删除非常规路径：$VenvDir"
        exit 1
    }
    Write-Step "删除旧的 .venv"
    Remove-Item -LiteralPath $VenvDir -Recurse -Force
}

if (-not (Test-Path $VenvPython)) {
    Write-Step "创建虚拟环境 .venv"
    & $PyExe -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { Write-Bad "创建虚拟环境失败"; exit 1 }
    Write-Ok "已创建 $VenvDir"
} else {
    Write-Ok "已存在虚拟环境 .venv，直接复用"
}

# ---------- 3. 安装依赖 ----------
function Invoke-Pip {
    param([string[]]$PipArgs)
    & $VenvPython -m pip @PipArgs -i $Index --timeout 60 --retries 3
    if ($LASTEXITCODE -ne 0) {
        if (-not $Official) {
            Write-Note "镜像源失败，改用官方 PyPI 重试…"
            & $VenvPython -m pip @PipArgs -i "https://pypi.org/simple" --timeout 60 --retries 3
        }
        if ($LASTEXITCODE -ne 0) { Write-Bad "安装失败：pip $($PipArgs -join ' ')"; exit 1 }
    }
}

Write-Step "升级 pip / setuptools / wheel"
Invoke-Pip @("install", "--upgrade", "pip", "setuptools", "wheel")

$LockFile = Join-Path $Root "requirements.lock.txt"
$ReqFile  = if (Test-Path $LockFile) { $LockFile } else { Join-Path $Root "requirements.txt" }
Write-Step "安装依赖（$([System.IO.Path]::GetFileName($ReqFile))，源：$Index）"
Write-Note "第一次会下载 200MB 左右，慢慢等，别关窗口。"
Invoke-Pip @("install", "-r", $ReqFile)

# ---------- 4. 自检 ----------
Write-Step "环境自检"
& $VenvPython (Join-Path $PSScriptRoot "smoke_test.py")
if ($LASTEXITCODE -ne 0) { Write-Bad "自检未通过，请看上面的报错"; exit 1 }

Write-Host ""
Write-Ok "环境准备好了，接下来："
Write-Host "  1) 激活环境      : .venv\Scripts\activate"
Write-Host "  2) 一键跑全部结果 : python code\run_all.py"
Write-Host "  3) VS Code 里选解释器: .venv\Scripts\python.exe"
Write-Host "  4) 队友加入后重复本脚本即可，版本完全一致"
