---
name: fetch-device-data
description: 按 HTTP 接口拉取设备非信号时序和信号波形。向用户确认 base URL、设备、时间范围和 token；数据项可由用户指定或先查再选；信号先取采集时刻再取元数据再分页拉原始点，并区分降采样与原始。在用户说拉取设备数据、信号波形、原始信号、历史原始数据、非信号测点，或运行 /fetch-device-data 时使用。
---

# 拉取设备数据

只用 HTTP POST 调接口。路径、请求体、响应字段见 [references/api-map.md](references/api-map.md)。

## 1. 收齐前置条件

缺任何一项就停下来问用户：

| 项 | 完成标准 |
|----|----------|
| base URL | 形如 `http(s)://host[:port]`，无路径后缀 |
| 设备 | `deviceCode` |
| 时间范围 | 可换算的起止时间。时区默认 `Asia/Shanghai`，告知用户即可，不要再问 |
| token | 用户提供的鉴权串 |

用户只给了环境别名、没给 host 时，要其给出完整 base URL。

完成标准：四项都有值，且能算出窗口的 `startTimeMS` / `endTimeMS`。

## 2. 如何调用

拼接：`{baseUrl 去尾斜杠}{path}`，`path` 以 `/` 开头。api-map 里同一能力可能有两条 path（`/api/busout/...` 与 `/iehm-cloud/api/v1/busout/...`）；先用表中默认，HTTP 404 再试另一条，仍失败则把两条 URL 和状态码告诉用户。

每次请求：

- `POST`，`Content-Type: application/json`
- 头：`token`、`x-token`，值均为用户 token
- body 按 api-map：有的是顶层字段，有的是 `{"params":{...}}`
- 不要在回复里回显 token

判定：HTTP 200 且 `__sys__.status` 不是 `-1`、`msg` 不含「票据过期」→ 成功。否则停止，向用户要新 token 或核对 base URL。

## 3. 确定数据项

- 已给测点 + 数据项：沿用，仍用目录接口核对是否信号。
- 未指定、或只要「某一个」：先列目录，请用户选。
- 「全部信号 / 全部数据项」：列完再按用户确认的集合拉。

目录：`POST /ddslp/service/LPDS01/getPointAndKpiListByDeviceCodeList`，body `{"params":{"deviceCodeList":["<deviceCode>"]}}`。

信号判定：KPI 名含「波形」，或目录字段标明 `isSignal`。吃不准就问用户。名称含「波形」却被当非信号去拉历史、得到空 `timestamps` 时，改走第 5 步。

完成标准：每个目标有 `pointId`、`kpiId`、信号/非信号。

## 4. 非信号

一次调用历史原始数据接口，窗口用毫秒。`data.timestamps` 非空即为完成。空且该 KPI 是波形 → 第 5 步。

## 5. 信号

用户没说「降采样」或「原始」时，先问再拉。

两条路径都从**采集时刻**开始：

1. **采集时刻**  
   调「时间范围内信号点」（或「信号采集时刻」）。只要一个点：取距目标时刻最近的 `timestamp`，并告诉用户该时刻。  
   完成标准：至少一条采集时刻。毫秒 `DTimeMs = timestampNs / 1e6`。

2. **降采样**  
   用 `DTimeMs` 调「信号波形」。交付时写明 `isOriginal` 与 `len(values)` / `cl`。

3. **原始**（三步，不要跳）  
   - 时刻：上一步已有。  
   - 元数据：用纳秒 `DTime` 调「信号详情」，拿到 `hz`、`cl`、`startTime`、`endTime`。缺任一字段则停止并展示响应。  
   - 分页：用 `startTime`/`endTime` 调「原始信号」。`offset=0`，`limit` 取 `min(cl, 50000)`。将每页 `times`/`values` 拼接；`offset += 本页条数`，直到累计条数 ≥ `cl`、或本页为空、或本页条数 < `limit`。  
   完成标准：写明累计点数与 `cl`（含少 1 点）。

## 6. 交付

每个数据项：base URL、设备、测点、kpi、时间窗、调用的 path、是否原始/降采样、点数、信号的 `cl`/`hz`。用户要求文件时再写 JSON。
