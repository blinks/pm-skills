# AGENTS.md

Guidance for AI agents (Google Antigravity, Claude Code, and others) working in this repository.
The unified single source of truth for repository structure and development procedures is **[CLAUDE.md](CLAUDE.md)**.

## Antigravity Plugin Architecture

This repository ships dual-platform plugins compatible with both Claude Code and Google Antigravity:

- **Manifests**: Every plugin directory (`pm-*`) contains a native Antigravity manifest `plugin.json` at its root, alongside `.claude-plugin/plugin.json`.
- **Workspace Discovery**: `plugins.json` and `.agents/plugins.json` declare all 9 plugins, enabling automatic discovery in any Antigravity workspace.
- **Rules**: Each plugin contains `rules/AGENTS.md`, which Antigravity automatically merges into the active rule budget when that plugin is active.
- **Commands & Workflows**: Commands in `commands/*.md` are ingested and automatically converted to skills by Antigravity CLI and runtime (`agy plugin validate`).
- **Validation**: Run `python3 validate_plugins.py` and `python3 -m unittest discover -s tests` (which includes `tests/test_antigravity.py` and runs `agy plugin validate`).

Always read [CLAUDE.md](CLAUDE.md) for full design rules, release procedures, and version synchronization invariants.
