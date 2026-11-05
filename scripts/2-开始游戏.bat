@echo off
chcp 936 >nul
title 传奇 mir2x - 客户端
cd /d F:\mir\mir2x\client
echo 正在连接 127.0.0.1:7000 ...
start "" client.exe --server-ip=127.0.0.1 --auto-login=test:123456
echo 客户端已启动。账号 test / 密码 123456
timeout /t 3 >nul