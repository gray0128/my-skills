# my-skills

[English](./README.md) | [简体中文](./README-zh.md)

个人 Agent Skills 集合，按主题目录分组。

## 目录结构

| 目录 | 覆盖范围 |
|------|----------|
| [engineering/](./engineering/) | 判断方案、方向与决策，不改被审视的实现 |
| [design/](./design/) | 设计不像机器生成的界面 |
| [data/](./data/) | 按 HTTP 接口拉取业务数据 |

分组只影响仓库组织方式：每个 skill 保留自己的目录名，因此安装 `engineering/brutal-advisor` 得到的技能名仍是 `brutal-advisor`。主题是开放集合——新技能找不到合适归属时，新建一个主题，而不是塞进一个不对的主题。

## Skills

### engineering/

本主题只做判断：对方案、方向或决策加压审视，不改被审视对象的实现。

| Skill | 产物 | 说明 |
|-------|------|------|
| [brutal-advisor](./engineering/brutal-advisor/) | 聊天回复 | 直言不讳的战略顾问与认知镜子：追根因与假设审计、盲区与机会成本、重定义问题、按优先级排序的行动方案 |

### design/

本主题的技能产出视觉成品，而不是对已有工作的判断。核心是工艺：跳出最大概率的下一个 token，做出有明确主张的东西。

| Skill | 说明 |
|-------|------|
| [world-class-designer](./design/world-class-designer/) | 世界级工作室水准的界面设计与打磨，避免通用 AI 味：随机种子发散、盲审截图评审闭环、减法打磨、人工重写文案 |

### data/

| Skill | 说明 |
|-------|------|
| [fetch-device-data](./data/fetch-device-data/) | 按 HTTP 接口拉取设备非信号时序和信号波形：确认 base URL、设备与时间范围；数据项可用户指定或由 Agent 查目录获得（默认免 token）；信号为采集时刻 → 元数据 → 分页原始点 |

## 安装

用 [`skills`](https://skills.sh) CLI 安装。它读取本仓库，让你选择装哪些技能、装到哪些宿主，再写进各宿主的 skills 目录。

```bash
npx skills add gray0128/my-skills
```

加 `-g -y` 可跳过交互、直接全局安装。其他用法：

```bash
npx skills add gray0128/my-skills --list                                  # 先看仓库里有什么
npx skills add gray0128/my-skills --skill brutal-advisor --agent claude-code # 单个技能装到单个宿主
npx skills add gray0128/my-skills --skill '*' --agent '*' -g -y           # 全部技能装到全部已识别宿主
npx skills add ./ --skill fetch-device-data -g -y                          # 在本地克隆里安装
```

技能以自身目录名安装；上一层的主题目录只属于本仓库，不参与安装。

如果目标宿主不在 CLI 支持的范围内，直接把技能目录复制进该宿主的 skills 目录。

安装 `brutal-advisor` 与 `world-class-designer`（单文件技能）：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
for skill in brutal-advisor world-class-designer; do
  cp -R "/tmp/my-skills/$skill" ~/.agents/skills/
done
```

## 使用

按宿主的既有方式调用技能：斜杠命令，或与技能 description 匹配的自然语言。
