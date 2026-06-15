# Platform 一键启动脚本 (PowerShell)
# ================================
# 同时启动 platform-admin-app (8000) 和 platform-app (8001)
#
# 用法:
#   .\start.ps1
#   .\start.ps1 -NoReload
#   .\start.ps1 -Host 0.0.0.0

param(
    [switch]$NoReload,
    [string]$Host = "127.0.0.1",
    [switch]$InstallDeps
)

$ErrorActionPreference = "Stop"

# 路径
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$AdminDir = Join-Path $ScriptDir "platform-admin-app"
$AppDir = Join-Path $ScriptDir "platform-app"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)  # Python3-Root

# 查找 Python
function Find-Python {
    $candidates = @()
    $venvPy = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPy) { $candidates += $venvPy }
    $candidates += "python", "python3"
    foreach ($c in $candidates) {
        try {
            $ver = & $c --version 2>$null
            if ($ver) { return $c }
        } catch { continue }
    }
    return $null
}

$python = Find-Python
if (-not $python) {
    Write-Host "[ERROR] 未找到可用的 Python 解释器" -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       Platform 一键启动脚本" -ForegroundColor Cyan
Write-Host "       Python: $python" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 依赖检查 / 安装
function Test-Deps {
    try {
        & $python -c "import fastapi, uvicorn, sqlalchemy, pydantic, jwt" 2>$null | Out-Null
        return $true
    } catch { return $false }
}

if ($InstallDeps -or -not (Test-Deps)) {
    if (-not $InstallDeps) {
        $resp = Read-Host "依赖可能未安装，是否现在安装? [y/N]"
        if ($resp -notin @("y","Y","yes","Yes")) { exit 1 }
    }
    @($AdminDir, $AppDir) | ForEach-Object {
        $req = Join-Path $_ "requirements.txt"
        if (Test-Path $req) {
            Write-Host "[INFO] 安装依赖: $req" -ForegroundColor Yellow
            & $python -m pip install -r $req -q
        }
    }
}

# 构建命令
$reloadArg = if ($NoReload) { @() } else { @("--reload") }
$adminCmd = @($python, "-m", "uvicorn", "app.main:app", "--host", $Host, "--port", "8000") + $reloadArg
$appCmd = @($python, "-m", "uvicorn", "platform_app.main:app", "--host", $Host, "--port", "8001") + $reloadArg

# 启动 Job
Write-Host ""
$jobs = @()

Write-Host "[Admin] 启动中... http://${Host}:8000" -ForegroundColor Green
$adminJob = Start-Job -ScriptBlock {
    param($cmd, $cwd)
    Set-Location $cwd
    & $cmd[0] $cmd[1..($cmd.Length-1)]
} -ArgumentList (,$adminCmd), $AdminDir
$jobs += @{ Name = "Admin"; Job = $adminJob; Color = "Green"; Port = "8000" }

Write-Host "[App  ] 启动中... http://${Host}:8001" -ForegroundColor Blue
$appJob = Start-Job -ScriptBlock {
    param($cmd, $cwd)
    Set-Location $cwd
    & $cmd[0] $cmd[1..($cmd.Length-1)]
} -ArgumentList (,$appCmd), $AppDir
$jobs += @{ Name = "App  "; Job = $appJob; Color = "Blue"; Port = "8001" }

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
foreach ($j in $jobs) {
    $url = "http://${Host}:$($j.Port)"
    Write-Host "  [$($j.Name)]  $url" -ForegroundColor ($j.Color)
}
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "`n按 Ctrl+C 停止所有服务`n" -ForegroundColor Yellow

# 监控循环
try {
    while ($true) {
        foreach ($j in $jobs) {
            $state = $j.Job.State
            if ($state -eq "Completed" -or $state -eq "Failed" -or $state -eq "Stopped") {
                Write-Host "`n[$($j.Name)] 进程异常退出 (State=$state)" -ForegroundColor Red
                throw "Service exited"
            }
        }
        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host "`n[INFO] 正在停止所有服务..." -ForegroundColor Yellow
    foreach ($j in $jobs) {
        Write-Host "[$($j.Name)] 终止中..." -ForegroundColor ($j.Color)
        Stop-Job $j.Job -ErrorAction SilentlyContinue
        Remove-Job $j.Job -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] 所有服务已停止`n" -ForegroundColor Green
}
