---
name: x-com-post
description: >
  Access, read, and publish on x.com (Twitter) via agent-browser with the user's Chrome profile.
  Use when the user asks to post/publish/promote on X, or to fetch/get/extract tweet or article
  content (推文, 长文, Article, thread, 获取内容, 抓取, 翻译). Covers Chrome profile selection,
  login verification, content extraction, character limits, and tweet URL retrieval.
  Triggers: /x-com-post, "post on x.com", "发推", "发帖", "获取推文", "x.com 长文", "twitter post".
allowed-tools: Bash(agent-browser:*)
---

# X.com 访问、读取与发布

通过 `agent-browser` 复用用户 Chrome 个人资料的登录态，在 x.com **读取内容**或**发帖**。不依赖 X API，不保存或输出密码。

## 先判断任务类型

| 任务 | 推荐连接方式 | Chrome 是否必须退出 |
|------|-------------|-------------------|
| **读取**推文/长文/线程 | `--auto-connect`（优先） | 否，可附着已开 CDP 的 Chrome |
| **发布**推文 | `--profile "Profile N"` | **是**，必须 Cmd+Q |

```bash
bash ~/.grok/skills/x-com-post/scripts/preflight.sh "Profile N" read   # 读取
bash ~/.grok/skills/x-com-post/scripts/preflight.sh "Profile N" post     # 发帖
```

---

## 连接浏览器

### 读取：优先 auto-connect

```bash
agent-browser --auto-connect get url    # 探测是否可连接
agent-browser --auto-connect open "https://x.com/<user>/status/<id>"
```

成功则直接导航，**不要**要求用户退出 Chrome。

失败（`No running Chrome instance found`）→ 走 Profile 启动：

```bash
agent-browser close
agent-browser --profile "Profile N" --headed open about:blank
agent-browser open "https://x.com/..."
```

### 发帖：必须 Profile 独占

```bash
pgrep -x "Google Chrome" >/dev/null && echo "BLOCKED" || echo "OK"
agent-browser close
agent-browser --profile "Profile N" --headed open about:blank
agent-browser open https://x.com
```

**不要**对默认 Chrome 数据目录使用 `--remote-debugging-port`（Chrome 会拒绝）。

网络自检：x.com 超时 → 先测 `agent-browser open https://www.google.com`；Google 可达但 x.com 不行 → 提示检查代理/VPN。

---

## 选择 Chrome Profile

```bash
agent-browser profiles
```

向用户确认 Profile；对照截图中的邮箱/昵称与列表。

确认目标 Profile 有 X cookie：

```bash
bash ~/.grok/skills/x-com-post/scripts/preflight.sh "Profile N"
```

---

## 验证已登录

```bash
agent-browser snapshot -i
```

**已登录：** `Account menu`、`@用户名`、时间线、文章正文可见。

**未登录：** `使用手机继续`、`电子邮箱或用户名`、`Log in` / `Sign up`。停止自动化，让用户在该 Profile 手动登录。

---

## 读取内容

### 不要用 WebFetch 代替浏览器

`WebFetch` 对 x.com 通常只返回登录墙或卡片摘要（标题 + 封面），**拿不到长文正文**。必须用已登录的浏览器提取。

### 识别 URL 类型

| URL 模式 | 内容类型 | 打开方式 |
|----------|---------|---------|
| `x.com/<user>/status/<id>` | 推文（可能含 Article 卡片） | 直接打开 |
| `x.com/i/article/<id>` | X 长文（Article） | 直接打开（首选） |
| `x.com/<user>` | 用户主页 | 用于定位特定推文 |

### 提取长文（Article）

```bash
# 用户给的是 status 链接时，先打开 status
agent-browser --auto-connect open "https://x.com/<user>/status/<id>"
agent-browser snapshot -i
# 若见到 "Article" 卡片，改开 article 页（从页面链接或 /i/article/<id>）
agent-browser --auto-connect open "https://x.com/i/article/<article_id>"

# 提取正文（get title 常含完整文章；get text body 作备选）
agent-browser --auto-connect get title
agent-browser --auto-connect get text body
```

