# 接口字段

`url = baseUrl.rstrip("/") + path`。

## 目录

`POST /ddslp/service/LPDS01/getPointAndKpiListByDeviceCodeList`

```json
{"params":{"deviceCodeList":["<deviceCode>"]}}
```

响应 `result[]`：`collectPointId` / `pointId`、`deviceCode`、`kpiList[]`（`collectKpiId`、`kpiName`、`kpiId`）。拉数时 `pointId` 用测点编号，`kpiId` 用 `collectKpiId` 或 `kpiName`（与目录一致即可）。

## 非信号：历史原始数据

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

## 信号：时间范围内信号点

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

同能力的 ddslp 写法：`POST /ddslp/service/LPBI01/getSignalTimeListByCondition`，body 为 `params`，`startTime`/`endTime` 用毫秒；响应 `result.DTimes`、`result.dTimesStr`。默认走 busout 信号点接口。

## 信号：详情（元数据）

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

## 信号：降采样波形

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

## 时间单位

墙钟时间按 `Asia/Shanghai` 换算成毫秒/纳秒，告知用户已采用此时区。

| 字段 | 单位 |
|------|------|
| `startTimeMS` `endTimeMS`；波形 `DTime`；ddslp 采集时刻的 start/end | 毫秒 |
| 信号点 `timestamps`；详情 `DTime` `startTime` `endTime`；原始 `startTimeNS` `endTimeNS`；历史 `data.timestamps` | 纳秒 = 毫秒 × 1e6 |
