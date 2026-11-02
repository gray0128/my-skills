# AGENTS.md

本仓库是一组 Agent Skills。这份文件只写**操作步骤**：新增一个技能、修改一个现有技能时按什么顺序做、做到什么算完成。

约束不在本文件——命名、自包含、安装边界、触发方式、主题的成立标准由 [`architecture.md`](./architecture.md) 定义，主题职责由各主题目录的 `SPEC.md` 定义。动手前读这两处，本文件只把它们串成一条可执行的路径。

## 落点判据

新增时的第一个问题是“放哪”，分两级判断，先主题后技能。

**主题：现有主题能装下它吗？** 当前是 `engineering`、`tools`、`design`、`data`。

- 有合适的 → 进那个主题。
- 都装不下 → **新建一个主题**。这不是例外情况，`architecture.md` 把主题定为开放集合。起名照那两条标准来：按“在做什么”分而非“用了什么技术”分，按可预见的下一个成员命名而非为当前这一个量身定做。

新建主题属于架构变更：先改 `architecture.md` 的拓扑与 `goal` 的能力清单，再建目录。顺序反了，spec 描述的结构与磁盘就会不一致。

**技能：该主题已有的能覆盖它吗？** 判据是能一句话说出两者的区别。

- 说得出 → 建新技能。
- 说不出 → 并入已有技能，而不是并排放两个近似的。

完成标准：能指出 `<topic>/<skill>` 路径，并说出该主题 `SPEC.md` 里已有哪几个技能、新的这个与之差在哪。

## 新增技能

1. **读落点**。打开目标主题的 `SPEC.md`，通读它的职责与全部约束节——节名各主题不统一（`Boundary`、`Invariants`、`Composition Rule` 都有），不要只找其中一个。完成标准：技能职责落在该主题的 Responsibility 之内，且不违反它写的任一约束。

2. **建 `SKILL.md`**。路径 `<topic>/<skill>/SKILL.md`，frontmatter 按 `architecture.md` 的命名与触发约束填，正文写清“什么时候用、怎么做、做到什么算完成”。完成标准：结构检查通过（见校验节第一段）。

3. **只建真正需要的子目录**。`references/`、`assets/`、`scripts/`、`tests/`、`evals/`、`agents/` 按需创建。完成标准：每个建出来的目录都有文件落脚。

4. **脚本单独验证**。技能带 `scripts/` 时，从**技能目录内**按 `SKILL.md` 里写的命令原样执行一次。完成标准：命令不用改路径就能跑通——这同时验证了自包含约束。

5. **同步两处清单**。先改主题的 `SPEC.md` 技能表（权威），再改 `README.md` 与 `README-zh.md` 的技能表。完成标准：三处技能名集合与磁盘目录完全一致。

6. **跑全部校验**。下节三段都要过。

## 更新技能

先改 `SKILL.md`，再按改动性质往上查：

| 改动性质 | 还要做 |
|---|---|
| 只改步骤措辞、示例 | 无 |
| 改了 `scripts/` | 在技能目录内跑该技能的 `tests/`（有的话），并按文档原样执行一次命令 |
| 新增或删除能力，职责变了 | 改主题 `SPEC.md` 的职责、边界与技能表 |
| 目录名或 `name` 变了 | 改主题 `SPEC.md`、两份 README 的表格与链接；目录与 `name` 同改 |
| 触发方式在自主与显式之间切换 | 无——`architecture.md` 已声明两条路径都合法 |
| 新增或删除技能 | 主题 `SPEC.md` + 两份 README；删之前确认没有别处链接到它 |
| 主题拆分、合并或改名 | 先改 `architecture.md`，再搬目录，最后同步各 `SPEC.md` 与 README |
| 拓扑、不变量、安装方式变了 | 先改 `architecture.md`，再改文件 |

表格答不上来时，回到 `architecture.md` 找对应约束，而不是自行推断。

## 校验

第一段：结构。每步都能跑，新技能建完时先跑它。

```bash
bad=0
[ -e SKILL.md ] && { echo "ROOT SKILL.md：仓库根不是技能目录"; bad=1; }
for f in */SKILL.md; do
  [ -e "$f" ] && { echo "STRAY $f 必须位于 <topic>/<skill>/"; bad=1; }
done
for f in */*/SKILL.md; do
  n=$(awk -F': ' '/^name:/{print $2; exit}' "$f")
  d=$(basename "$(dirname "$f")")
  [ "$n" = "$d" ] || { echo "MISMATCH $f name=$n dir=$d"; bad=1; }
  grep -q '^description:' "$f" || { echo "NO-DESCRIPTION $f"; bad=1; }
done
[ "$bad" = 0 ] && echo "OK：结构通过"
```

第二段：清单与引用。全部改完后跑。

```bash
bad=0
disk=$(for f in */*/SKILL.md; do basename "$(dirname "$f")"; done | sort)
spec=$(grep -hoE '^\| `[a-z0-9-]+`' */SPEC.md | tr -d '|` ' | sort)
en=$(grep -hoE '^\| \[[a-z0-9-]+\]' README.md | sed 's/| \[//; s/\]//' | sort)
zh=$(grep -hoE '^\| \[[a-z0-9-]+\]' README-zh.md | sed 's/| \[//; s/\]//' | sort)
diff <(echo "$disk") <(echo "$spec") || { echo "↑ SPEC 与磁盘不一致"; bad=1; }
diff <(echo "$disk") <(echo "$en")   || { echo "↑ README 与磁盘不一致"; bad=1; }
diff <(echo "$disk") <(echo "$zh")   || { echo "↑ README-zh 与磁盘不一致"; bad=1; }
broken=$(for f in README.md README-zh.md; do
  grep -oE '\]\(\./[^)]+\)' "$f" | sed 's/](\.\///; s/)$//' | while read -r p; do
    [ -e "$p" ] || echo "$f -> ./$p"
  done
done)
[ -n "$broken" ] && { echo "BROKEN 链接："; echo "$broken"; bad=1; }
[ "$bad" = 0 ] && echo "OK：清单与链接通过"
```

两段各以 `OK：…` 结尾才算通过；出现任何其它输出都说明有问题。它们盖住这些故障：技能落在错误层级、`name` 与目录名不一致、缺 `description`、新增或删除技能后三处清单没跟上、目录改名后残留 404 链接。

第三段：spec graph。`spec_validate` 是宿主提供的工具，**不是 shell 命令**——有它就调用它；没有就至少跑下面这段，检查每个 `parent` 指向的 id 确实存在。

```bash
ids=$(grep -hE '^id:' *.md */SPEC.md 2>/dev/null | awk '{print $2}' | sort -u)
dangling=$(for f in *.md */SPEC.md; do
  awk -v F="$f" '/^parent:/{print F" "$2}' "$f"
done | while read -r f p; do
  printf '%s\n' "$ids" | grep -qx "$p" || echo "$f parent=$p"
done)
[ -n "$dangling" ] && { echo "DANGLING parent："; echo "$dangling"; } || echo "OK：spec 链接通过"
```

无输出即通过。完整的工具版校验还会查重复 id 与父子环，这段只覆盖悬空 `parent`。