长文页面 snapshot 中应有多个 `heading`（如 `1. ...`、`2. ...`）。交付时整理为：标题、作者、发布时间、正文（保留章节结构）、原文链接。

### 提取普通推文

```bash
agent-browser --auto-connect open "https://x.com/<user>/status/<id>"
agent-browser snapshot -i          # article 元素含推文全文
agent-browser --auto-connect get text body
```

### 提取线程（Thread）

长线程需多次 `scroll down`，每屏 `snapshot -i` 或 `get text body`，合并去重。若页面有「Show replies」/ 折叠回复，先展开再滚动。

### 读取交付清单

向用户报告：
1. 标题、作者、@handle、发布时间（如有）
2. 完整正文（分节保留 heading）
3. 原文 URL（status 与 article 链接）
4. 互动数据（views/likes/reposts，若可见）
5. 若用户需要，提供中文摘要或译文（单独章节，不覆盖原文）

---

## 发布内容

### 单条推文

```bash
agent-browser open https://x.com/compose/post
agent-browser snapshot -i
agent-browser fill @eXX "推文正文"
agent-browser snapshot -i
# 确认无 "exceeded the character limit"；Post 非 disabled
agent-browser press Escape          # 关闭 hashtag 遮罩
agent-browser click @eYY            # button "Post"
agent-browser wait 3000
```

### 多条推文（如中英文各一条）

每条独立 compose，不要一次 fill 多篇。发完一条后重新 `open https://x.com/compose/post`。

### 字符限制

- 普通账号 **280 字符**（中英文、emoji、URL、#标签均计入）
- `exceeded the character limit by N` → 缩短后**重新 fill**（不要 append）
- 英文推广文通常需比中文更短

### 获取已发推文链接

```bash
agent-browser open https://x.com/<username>
agent-browser snapshot -i
agent-browser click @eTIME          # 点 "Xs ago"，不要点 #标签
agent-browser get url
# 期望: https://x.com/<user>/status/<id>
```

---

## 常见错误与处理

| 现象 | 原因 | 处理 |
|------|------|------|
| WebFetch 只有标题/封面 | 未登录或无 JS 渲染 | 改用 agent-browser |
| `No running Chrome instance found` | 读取时无 CDP | 试 `--profile` 启动，或让用户用带调试端口的 Chrome |
| `Operation timed out` + `about:blank` | Profile 被占用（发帖） | 用户 Cmd+Q 完全退出 Chrome |
| `Element covered by div#layers` | hashtag 补全层遮挡 | `agent-browser press Escape` |
| `Post` disabled | 超字数或正文为空 | snapshot 查字数，缩短后重新 fill |
| 点到 hashtag 页面 | 误点 #标签 | 回 profile/status，改点时间戳链接 |
| 长文不完整 | 未滚到底 | `scroll down` 后重新 `get text body` |

---

## 推广帖模板（发帖时按需改写）

**中文（≤280 字）：**
```
想在 Codex Desktop / CLI 里用 DeepSeek？

用 Cloudflare Worker 把 Codex Responses API 适配到 DeepSeek Chat Completions，支持流式输出、function tools、并行工具调用和 thinking 请求。

🚀 轻量部署，开源可用
🔗 github.com/<org>/<repo>

#DeepSeek #Codex #CloudflareWorkers #AI
```

**英文（需更短）：**
```
Want DeepSeek in Codex Desktop or CLI?

Cloudflare Worker bridging Codex Responses API to DeepSeek: streaming, tools, parallel calls, thinking.

Open source: github.com/<org>/<repo>

#DeepSeek #Codex #CloudflareWorkers
```

---

## 会话持久化

```bash
agent-browser state save ~/.agent-browser/x-auth.json
# 下次：agent-browser --state ~/.agent-browser/x-auth.json --profile "Profile N" open https://x.com
```

---

## 安全

- 不要读取、记录或提交 X 密码
- 不要在输出中泄露 `auth.json` / cookie 内容
- 发帖内容需用户确认；未获同意不要 `@` 他人或发敏感信息
- 读取他人内容时注明作者与原文链接，尊重版权