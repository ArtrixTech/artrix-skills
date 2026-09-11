---
name: mijia-label-printer
description: 通过 BLE 扫描、查询和控制米家标签打印机 MJBQDYJ1-WC，渲染中文短标签并按用户要求打印。适用于这款米家标签打印机的蓝牙连接、状态排查和文字打印，不适用于其他型号的小米照片或文档打印机。
---

# 米家标签打印机

使用随附的 `scripts/printer.py` 操作 **MJBQDYJ1-WC**。已在 macOS 上验证中文短标签打印；其他系统或固件需要现场验证。扫描和状态查询可用于调查连接能力；只有用户要求打印时才执行 `print`。已有明确打印指令即为授权，无须再次确认。

## 执行

将当前目录切换到本技能所在目录，或把脚本路径解析成绝对路径。运行环境需要 Python、Bleak、PyCryptodome 和 Pillow；脚本带内联依赖声明，可直接使用 `uv run`。指定绝对 `--output` 父目录，脚本为每次调用创建唯一子目录，保存预览和日志并保留此前记录。

1. **定位设备**：不知道地址时先执行 `scan`，结合用户设备和扫描结果选定目标。macOS 使用扫描返回的 CoreBluetooth UUID。多个候选无法区分时先明确目标，不自动连接名称含 `printer` 的首项。
2. **检查状态**：使用选定地址执行 `status`。以收到并校验过的状态响应为依据；无响应、盖子打开或非零状态 flags 时停止打印并处理现场问题。连接成功本身不等于设备就绪。
3. **准备内容**：`render` 只生成预览，不连接或打印。中文使用支持中文的本地字体，必要时传 `--font`。脚本限制为 96 点宽、最长 600 点的短标签；过长内容先缩短或重新排版，不自动拆成多张。
4. **发送一张**：用户已要求打印且目标、内容明确时执行一次 `print`。脚本会重新检查设备状态；不必为了流程再要求用户批准同一内容。

命令形式如下；`ID`、`DIR`、`TEXT` 和 `FONT` 是待替换参数：

```sh
uv run scripts/printer.py scan --output DIR
uv run scripts/printer.py status --address ID --output DIR
uv run scripts/printer.py render --text TEXT --output DIR
uv run scripts/printer.py print --address ID --text TEXT --output DIR
```

`render`、`print` 可追加 `--font FONT`。对实际文字、地址和路径使用正确的 shell 引号；把“研究能否打印”“做个预览”保持在扫描、查询或渲染范围内。

## 判断结果

- **协议确认**：finalize 的 `21 05 0C` ACK 只说明设备应答了提交命令。实测 ACK 之后设备才上报 `printing`，所以 ACK 不能证明纸面打印完成。
- **设备状态**：收到 ACK 后的新查询返回 flags=0 时，可报告“设备当前空闲”；只有日志观察到 `printing` 从 1 回到 0，才报告“观察到打印状态结束”。两者都不能证明字形、方向或出纸质量。
- **实物确认**：用户确认纸面内容后，才报告对应内容已实际打印。若目前只有 ACK，就说明“已发送并收到应答，纸面结果待确认”。

超时或断连后先检查日志、重新查询状态并确认是否已经出纸。结果未知时不自动重放打印任务，避免重复标签。状态中的未知电量字段保留原值，不沿用上游的错误“3%”读数。

遇到 CRC/回包解析问题、需要移植协议或解释设备状态时，读取 [references/protocol.md](references/protocol.md)。常规打印直接使用脚本，不必重新实现加密和分片。
