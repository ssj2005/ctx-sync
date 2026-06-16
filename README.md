<p align="center">
  <strong>ctx-sync</strong>
  <br>
  <em>Sync AI coding tool configs. Score quality. Stay consistent.</em>
</p>

<p align="center">
  <a href="#中文文档">中文</a> | <a href="#english">English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/status-alpha-orange.svg" alt="Alpha">
</p>

---

# 中文文档

## 解决什么问题

你在用 **多个 AI 编码工具** — Claude Code、OpenCode、Cursor、GitHub Copilot — 可能同时在一个项目里用。

每个工具读自己的配置文件：

| 工具 | 配置文件 |
|------|---------|
| Claude Code | `CLAUDE.md` |
| OpenCode / Codex | `AGENTS.md` |
| Cursor | `.cursorrules` |
| GitHub Copilot | `.github/copilot-instructions.md` |

**三个痛点：**

1. **配置漂移** — 你在 Claude Code 里踩了坑，写进了 CLAUDE.md。Cursor 和 Copilot 完全不知道。
2. **碎片化** — 每个文件都是同一份信息的不同版本，内容不一致。
3. **不知道写得好不好** — 你不知道配置文件是在帮 AI 还是在害它。（研究表明，过长的配置文件会**降低** AI 任务成功率约 20%。）

**ctx-sync 一次解决这三个问题。**

## 30 秒上手

```bash
git clone https://github.com/ssj2005/ctx-sync.git
cd ctx-sync
pip install -e .
```

```bash
# 扫描项目里有哪些 AI 配置文件
ctx-sync init

# 给配置文件打质量分（0-100）
ctx-sync score

# 把 CLAUDE.md 一键同步到其他所有格式
ctx-sync sync CLAUDE.md

# 只预览不写入
ctx-sync sync CLAUDE.md --dry-run

# 只同步到指定格式
ctx-sync sync CLAUDE.md --to agents-md --to cursorrules

# 对比项目中不同配置文件的差异
ctx-sync diff
```

## 功能演示

### `ctx-sync init` — 检测配置文件

```
$ ctx-sync init

                  检测到的 AI 配置文件
+----------------------------------------------------------+
| 工具                             | 路径          | 大小  |
|----------------------------------+---------------+-------|
| Claude Code (CLAUDE.md)          | CLAUDE.md     | 1,003B|
| Cursor (.cursorrules)            | .cursorrules  |   974B|
| GitHub Copilot (copilot-...)     | .github/...   |   920B|
+----------------------------------------------------------+

检测到 3 种配置格式，建议设置同步。
```

### `ctx-sync score` — 质量评分

从 6 个维度给你的配置文件打分（满分 100）：

| 维度 | 满分 | 检查什么 |
|------|------|---------|
| Commands 命令 | 30 | 有没有 build/test/lint/dev 命令（研究表明这是最有价值的信息） |
| Architecture 架构 | 20 | 有没有项目结构说明 |
| Conventions 约定 | 15 | 有没有编码规范 |
| Conciseness 简洁度 | 15 | 是否在 50-200 行最佳区间 |
| Freshness 时效性 | 10 | 引用的文件路径是否还存在 |
| Security 安全 | 10 | 有没有泄露的密钥 |

```
$ ctx-sync score CLAUDE.md

  CLAUDE.md    Score: 97/100    Grade: A

  Commands        ██████████████████████████████  30/30
  Architecture    ████████████████████████  20/20
  Conventions     ███████████████████  15/15
  Conciseness     ███████████████████  15/15
  Freshness       ██████████████  7/10
  Security        ███████████████████  10/10
```

### `ctx-sync sync` — 跨格式同步

任意方向互转，已支持 5 种格式：

```bash
# CLAUDE.md → 全部其他格式
ctx-sync sync CLAUDE.md

# .cursorrules → Claude Code + Copilot
ctx-sync sync .cursorrules -t claude-md -t copilot

# AGENTS.md → Cursor
ctx-sync sync AGENTS.md -t cursorrules
```

### `ctx-sync diff` — 差异对比

一个项目里有多个配置文件时，一目了然看到各自覆盖情况：

```
$ ctx-sync diff

| 维度     | agents-md    | cursorrules  | copilot      |
|---------|--------------|--------------|--------------|
| 命令     | ✓ (4条)      | ✓ (4条)      | ✓ (4条)      |
| 架构     | ✓ (5条)      | ✓ (5条)      | ✓ (5条)      |
| 约定     | ✓ (4条)      | ✓ (4条)      | ✓ (4条)      |
| 质量分   | 97/100 (A)   | 92/100 (A)   | 81/100 (A)   |
```

