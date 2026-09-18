---
name: fetch-device-data
description: 按 HTTP 接口拉取设备非信号时序和信号波形。默认全链路使用免 token 接口：用 /pmsds/service 的 S_DS_AP_15 查询测点/KPI 目录、S_DS_AP_19 获取 KPI 类型与关联信号，非信号走 busout，原始信号走 busout + iehmBusOut。信号默认拉取原始数据，并告知用户可选降采样；非信号历史原始数据单次时间窗口不超过 30 天，超出自动拆分后拼接；所有接口调用并发不超过 5。在用户说拉取设备数据、信号波形、原始信号、历史原始数据、非信号测点，或运行 /fetch-device-data 时使用。
---

# 拉取设备数据

只用 HTTP POST 调接口。路径、请求体、响应字段和鉴权要求见 [references/api-map.md](references/api-map.md)。

核心原则：**默认工作流不要向用户索取 token。** 目录、KPI 信息、非信号历史原始数据和原始信号链路均有已验证的免 token 接口。只有用户明确要求某个仍依赖鉴权接口的可选能力时，才在真正需要的那一步询问 token。

## 1. 收齐前置条件

完成当前请求通常只需要：

| 项 | 完成标准 |
|----|----------|
| base URL | 形如 `http(s)://host[:port]`，无路径后缀 |
| 设备 | `deviceCode` |
| 时间范围 | 可换算的起止时间。时区默认 `Asia/Shanghai`，告知用户即可，不要再问 |
| 数据项 | 用户已给则直接用；未给时 Agent 自行调用目录接口查询，不需要 token |

用户只给了环境别名、没给 host 时，要其给出完整 base URL。

**不要把 token 当成前置条件。** 用户没给 `pointId` / `kpiId` 时，也不要因此向用户要 token 或要求用户手工查标识；直接按第 3 节调用免 token 目录接口。

完成标准：已有 base URL、deviceCode、时间范围。数据项可以由用户直接指定，也可以由 Agent 后续自行查询确定。

## 2. 如何调用

拼接：`{baseUrl 去尾斜杠}{path}`，`path` 以 `/` 开头。api-map 里同一 busout 能力可能有两条 path（`/api/busout/...` 与 `/iehm-cloud/api/v1/busout/...`）；先用表中默认，HTTP 404 再试另一条，仍失败则把两条 URL 和状态码告诉用户。

### 鉴权策略

默认以下接口**都不带 token / x-token**：

- `POST /pmsds/service`：`S_DS_AP_15`、`S_DS_AP_19`
- `/api/busout/`
- `/iehm-cloud/api/v1/busout/`
- `/iehmBusOut/`

即使用户此前提供过 token，调用这些免 token 路由时也默认不要附带凭据，减少不必要的凭据暴露。

只有某个可选能力在 api-map 中明确标记为需要鉴权时，才携带 token；若当前没有 token，到真正执行该能力时再向用户索取，不要提前索取。

若一个已标记免 token 的接口在当前环境返回**明确的鉴权失败**，再说明该环境行为与已验证环境不同，并根据实际响应决定是否需要 token。不要因为业务空结果、参数错误或后端 Java 异常就推断“需要 token”。

每次请求：

- `POST`，`Content-Type: application/json`
- body 严格按 api-map；`/pmsds/service` 使用顶层 `serviceId` 和业务参数，不包 `params`
- 免 token 接口不要发送 `token` / `x-token`
- 不要在回复、日志摘要或错误信息里回显 token

### 并发控制

- **所有接口调用统一限制为最多 5 个并发请求**；任意时刻 in-flight 请求数不得超过 5。
- 批量拉多个设备、测点、KPI 或历史时间分片时，使用并发池/队列调度，不要一次性并发发出全部请求。
- 同一信号的原始数据分页依赖分页进度和终止条件，默认按页顺序拉取，不要为了提速突破全局并发上限。

### 响应判定

不要用一套规则判断所有路由：

- `/pmsds/service`：HTTP 200 且 `__sys__.status == 0` 视为接口成功；业务数据在 `dataList`。
- busout：优先看 HTTP 状态、`code`、`msg` 和预期 `data` 字段。HTTP 200、`code=200` 且业务字段正常即可视为成功。
- `/iehmBusOut/`：通常看 HTTP 状态、`__sys__` 以及预期业务字段。能进入业务层但返回 Java 空对象、参数错误等消息，不等于鉴权失败。
- 只有响应明确表明鉴权失败时才考虑 token；其余情况按路径、参数、时间窗或数据是否存在来排查。

## 3. 确定数据项

目录和 KPI 类型判断都使用免 token 的 `POST /pmsds/service`。

### 3.1 查询测点与 KPI 目录：S_DS_AP_15

当用户未明确给出 `pointId` / `kpiId`，或要求“列出测点 / 数据项 / 全部数据项”时，调用：

`POST /pmsds/service`

body：

```json
{
  "serviceId": "S_DS_AP_15",
  "deviceCodeList": ["<deviceCode>"]
}
```

从 `dataList[]` 读取：

- 设备：`deviceCode`、`deviceName`
- 测点：优先用 `collectPointId` 作为拉数所需 `pointId`；`pointNo`、`pointName` 用于展示
- KPI：`kpiList[].collectKpiId` 作为拉数所需 `kpiId`；同时保留 `kpiName`、`unit`、`deviceKpiType`

用户未指定具体数据项时：

- “某一个 / 请选择”：列出候选后让用户选。
- “全部 / 全部信号 / 全部非信号”：继续查询一次 S_DS_AP_19 做类型判定，然后自行筛选，不要要求用户逐项确认。

### 3.2 查询 KPI 信息与信号类型：S_DS_AP_19

