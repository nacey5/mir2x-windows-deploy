# mir2x 停止脚本：停掉服务端与全部客户端
$ErrorActionPreference = 'SilentlyContinue'

$procs = Get-Process server, client
if (-not $procs) {
    Write-Host "没有运行中的 server/client 进程"
    exit 0
}

foreach ($p in $procs) {
    $p | Stop-Process -Force
    Write-Host "已停止 $($p.ProcessName) pid=$($p.Id)"
}

Start-Sleep -Seconds 2
$left = Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 7000
if ($left) {
    Write-Warning "端口 7000 仍在监听，pid=$($left.OwningProcess)"
} else {
    Write-Host "端口 7000 已释放"
}
