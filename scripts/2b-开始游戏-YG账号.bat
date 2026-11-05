@echo off
chcp 936 >nul
title ´«Ææ mir2x - ¿Í»§¶Ë YG
cd /d F:\mir\mir2x\client
start "" client.exe --server-ip=127.0.0.1 --auto-login=yg:123456
timeout /t 3 >nul