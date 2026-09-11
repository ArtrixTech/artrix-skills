# MJBQDYJ1-WC 协议与验证边界

## 来源与实机范围

协议参考 `jasiek/xiaomi-mjbqdyj1-wc-reveng` 的固定 commit **`220bf5a0d1279a60b4573e9eb33d75c6965e112d`**：

- [client.py：帧、命令和 BLE 客户端](https://github.com/jasiek/xiaomi-mjbqdyj1-wc-reveng/blob/220bf5a0d1279a60b4573e9eb33d75c6965e112d/client.py)
- [FINDINGS.md：逆向协议笔记](https://github.com/jasiek/xiaomi-mjbqdyj1-wc-reveng/blob/220bf5a0d1279a60b4573e9eb33d75c6965e112d/FINDINGS.md)
- [ts/src/core.ts：另一份实现](https://github.com/jasiek/xiaomi-mjbqdyj1-wc-reveng/blob/220bf5a0d1279a60b4573e9eb33d75c6965e112d/ts/src/core.ts)

上游称协议来自 macOS 米家 `xiaomi.printer.label` 插件 1.1.4，但该 commit 没有其描述的原始 `plugin/main.bundle`，因此将上游笔记与实机证据区分。2026-09-11，本技能来源任务在 macOS 上完成状态查询和一张“你好世界”标签发送，用户确认实物打印成功。该次数据为 96×240 点、2880 字节位图；不据此宣称所有固件、耗材或 BLE 平台已经验证。

上游客户端没有米家账号、token、动态认证或绑定步骤；此次实机也接受固定密钥协议查询和打印。不需要为这条已验证路径添加米家登录流程。

## GATT 与外层帧

| 角色 | UUID |
|---|---|
| Service | `0000fe95-0000-1000-8000-00805f9b34fb` |
| TX，Write Without Response | `0000001f-0000-1000-8000-00805f9b34fb` |
| RX，Notify | `00000020-0000-1000-8000-00805f9b34fb` |

先订阅 RX，再发指令。主机外层帧：

```text
A3 20 <ciphertext_length LE16> <ciphertext> <CRC LE32>
```

- AES-128-CBC，key `99B829436CDD5647AADB8816F73E8644`，IV `0001020F3CF899ABABCD25318DF446B1`。
- 明文用零补至 16 字节倍数；已对齐时不额外补块，不使用 PKCS#7。
- CRC 对 ciphertext 计算，等价于 Python `zlib.crc32(ciphertext, 0x76953521)`。
- 设备也发送 `A3 00 <length LE16> <plaintext> <CRC LE32>`，这种通知不解 AES。
- RX 按长度组帧，先校验 CRC，再解密并按内层 body length 去除零填充。一个 BLE 通知不一定等于一个完整逻辑帧。

完整加密帧再切成不超过 `min(204, characteristic.max_write_without_response_size)` 的 BLE 写入片段。上游每 3 次物理 write 暂停 90 ms；短标签可使用更保守的逐片延时。长任务还需要依据实际空闲 buffer 做流控；本技能将长度限制为 600 点，未提供长图或连续多张打印。

## 查询与打印

内层命令：`11 <group> <command> <body_length LE16> <body>`。响应 marker 通常为 `21`，自发通知为 `10`。

| 操作 | 内层字节 |
|---|---|
| 标记连接 | `11 01 1E 01 00 01` |
| 查询状态 | `11 01 13 00 00` |
| 开始打印 | `11 05 0B 07 00 60 00 <height LE16> 01 00 00` |
| 图像块 | `11 05 0D <chunk_length+11 LE16> <index LE16> <total LE16> 10 0C 00 00 00 00 00 <raster>` |
| 单页提交 | `11 05 0C 09 00 01 02 00 00 00 02 01 00 00` |

每图像逻辑块至多 1800 字节，index 从 1 开始。打印顺序为 start → data blocks → finalize。位图固定宽 96 点，每行 12 字节，黑点为 1，MSB 为最左像素；主机先渲染字体，再沿走纸方向发送行。按上游的 8 点/mm，600 点约为 75 mm；这不是耗材自动适配能力。

实测最小握手只需标记连接和查询状态；未同步设备时钟也完成了本次打印。

## 状态 TLV 与已知误读

实测 `01/13`、`01/12`、`01/1F` 的 body 是 TLV：`<tag u8> <length LE16> <value>`。按声明长度遍历并保留未知 tag；不要把 AES 填充或 TLV 长度字段当数据。

| 消息 | 实测字段 |
|---|---|
| `01/13` 状态响应、`01/12` 状态通知 | tag1：4 字节状态 flags；tag2：1 字节，语义未核定 |
| `01/1F` 心跳 | tag1：4 字节 LE 空闲 buffer；tag2：4 字节状态 flags；tag3：1 字节，语义未核定 |

上游解释状态第一字节为：bit0 盖子打开、bit1 缺纸、bit2 卡纸、bit3 过热、bit4 无打印头、bit5 高电压、bit6 低电压、bit7 正在打印。上游解释第二字节为刀具、字体、PSRAM、纸张校准、关机过程、电池过热等状态。除已验证状态外仍视为逆向映射；最小打印流程遇到任何非零 flags 均停止，保留值供排查，避免遗漏高字节故障。

电量目前不提供百分比：

- 实测心跳 tag3 为 `03 01 00 20`，即长度 1、原始值 32。上游 Python 把其中 `00 20` 当两字节数，再除以 10，显示成 3%；它跨入了 TLV 长度字段，该显示不能采用。也不能据此改报 32%。
- 上游笔记写电量查询为 `01/0E`，当前 Python/TS 用 `01/1A`。实测 `01/1A` body 为 `40 1F`，LE16=8000，单位未核定。
- 上游 Python 和 TS 对心跳电量还使用不同偏移，不能以二者相互验证百分比。

## ACK 与物理完成

本次单页发送的时序：finalize TX → `21 05 0C 00 00` ACK → 状态 bit7 置 1（printing）。因此上游把该 ACK 命名为 `print_complete` 超出了这次实机证据。报告应使用“提交已应答”；状态回到空闲和用户确认纸面内容是另外两层证据。

若发生超时、断连或异常，保留该次独立输出目录并检查最后一次 TX/RX。已发送 finalize 后即使没有 ACK，也可能已经打印；先核实设备与纸面，再决定是否发送新任务。