## 支持的格式

| 格式参数 | 输出文件 | 对应工具 |
|---------|---------|---------|
| `claude-md` | `CLAUDE.md` | Claude Code |
| `agents-md` | `AGENTS.md` | OpenCode / Codex |
| `cursorrules` | `.cursorrules` | Cursor |
| `cursor-mdc` | `.cursor/rules/*.mdc` | Cursor (新版) |
| `copilot` | `.github/copilot-instructions.md` | GitHub Copilot |

所有转换**双向支持** — CLAUDE.md → .cursorrules、.cursorrules → AGENTS.md、copilot → CLAUDE.md，任意组合都行。

## 典型使用场景

### 场景 1：主力 Claude Code，同时适配 Cursor + Copilot

```bash
ctx-sync sync CLAUDE.md -t cursorrules -t copilot
```

### 场景 2：从 Cursor 迁移到 OpenCode

```bash
ctx-sync sync .cursorrules -t agents-md -t claude-md
```

### 场景 3：检查配置文件质量

```bash
ctx-sync score
```

得分低于 B（60 分）就按建议改进。

### 场景 4：保持多工具配置一致

先写好 CLAUDE.md，然后一键生成全部：

```bash
ctx-sync sync CLAUDE.md
```

## 技术架构

```
源文件 ──► 解析器(Parser) ──► SyncContext ──► 渲染器(Renderer) ──► 目标文件
                            (统一数据模型)
```

每种格式有一个解析器和一个渲染器。同步引擎通过统一的中间模型转换，添加新格式只需要写一个 parser + 一个 renderer。

## 路线图

- [x] 5 种格式双向同步
- [x] 质量评分系统
- [x] 配置文件差异对比
- [ ] `ctx-sync watch` — 文件监听，改动后自动同步
- [ ] `.ctx-sync.toml` — 项目级配置（指定主文件、排除字段）
- [ ] `--ci` 模式 — GitHub Action 集成（PR 检查配置质量）
- [ ] 社区模板 — 各技术栈的最佳配置模板
- [ ] Web UI — 可视化评分和对比仪表盘
- [ ] 更多格式 — Windsurf、Aider、Continue.dev
- [ ] PyPI 发布 — `pip install ctx-sync`

## 参与贡献

欢迎 PR，特别需要：

- 新格式支持（Windsurf、Aider 等）
- 各技术栈的最佳配置模板
- Bug 修复和测试覆盖
- 文档改进

## License

MIT

---

# English

## The Problem

You use **multiple AI coding tools** — Claude Code, OpenCode, Cursor, GitHub Copilot — sometimes in the same project.

Each tool reads its own config file:

| Tool | Config File |
|------|-------------|
| Claude Code | `CLAUDE.md` |
| OpenCode / Codex | `AGENTS.md` |
| Cursor | `.cursorrules` |
| GitHub Copilot | `.github/copilot-instructions.md` |

**Three problems:**

1. **Drift** — You discover a gotcha in Claude Code and write it in `CLAUDE.md`. Cursor and Copilot don't know about it.
2. **Fragmentation** — Each file is a slightly different version of the same information.
3. **No quality feedback** — You don't know if your config file is actually helping or hurting the AI. (Research shows verbose configs *reduce* task success by ~20%.)

**ctx-sync fixes all three.**

## Quick Start

```bash
git clone https://github.com/ssj2005/ctx-sync.git
cd ctx-sync
pip install -e .
```

```bash
ctx-sync init                                    # detect configs
ctx-sync score                                   # quality scoring
ctx-sync sync CLAUDE.md                          # sync to all formats
ctx-sync sync CLAUDE.md --dry-run                # preview only
ctx-sync sync CLAUDE.md -t agents-md -t cursorrules  # specific targets
ctx-sync diff                                    # compare configs
```

## Supported Formats

| Format | File | Tool |
|--------|------|------|
| `claude-md` | `CLAUDE.md` | Claude Code |
| `agents-md` | `AGENTS.md` | OpenCode / Codex |
| `cursorrules` | `.cursorrules` | Cursor |
| `cursor-mdc` | `.cursor/rules/*.mdc` | Cursor (current) |
| `copilot` | `.github/copilot-instructions.md` | GitHub Copilot |

All conversions work in **any direction**.

## License

MIT
