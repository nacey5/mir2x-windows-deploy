@echo off
chcp 936 >nul
title 传奇 mir2x - 服务端
cd /d F:\mir\mir2x\server
echo ============================================
echo   传奇 mir2x 服务端启动中...
echo   端口: 7000
echo   启动后本窗口可最小化
echo ============================================
start "" server.exe --auto-launch
timeout /t 4 >nul
echo.
echo 已启动。若客户端连不上，请看是否有防火墙弹窗要点“允许”。
timeout /t 4 >nul