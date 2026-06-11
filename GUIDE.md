# ctx-sync 使用指南

跨 AI 编码工具配置文件同步 + 质量评分。

---

## 一、环境要求

| 项目 | 最低版本 | 说明 |
|------|---------|------|
| Python | >= 3.10 | 项目 `pyproject.toml` 中声明了 `requires-python = ">=3.10"` |
| pip | >= 21.3 | 需要支持 editable 安装模式 (`pip install -e .`) |

不需要 Node.js、不需要 uv、不需要虚拟环境（但推荐用）。

---

## 二、从零安装（5 分钟）

### 第 1 步：确认 Python 已安装

打开终端（CMD / PowerShell / Windows Terminal 都行），运行：

```bash
python --version
```

应该看到类似：

```
Python 3.13.12
```

如果版本 >= 3.10，直接跳到第 2 步。

**如果没装 Python：**

去 https://www.python.org/downloads/ 下载 Python 3.12+，安装时**勾选 "Add Python to PATH"**。

### 第 2 步：进入项目目录

```bash
cd D:\ssj\learning\myagents
```

### 第 3 步：安装项目（连同依赖一起装）

```bash
pip install -e .
```

这个命令会：
1. 安装两个依赖包：`typer`（CLI 框架）和 `rich`（终端美化输出）
2. 以"可编辑模式"安装本项目，改代码后立即生效，不需要重新安装
3. 注册命令行命令 `ctx-sync`

安装成功后会看到：

```
Successfully installed typer-x.x.x ctx-sync-0.1.0
```

### 第 4 步：验证安装

```bash
ctx-sync --help
```

应该看到：

```
 Usage: ctx-sync [OPTIONS] COMMAND [ARGS]...

 Sync AI coding tool configs. Score quality. Stay consistent.

 Commands:
   init   Scan a project for AI config files.
   score  Score the quality of AI config files.
   sync   Sync a config file to other AI tool formats.
   diff   Compare differences between config files in a project.
```

看到这个就说明安装成功。

---

## 三、使用方法

### 命令 1：`ctx-sync init` — 检测项目配置文件

扫描一个项目目录，找出里面有哪些 AI 配置文件。

```bash
# 扫描当前目录
ctx-sync init

# 扫描指定目录
ctx-sync init D:\my-project

# 扫描测试样本
ctx-sync init tests\fixtures\sample-claude-md
```

### 命令 2：`ctx-sync score` — 配置文件质量评分

分析配置文件质量，给出 0-100 分和改进建议。

```bash
# 评分当前目录下所有配置文件
ctx-sync score

# 评分指定文件
ctx-sync score CLAUDE.md
ctx-sync score .cursorrules

# 评分指定目录
ctx-sync score D:\my-project
```

评分维度（满分 100）：

| 维度 | 满分 | 说明 |
|------|------|------|
| Commands | 30 | build/test/lint/dev 命令是否存在 |
| Architecture | 20 | 有无目录结构或架构说明 |
| Conventions | 15 | 代码风格/命名约定 |
| Conciseness | 15 | 是否在 50-200 行最佳区间 |
| Freshness | 10 | 引用的文件是否还存在 |
| Security | 10 | 是否包含泄露的密钥 |

等级：A (>=80) / B (>=60) / C (>=40) / D (<40)

### 命令 3：`ctx-sync sync` — 跨格式同步

把一个配置文件转换成其他工具的格式。

```bash
# 把 CLAUDE.md 同步到所有其他格式（实际写入文件）
ctx-sync sync CLAUDE.md

# 只预览，不写入文件
ctx-sync sync CLAUDE.md --dry-run

# 只同步到指定格式
ctx-sync sync CLAUDE.md --to agents-md --to cursorrules

# 同步到指定输出目录
ctx-sync sync CLAUDE.md --output D:\my-project

# 完整示例：从 .cursorrules 同步到 CLAUDE.md 和 copilot
ctx-sync sync .cursorrules -t claude-md -t copilot
```

支持的格式名称：

| 参数值 | 对应文件 | AI 工具 |
|--------|---------|---------|
| `claude-md` | CLAUDE.md | Claude Code |
| `agents-md` | AGENTS.md | OpenCode / Codex |
| `cursorrules` | .cursorrules | Cursor |
| `copilot` | .github/copilot-instructions.md | GitHub Copilot |

### 命令 4：`ctx-sync diff` — 比较配置文件差异

当一个项目里有多种格式的配置文件时，比较它们的内容覆盖情况。

```bash
ctx-sync diff

ctx-sync diff D:\my-project
```

输出一个对比表格，显示每种格式在 commands、architecture、conventions 等维度上的覆盖情况。

---

## 四、实际使用场景

### 场景 1：你用 Claude Code 开发，想同时支持 Cursor

```bash
cd your-project
ctx-sync sync CLAUDE.md --to cursorrules --to copilot
```

项目里会自动生成 `.cursorrules` 和 `.github/copilot-instructions.md`。

### 场景 2：你从 Cursor 迁移到 OpenCode

```bash
ctx-sync sync .cursorrules --to agents-md --to claude-md
```

### 场景 3：检查配置文件质量

```bash
ctx-sync score
```

如果得分低于 B（60 分），按 Suggestion 改进。

### 场景 4：保持多个工具配置一致

先写好 CLAUDE.md，然后：

```bash
ctx-sync sync CLAUDE.md
```

自动生成 AGENTS.md + .cursorrules + copilot-instructions.md。

---

## 五、常见问题

### Q: 运行 `ctx-sync` 提示"不是内部或外部命令"

安装没成功或 PATH 没刷新。重新运行 `pip install -e .`，然后**重新打开终端**。

### Q: `pip install -e .` 报错 "Readme file does not exist"

确保项目根目录下有 `README.md` 文件。

### Q: 想卸载

```bash
pip uninstall ctx-sync
```

### Q: 想在虚拟环境中用（推荐）

```bash
cd D:\ssj\learning\myagents
python -m venv .venv
.venv\Scripts\activate
pip install -e .
ctx-sync --help
```

### Q: 改了源码后需要重新安装吗

不需要。`-e` 模式下修改源码直接生效，下次运行 `ctx-sync` 就会用最新代码。

---

## 六、项目文件结构

```
myagents/
├── pyproject.toml          ← 项目配置
├── README.md               ← 基本说明
├── src/ctx_sync/
│   ├── cli.py              ← 命令行入口
│   ├── models.py           ← 数据模型
│   ├── detectors.py        ← 配置文件检测
│   ├── syncer.py           ← 同步引擎
│   ├── scorer.py           ← 质量评分
│   ├── parsers/            ← 各格式解析器
│   │   ├── claude_md.py
│   │   ├── agents_md.py
│   │   ├── cursorrules.py
│   │   ├── cursor_mdc.py
│   │   └── copilot.py
│   └── renderers/          ← 各格式输出器
│       ├── claude_md.py
│       ├── agents_md.py
│       ├── cursorrules.py
│       └── copilot.py
└── tests/fixtures/         ← 测试样本文件
    ├── sample-claude-md/
    ├── sample-agents-md/
    └── sample-cursorrules/
```

## 七、最低限度速查

只装了 Python 3.10+ 的情况下，两行命令就能跑：

```bash
cd D:\ssj\learning\myagents
pip install -e .
ctx-sync --help
```

完事。
