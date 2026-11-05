@echo off
chcp 936 >nul
title 传奇 mir2x - 停止
echo 正在关闭服务端与全部客户端...
taskkill /f /im server.exe >nul 2>&1
taskkill /f /im client.exe >nul 2>&1
echo 已全部关闭。
timeout /t 3 >nul