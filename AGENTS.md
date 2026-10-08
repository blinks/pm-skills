# AGENTS.md

Guidance for AI agents (Google Antigravity, Claude Code, and others) working in this repository.
The unified single source of truth for repository structure and development procedures is **[CLAUDE.md](CLAUDE.md)**.

## Antigravity Plugin Architecture

This repository ships dual-platform plugins compatible with both Claude Code and Google Antigravity:

- **Manifests**: Every plugin directory (`pm-*`) contains a native Antigravity manifest `plugin.json` at its root, alongside `.claude-plugin/plugin.json`.
- **Workspace Discovery**: `plugins.json` and `.agents/plugins.json` declare all 9 plugins, enabling automatic discovery in any Antigravity workspace.
- **Rules**: Each plugin contains `rules/AGENTS.md`, which Antigravity automatically merges into the active rule budget when that plugin is active.
- **Commands & Workflows**: In Antigravity, user-facing slash commands are registered from skills in `skills/<command>/SKILL.md` (omitting `disable-slash-command: true`). Analytical framework skills set `disable-slash-command: true` to remain model-only. Both Claude Code's `commands/` directory and Antigravity's unified `skills/` directory are maintained.
- **Validation**: Run `python3 validate_plugins.py` and `python3 -m unittest discover -s tests` (which includes `tests/test_antigravity.py` and runs `agy plugin validate`).

Always read [CLAUDE.md](CLAUDE.md) for full design rules, release procedures, and version synchronization invariants.
