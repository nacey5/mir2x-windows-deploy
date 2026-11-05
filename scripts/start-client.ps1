# mir2x 客户端启动脚本（Windows）
# 本机 pwsh 不在 PATH，请用 powershell 调用：
#   powershell -ExecutionPolicy Bypass -File F:\mir\start-client.ps1
#   powershell -ExecutionPolicy Bypass -File F:\mir\start-client.ps1 -ServerIP 192.168.3.117
#   powershell -ExecutionPolicy Bypass -File F:\mir\start-client.ps1 -NoAutoLogin
param(
    [string]$ServerIP = '127.0.0.1',
    [string]$Account  = 'test',
    [string]$Password = '123456',
    [switch]$NoAutoLogin,
    [int]$ScreenMode  = -1     # 0/1/2，-1 表示用客户端默认
)

$ErrorActionPreference = 'Stop'
$ClientDir = 'F:\mir\mir2x\client'
$LogDir = 'F:\mir\logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$exe = Join-Path $ClientDir 'client.exe'
if (-not (Test-Path $exe)) { throw "client.exe 不存在: $exe" }

$args = @("--server-ip=$ServerIP")
if (-not $NoAutoLogin) { $args += "--auto-login=$Account`:$Password" }
if ($ScreenMode -ge 0) { $args += "--screen-mode=$ScreenMode" }

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$p = Start-Process -FilePath $exe -ArgumentList $args -WorkingDirectory $ClientDir -PassThru `
        -RedirectStandardOutput (Join-Path $LogDir "client-out-$stamp.log") `
        -RedirectStandardError  (Join-Path $LogDir "client-err-$stamp.log")

Write-Host "客户端已启动 pid=$($p.Id)  server=$ServerIP  参数=$($args -join ' ')"
