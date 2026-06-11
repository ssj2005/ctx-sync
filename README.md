<p align="center">
  <strong>ctx-sync</strong>
  <br>
  <em>Sync AI coding tool configs. Score quality. Stay consistent.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/ctx-sync/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/status-alpha-orange.svg" alt="Alpha">
</p>

---

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
pip install -e .
```

```bash
# Scan a project for existing AI configs
ctx-sync init

# Score config quality (0-100)
ctx-sync score

# Sync CLAUDE.md to all other formats
ctx-sync sync CLAUDE.md

# Preview without writing
ctx-sync sync CLAUDE.md --dry-run

# Sync only to specific formats
ctx-sync sync CLAUDE.md --to agents-md --to cursorrules

# Compare differences between config files
ctx-sync diff
```

## How It Works

### `ctx-sync init` — Detect configs

```
$ ctx-sync init

                  Detected AI Config Files
+----------------------------------------------------------+
| Tool                             | Path          | Size  |
|----------------------------------+---------------+-------|
| Claude Code (CLAUDE.md)          | CLAUDE.md     | 1,003B|
| Cursor (.cursorrules)            | .cursorrules  |   974B|
| GitHub Copilot (copilot-...)     | .github/...   |   920B|
+----------------------------------------------------------+

Found 3 config formats. Use ctx-sync sync to keep them synchronized.
```

### `ctx-sync score` — Quality scoring

Scores your config file across 6 dimensions (total 100 points):

| Dimension | Max | What it checks |
|-----------|-----|----------------|
| Commands | 30 | Are build/test/lint/dev commands present? (most valuable per research) |
| Architecture | 20 | Is project structure documented? |
| Conventions | 15 | Are coding rules specified? |
| Conciseness | 15 | Is it in the optimal 50-200 line range? |
| Freshness | 10 | Do referenced file paths still exist? |
| Security | 10 | Are there leaked secrets/credentials? |

```
$ ctx-sync score CLAUDE.md

+-------------------------- Claude Code (CLAUDE.md) --------------------------+
| CLAUDE.md                 Score: 97/100  Grade: A                            |
+-----------------------------------------------------------------------------+

| Dimension    | Score | Max |
|--------------|-------+-----|
| Commands     |    30 |  30 |
| Architecture |    20 |  20 |
| Conventions  |    15 |  15 |
| Conciseness  |    15 |  15 |
| Freshness    |     7 |  10 |
| Security     |    10 |  10 |
```

Based on findings from [arXiv 2602.11988](https://arxiv.org/abs/2602.11988): exact commands are the most valuable context, and verbose configs *reduce* task success rates.

### `ctx-sync sync` — Cross-format sync

Converts between any supported formats. Works in any direction:

```bash
# From CLAUDE.md to everything else
ctx-sync sync CLAUDE.md

# From .cursorrules to Claude Code + Copilot
ctx-sync sync .cursorrules -t claude-md -t copilot

# From AGENTS.md to Cursor
ctx-sync sync AGENTS.md -t cursorrules
```

### `ctx-sync diff` — Compare configs

When a project has multiple config files, shows what each one covers:

```
$ ctx-sync diff

| Section       | agents-md    | cursorrules  | copilot      |
|---------------|--------------|--------------|--------------|
| Commands      | OK (4 items) | OK (4 items) | OK (4 items) |
| Architecture  | OK (5 items) | OK (5 items) | OK (5 items) |
| Conventions   | OK (4 items) | OK (4 items) | OK (4 items) |
| Quality score | 97/100 (A)   | 92/100 (A)   | 81/100 (A)   |
```

## Architecture

```
Source file ──► Parser ──► SyncContext ──► Renderer ──► Target file
                          (unified model)
```

Every format has a **Parser** (file → structured data) and a **Renderer** (structured data → file). The sync engine converts through a unified intermediate model, so adding a new format only requires writing one parser + one renderer.

## Supported Formats

| Format | File | Tool |
|--------|------|------|
| `claude-md` | `CLAUDE.md` | Claude Code |
| `agents-md` | `AGENTS.md` | OpenCode / Codex |
| `cursorrules` | `.cursorrules` | Cursor |
| `cursor-mdc` | `.cursor/rules/*.mdc` | Cursor (current) |
| `copilot` | `.github/copilot-instructions.md` | GitHub Copilot |

All conversions work in **any direction** — CLAUDE.md to .cursorrules, .cursorrules to AGENTS.md, copilot to CLAUDE.md, etc.

## Installation

```bash
# From source
git clone https://github.com/YOUR_USERNAME/ctx-sync.git
cd ctx-sync
pip install -e .

# Verify
ctx-sync --help
```

Requires **Python 3.10+**. No other runtime dependencies (only `typer` and `rich`).

## Development

```bash
pip install -e .
pip install pytest

# Run tests
pytest

# Try on the sample fixtures
ctx-sync init tests/fixtures/sample-claude-md
ctx-sync score tests/fixtures/sample-claude-md
ctx-sync sync tests/fixtures/sample-claude-md/CLAUDE.md --dry-run
```

## Roadmap

- [ ] `ctx-sync watch` — file watcher for auto-sync on changes
- [ ] `.ctx-sync.toml` — project-level config (source of truth, field exclusions)
- [ ] `--ci` mode — GitHub Action integration (PR checks for config quality)
- [ ] Community templates — best-practice config templates per tech stack
- [ ] Web UI — visual dashboard for scoring and comparison
- [ ] More formats — Windsurf (`.windsurfrules`), Aider (`.aider.conf.yml`)
- [ ] PyPI publish — `pip install ctx-sync`

## Contributing

Contributions welcome! Especially:

- New format parsers/renderers (Windsurf, Aider, Continue.dev, etc.)
- Community config templates for popular stacks
- Bug fixes and test coverage
- Documentation improvements

## License

MIT
