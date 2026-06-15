# Platform 一键停止脚本 (PowerShell)
# ===================================
# 停止 platform-admin-app (8000) 和 platform-app (8001)
#
# 用法:
#   .\stop.ps1
#   .\stop.ps1 -Force
#   .\stop.ps1 -Ports 8000,8001,8002

param(
    [switch]$Force,
    [int[]]$Ports = @(8000, 8001)
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "         Platform 一键停止脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$found = $false
foreach ($port in $Ports) {
    $pids = Get-NetTCPConnection -LocalPort $port | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique
    if ($pids) {
        $found = $true
        $pidList = $pids -join ", "
        Write-Host "  端口 $port  ->  PID: $pidList" -ForegroundColor Yellow
        foreach ($pid in $pids) {
            if ($Force) {
                Write-Host "  [PID $pid] 强制终止..." -ForegroundColor Red
                Stop-Process -Id $pid -Force
            } else {
                Write-Host "  [PID $pid] 优雅终止..." -ForegroundColor Cyan
                Stop-Process -Id $pid
            }
        }
    }
}

if (-not $found) {
    Write-Host "`n[INFO] 未发现占用指定端口的进程，服务可能已经停止。`n" -ForegroundColor Yellow
    exit 0
}

if (-not $Force) {
    Write-Host "`n  等待 3 秒..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3

    foreach ($port in $Ports) {
        $pids = Get-NetTCPConnection -LocalPort $port | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique
        if ($pids) {
            foreach ($pid in $pids) {
                Write-Host "  [PID $pid] 未响应，强制终止..." -ForegroundColor Red
                Stop-Process -Id $pid -Force
            }
        }
    }
}

Start-Sleep -Seconds 1
$stillAlive = $false
foreach ($port in $Ports) {
    $pids = Get-NetTCPConnection -LocalPort $port | Select-Object -ExpandProperty OwningProcess
    if ($pids) { $stillAlive = $true }
}

if ($stillAlive) {
    Write-Host "`n[ERROR] 部分进程未能终止，请手动检查。`n" -ForegroundColor Red
    exit 1
} else {
    Write-Host "`n[OK] 所有服务已停止`n" -ForegroundColor Green
}
