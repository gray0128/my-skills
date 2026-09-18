# 接口字段

`url = baseUrl.rstrip("/") + path`。

## 鉴权规则

按已验证环境的实际路由行为：

| 路由前缀 | 默认鉴权策略 | 说明 |
|---|---|---|
| `/ddslp/` | **需要 token** | 无 token 会在网关层返回 `__sys__.status=-1` 及票据/权限类错误 |
| `/api/busout/` | **无需 token** | 默认不要发送 `token` / `x-token` |
| `/iehm-cloud/api/v1/busout/` | **无需 token** | 作为 busout 备选路径时同样先免 token 调用 |
| `/iehmBusOut/` | **无需 token** | 可直达后端业务接口；业务层 Java 异常不等于鉴权失败 |

原则：

- 除非调用 `/ddslp/`，否则默认不要携带 token。
- 即使用户已经提供 token，也不要无必要地把凭据发送给免 token 路由。
- 若其他环境中的免 token 路由返回明确鉴权失败，再按实际响应处理；不要因空数据、参数错误或 Java 异常误判为需要 token。
- `/ddslp/` 请求若需要鉴权，请同时发送 `token` 与 `x-token`，值相同。

## 目录

**需要 token。**

`POST /ddslp/service/LPDS01/getPointAndKpiListByDeviceCodeList`

```json
{"params":{"deviceCodeList":["<deviceCode>"]}}
```

响应 `result[]`：`collectPointId` / `pointId`、`deviceCode`、`kpiList[]`（`collectKpiId`、`kpiName`、`kpiId`）。拉数时 `pointId` 用测点编号，`kpiId` 用 `collectKpiId` 或 `kpiName`（与目录一致即可）。

如果用户已经知道 `pointId` / `kpiId`，不要只为了核对而调用此接口。

## 非信号：历史原始数据

**无需 token。**

默认 `POST /api/busout/timeSeriesService/getDataListByCondition`  
备选 `POST /iehm-cloud/api/v1/busout/timeSeriesService/getDataListByCondition`

顶层 body（不要包 `params`；若 4xx 再试包一层 `params`）：

```json
{
  "deviceCode": "<deviceCode>",
  "pointId": "<pointId>",
  "kpiId": "<kpiId>",
  "startTimeMS": 0,
  "endTimeMS": 0
}
```

响应 `data.timestamps`（纳秒）、`data.values`。波形 KPI 在此接口常为空序列。

单次调用时间范围最大不超过 30 天；更长时间范围由 Agent 拆成多个 ≤30 天窗口后拉取、按时间排序拼接并对边界重复 timestamp 去重。总接口并发不得超过 5。

## 信号：时间范围内信号点

**默认 busout 路径无需 token。**

默认 `POST /api/busout/signalService/getSignalIndexListByCondition`  
备选 `POST /iehm-cloud/api/v1/busout/signalService/getSignalIndexListByCondition`

顶层 body：

```json
{
  "deviceCode": "<deviceCode>",
  "pointId": "<pointId>",
  "kpiId": "<kpiId>",
  "startTimeMS": 0,
  "endTimeMS": 0
}
```

响应 `data.timestamps`：各次采集时刻（纳秒）。`data.values` 三行依次为 hz、end_time、cl，与 timestamps 等长。

同能力的 ddslp 写法：`POST /ddslp/service/LPBI01/getSignalTimeListByCondition`，body 为 `params`，`startTime`/`endTime` 用毫秒；响应 `result.DTimes`、`result.dTimesStr`。**该 ddslp 路径需要 token，因此默认不要使用；优先走 busout 信号点接口。**

## 信号：详情（元数据）

**无需 token。**

`POST /iehmBusOut/service/AAAA01/findOneSignalIndex`

```json
{
  "params": {
    "deviceCode": "<deviceCode>",
    "pointId": "<pointId>",
    "kpiId": "<kpiId>",
    "DTime": 0
  }
}
```

`DTime` 为纳秒（采集时刻）。响应在顶层：`hz`、`cl`、`startTime`、`endTime`（后两者为纳秒，用作原始信号窗口）。

如果返回后端业务层空对象、参数异常或 Java 异常，说明请求已进入业务层；不要因此要求用户提供 token。

## 信号：降采样波形

**需要 token。仅在用户明确要求降采样时调用。**

`POST /ddslp/service/LPBI01/getSignalKpiValueListByCondition`

```json
{
  "params": {
    "deviceCode": "<deviceCode>",
    "pointId": "<pointId>",
    "pointName": "<pointName>",
    "kpiId": "<kpiId>",
    "DTime": 0,
    "func": 0
  }
}
```

`DTime` 为毫秒。`pointName` 未知可先用 `pointId`。响应在 `result`：`cl`、`hz`、`isOriginal`、`times`、`values`。`isOriginal=false` 表示降采样，`len(values)` 常小于 `cl`。

## 信号：原始（分页）

**无需 token。**

`POST /iehmBusOut/service/AAAA01/findSectionRawSignalWithPage`

```json
{
  "params": {
    "deviceCode": "<deviceCode>",
    "pointId": "<pointId>",
    "kpiId": "<kpiId>",
    "startTimeNS": 0,
    "endTimeNS": 0,
    "offset": 0,
    "limit": 50000
  }
}
```

`startTimeNS`/`endTimeNS` 用详情接口的 `startTime`/`endTime`。响应在顶层：`times`、`values`。`offset` 为已取到的样本序号，不是时间。

原始信号默认链路为：

`busout 采集时刻 → iehmBusOut 元数据 → iehmBusOut 原始分页`

整条链路默认无需 token。

## 时间单位

墙钟时间按 `Asia/Shanghai` 换算成毫秒/纳秒，告知用户已采用此时区。

| 字段 | 单位 |
|------|------|
| `startTimeMS` `endTimeMS`；波形 `DTime`；ddslp 采集时刻的 start/end | 毫秒 |
| 信号点 `timestamps`；详情 `DTime` `startTime` `endTime`；原始 `startTimeNS` `endTimeNS`；历史 `data.timestamps` | 纳秒 = 毫秒 × 1e6 |
