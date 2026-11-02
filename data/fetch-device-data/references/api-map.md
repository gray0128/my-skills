# 接口字段

`url = baseUrl.rstrip("/") + path`。

## 鉴权规则

默认工作流使用的接口均可免 token：

| 路由 / 能力 | 默认鉴权策略 | 说明 |
|---|---|---|
| `POST /pmsds/service` + `S_DS_AP_15` | **无需 token** | 查询设备下测点和 KPI 目录 |
| `POST /pmsds/service` + `S_DS_AP_19` | **无需 token** | 查询 KPI 名称、信号类型、关联信号等信息 |
| `/api/busout/` | **无需 token** | 非信号历史、信号采集时刻 |
| `/iehm-cloud/api/v1/busout/` | **无需 token** | busout 备选路径 |
| `/iehmBusOut/` | **无需 token** | 信号元数据、原始波形分页 |
| `/ddslp/` | **需要 token** | 仅保留给当前没有免 token 替代的可选能力，如服务端降采样 |

原则：

- 默认不要向用户索取 token。
- 即使用户已经提供 token，也不要把凭据发送给已验证可免 token 的接口。
- 若某个免 token 接口在其他环境返回明确鉴权失败，再按实际响应处理；不要因空数据、参数错误或 Java 异常误判为需要 token。
- 仅在确实调用 `/ddslp/` 等鉴权接口时，才发送 `token` 与 `x-token`。

## 目录：设备测点与 KPI 列表

**无需 token。**

`POST /pmsds/service`

请求体：

```json
{
  "serviceId": "S_DS_AP_15",
  "deviceCodeList": ["<deviceCode>"]
}
```

成功判定：

- HTTP 200
- `__sys__.status == 0`

响应业务数据在 `dataList[]`。常用字段：

- `deviceCode`
- `deviceName`
- `pointNo`
- `pointName`
- `collectPointId`
- `kpiList[].kpiName`
- `kpiList[].collectKpiId`
- `kpiList[].unit`
- `kpiList[].deviceKpiType`

拉数时：

- `pointId` 优先使用 `collectPointId`
- `kpiId` 优先使用 `collectKpiId`

若用户未指定具体数据项，可用该接口枚举候选；不需要 token，也不需要让用户手工提供 pointId / kpiId。

## KPI 信息与信号类型

**无需 token。**

`POST /pmsds/service`

请求体：

```json
{
  "serviceId": "S_DS_AP_19",
  "deviceCode": "<deviceCode>"
}
```

成功判定：

- HTTP 200
- `__sys__.status == 0`

响应业务数据在 `dataList[]`。常用字段：

- `deviceCode`
- `pointNo`
- `kpiName`
- `collectKpiId`
- `isSignal`
- `hasSignal`
- `relatedSignalKpi`
- `collectMethod`
- 以及响应中存在的单位等附加信息

类型判定优先使用：

- `isSignal == "是"` → 信号
- `isSignal == "否"` → 非信号

`hasSignal` 表示该 KPI 是否存在关联信号语义，不要把它等同于当前 KPI 自身是否为信号。需要关联信号时读取 `relatedSignalKpi`。

将 S_DS_AP_15 与 S_DS_AP_19 结果关联时，优先按以下字段匹配：

1. `pointNo` / `collectPointId`
2. `collectKpiId`
3. 必要时用 `kpiName` 辅助匹配

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

**无需 token。**

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

默认只使用 busout 路径，不需要退回 `/ddslp/` 同能力接口。

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

原始信号默认链路：

`busout 采集时刻 → iehmBusOut 元数据 → iehmBusOut 原始分页`

整条链路无需 token。

## 信号：降采样波形（可选）

当前已知能力仍使用鉴权接口，仅在用户明确要求服务端降采样时调用。

`POST /ddslp/service/LPBI01/getSignalKpiValueListByCondition`

**需要 token。**

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

如果当前没有 token，只在用户明确要求此能力且真正执行到该步骤时再询问，不要影响默认原始信号流程。

## 默认免 Token 闭环

标准数据拉取流程：

1. 查询目录：`POST /pmsds/service` + `S_DS_AP_15`
2. 判断 KPI 类型 / 查询关联信号：`POST /pmsds/service` + `S_DS_AP_19`
3. 非信号：busout 历史原始数据
4. 原始信号：
   - busout 查询采集时刻
   - iehmBusOut 查询 `hz/cl/startTime/endTime`
   - iehmBusOut 分页拉取原始点

以上默认闭环均无需 token。

## 时间单位

墙钟时间按 `Asia/Shanghai` 换算成毫秒/纳秒，告知用户已采用此时区。

| 字段 | 单位 |
|------|------|
| `startTimeMS` `endTimeMS`；降采样波形 `DTime` | 毫秒 |
| 信号点 `timestamps`；详情 `DTime` `startTime` `endTime`；原始 `startTimeNS` `endTimeNS`；历史 `data.timestamps` | 纳秒 = 毫秒 × 1e6 |
