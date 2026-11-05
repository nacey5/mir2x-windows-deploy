# mir2x 本地服务端启停脚本（Windows）
# 本机 pwsh 不在 PATH，请用 powershell 调用：
#   powershell -ExecutionPolicy Bypass -File F:\mir\start-server.ps1
#   powershell -ExecutionPolicy Bypass -File F:\mir\start-server.ps1 -Force   # 已有实例先杀掉再启动
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$Root = 'F:\mir\mir2x'
$ServerDir = Join-Path $Root 'server'
$LogDir = 'F:\mir\logs'
$Port = 7000

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if (-not (Test-Path (Join-Path $ServerDir 'server.exe'))) {
    throw "server.exe 不存在: $ServerDir\server.exe"
}

$running = Get-Process server -ErrorAction SilentlyContinue
if ($running) {
    if (-not $Force) {
        Write-Host "服务端已在运行 (pid=$($running.Id))，如需重启加 -Force"
        exit 0
    }
    Write-Host "停止既有服务端 pid=$($running.Id)"
    $running | Stop-Process -Force
    Start-Sleep -Seconds 2
}

$busy = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object LocalPort -eq $Port
if ($busy) {
    Write-Warning "端口 $Port 已被占用 (pid=$($busy.OwningProcess))，启动可能失败"
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$p = Start-Process -FilePath (Join-Path $ServerDir 'server.exe') `
                   -ArgumentList '--auto-launch' `
                   -WorkingDirectory $ServerDir `
                   -PassThru `
                   -RedirectStandardOutput (Join-Path $LogDir "server-out-$stamp.log") `
                   -RedirectStandardError  (Join-Path $LogDir "server-err-$stamp.log")

Write-Host "服务端已启动 pid=$($p.Id)，等待监听 $Port ..."
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 700
    $listen = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
              Where-Object { $_.LocalPort -eq $Port -and $_.OwningProcess -eq $p.Id }
    if ($listen) {
        Write-Host "OK 监听 $($listen.LocalAddress):$Port"
        exit 0
    }
}

Write-Warning "20 秒内未观察到 $Port 监听，请查看 $LogDir\server-err-$stamp.log"