当需要判断信号/非信号、查看工程单位、关联信号或补充 KPI 信息时，调用：

`POST /pmsds/service`

body：

```json
{
  "serviceId": "S_DS_AP_19",
  "deviceCode": "<deviceCode>"
}
```

从 `dataList[]` 读取：

- `pointNo`
- `kpiName`
- `collectKpiId`
- `isSignal`
- `hasSignal`
- `relatedSignalKpi`
- 以及响应中存在的单位、采集方式等信息

**优先以 `isSignal` 判断 KPI 类型：**

- `isSignal == "是"` → 信号，走第 5 节。
- `isSignal == "否"` → 非信号，走第 4 节。
- 字段缺失或值异常时，再结合 KPI 名称、用户意图和实际数据接口结果判断；不要在已有 S_DS_AP_19 可用时优先采用试错式探测。

将 S_DS_AP_15 与 S_DS_AP_19 结果关联时，优先使用：

1. 同一 `pointNo` / `collectPointId`
2. 同一 `collectKpiId`
3. 必要时再用 `kpiName` 辅助匹配

如果用户已明确给出 `pointId`、`kpiId` 和数据类型，可直接拉数，不必为了形式上的“核对”调用目录；但当类型未知时，优先调用一次 S_DS_AP_19，而不是先试非信号接口再试信号接口。

完成标准：每个目标均有可用于拉数的 `pointId`、`kpiId`，并确定信号/非信号。

## 4. 非信号

非信号历史原始数据使用免 token 的 busout 接口。

拉取「历史原始数据」时，**单次接口调用的时间范围最大不得超过 30 天**：

- 用户请求的时间范围 ≤ 30 天：一次调用历史原始数据接口，窗口用毫秒。
- 用户请求的时间范围 > 30 天：Agent 自行按连续时间窗口拆成多个 **≤ 30 天** 的分片，不要让用户手工拆分；按第 2 节的并发规则拉取，**总并发不得超过 5**。
- 所有分片完成后，按时间顺序拼接 `timestamps` 及其对应数据；对分片边界可能出现的同一 timestamp 做去重，保证时间序列有序且数据一一对应。
- 任一分片失败时，明确指出失败分片的起止时间和接口错误；不要把缺失分片静默当作完整结果。

`data.timestamps` 非空即为该分片完成。空结果本身不代表鉴权失败，也不要因此索取 token。

完成标准：整个用户时间范围已覆盖并完成拼接；若存在失败分片，则明确标记结果不完整。

## 5. 信号

**默认拉取原始信号数据。** 用户未明确指定数据类型时，不要反问「原始还是降采样」；直接按原始流程执行，并告知用户：**也可以选择降采样数据**。

默认原始信号链路全程免 token：

`busout 采集时刻 → iehmBusOut 元数据 → iehmBusOut 原始分页`

1. **采集时刻**  
   调 busout 的「时间范围内信号点」接口。只要一个点时，取距目标时刻最近的 `timestamp`，并告诉用户该时刻。  
   完成标准：至少一条采集时刻。毫秒 `DTimeMs = timestampNs / 1e6`。

2. **原始（默认，三步不要跳）**  
   - 时刻：上一步已有。  
   - 元数据：用纳秒 `DTime` 调 `/iehmBusOut/` 的「信号详情」，拿到 `hz`、`cl`、`startTime`、`endTime`。缺任一字段则停止并展示必要的业务错误信息；不要因为业务异常改为索取 token。  
   - 分页：用 `startTime`/`endTime` 调 `/iehmBusOut/` 的「原始信号」。`offset=0`，`limit` 取 `min(cl, 50000)`。将每页 `times`/`values` 拼接；`offset += 本页条数`，直到累计条数 ≥ `cl`、或本页为空、或本页条数 < `limit`。  
   完成标准：写明累计点数与 `cl`（含少 1 点），并注明这是原始信号数据。

3. **降采样（可选）**  
   只有用户明确要求服务端降采样时，才使用 api-map 中的降采样能力。该能力如果仍依赖鉴权，则**到这一步再向用户索取 token**，不要因为默认原始信号流程提前索取。  
   交付时写明 `isOriginal` 与 `len(values)` / `cl`，并明确注明结果为降采样数据。

## 6. Token 原则

正常的数据查询闭环应当可以**不要求用户提供 token**：

1. 目录：`S_DS_AP_15`
2. KPI 类型/信息：`S_DS_AP_19`
3. 非信号历史：busout
4. 原始信号：busout + iehmBusOut

只有以下情况才考虑向用户索取 token：

- 用户明确要求某个 api-map 已标记为需要鉴权、且没有等价免 token 替代路径的可选能力，例如当前的服务端降采样接口。
- 当前部署环境对原本已验证免 token 的接口返回了明确鉴权错误，且不存在其他免 token 替代路径。

以下情况**不要**索取 token：

- 用户没给 `pointId` / `kpiId`；直接调用 S_DS_AP_15。
- 需要判断 KPI 是否为信号；直接调用 S_DS_AP_19。
- busout 返回空 timestamps。
- `/pmsds/service` 返回业务空列表。
- `/iehmBusOut/` 返回业务层参数错误、空对象或 Java 异常。
- 仅仅为了“保险起见”。

## 7. 交付

每个数据项至少说明：base URL、设备、测点、kpi、时间窗、调用的 path / serviceId、是否原始/降采样、点数；信号额外给 `cl` / `hz`。用户要求文件时再写 JSON。

默认流程不输出、也不要求 token。若某个可选步骤确实使用了鉴权，只说明“该步骤使用了鉴权”，不要回显 token。

若信号按默认流程返回原始数据，在交付中顺带告知用户：如只需要趋势查看或更小数据量，也可改取降采样数据。
