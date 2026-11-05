# 2026-11-06 验证记录

## 代码和脚本

环境：Windows / Python 3.12.14 / lupa 2.6 的 Lua 5.4。依赖位于工作区 `.test-deps`，不入 Git。

执行：

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) '.test-deps'
$env:MIR2X_SCRIPT_ROOT = '<原始安装目录>\server\script'
python -X utf8 -m unittest discover -s tests -v
python -X utf8 tools/check_playability.py --server-root '<原始安装目录>\server'
git diff --check
```

结果：10 / 10 测试通过；兼容检查 `compatible: true`；差异空白检查通过。

覆盖：全部对话 XML 与链接可解析（1、6、7、30 级）、低级隐藏接取、直接/过期事件重新校验等级、7 级起复用原每日服务、操作说明、低等级登录提示、原始/已打补丁目录、依赖缺失/变化、已有 NPC 与同名任务保护。测试使用真实上游对话渲染器，玩家引擎调用及每日服务为测试替身；不能证明实际奖励发放与并发安全。

首跑兼容测试遇到沙箱临时目录权限错误；改到仓库 `.test-output` 内创建测试目录，并校验清理目标仍在此目录内，重新运行后全部通过。没有改变系统权限。

关键 9 个脚本的本地 Git blob 与上游 `201b19d322b2bf9e5582ea88f5f469d3a4bef29d` 一致；SHA-256 清单见补丁 `baseline.json`。这是代码版本关联，不是整个 EXE 的可重复构建证明。

## 原生运行尝试：未通过验收

工作区隔离目录 `.test-output/runtime`，复制程序、地图和脚本，不复制现有数据库。测试服务端参数为 `--auto-launch --client-port=17000 --peer-port=17001 --actor-pool-thread=2`；客户端指向该测试端口、使用只读原始资源目录。

首次客户端缺少 `libpinyin/data/table.conf` 并退出；复制原安装的 libpinyin 目录后进程能启动。服务端生成了独立测试数据库，两个窗口可枚举，但没有取得监听/连服成功证据。

窗口工具首次捕获到遮挡窗口而非游戏画面；重新枚举目标并尝试激活，返回 `failed to activate captured window`。没有据此推断脚本运行成功，也没有重复盲点或接管其他应用。随后终止本轮创建的两个执行会话，进程检查不再发现其 PID。

本地证据文件（忽略，不入 Git）：

- `.test-output/runtime/server/mir2x-server-v01.g3log.20261106-030819.log`（运行中为空，不能作为通过证据）
- `.test-output/runtime/client/mir2x-client-v01.g3log.20261106-030838.log`（缺少 libpinyin 的失败日志）
- `.test-output/runtime/client/mir2x-client-v01.g3log.20261106-030854.log`（后续启动；不能作为连服成功证据）

未保存或提交新截图，避免将其他应用画面当作游戏证据。原安装脚本、真实角色数据库和生产配置没有修改。

## 剩余门槛

原生对话排版、真实任务接取与领奖、断线/重启/跨日恢复、核心战斗循环、三职业与两人试玩、C++ 构建均未通过本轮验收。下一步先修通隔离启动/输入，按评估文档 M0 执行；不直接部署到现有服。
