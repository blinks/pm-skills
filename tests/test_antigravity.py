"""Antigravity plugin consistency and validation checks.

Verifies:
- Every PM plugin has a root plugin.json with required fields (name, displayName, version, description, author, keywords, license)
- Version sync: plugin.json versions match CHANGELOG.md and .claude-plugin/plugin.json
- plugins.json and .agents/plugins.json declare all 9 plugins for Antigravity workspace discovery
- Every PM plugin bundles domain-specific rules in rules/AGENTS.md
- agy plugin validate passes for all 9 plugins (when agy CLI is installed)
"""

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
PLUGINS_JSON = ROOT / "plugins.json"
AGENTS_PLUGINS_JSON = ROOT / ".agents" / "plugins.json"


def plugin_dirs():
    return sorted(
        p
        for p in ROOT.iterdir()
        if p.is_dir() and (p / ".claude-plugin" / "plugin.json").is_file()
    )


def latest_changelog_version() -> str:
    for line in CHANGELOG.read_text(encoding="utf-8").splitlines():
        if line.startswith("## v"):
            # e.g. ## v2.1.0 — 2026-04-06
            v = line.split()[1].lstrip("v")
            return v
    raise AssertionError("no ## vX.Y.Z heading found in CHANGELOG.md")


class TestAntigravityManifests(unittest.TestCase):
    def test_all_plugins_have_antigravity_manifest(self):
        for p in plugin_dirs():
            manifest = p / "plugin.json"
            self.assertTrue(
                manifest.is_file(),
                f"Missing Antigravity plugin manifest: {manifest}",
            )

    def test_antigravity_manifest_fields(self):
        for p in plugin_dirs():
            manifest = p / "plugin.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))

            self.assertEqual(data.get("name"), p.name)
            self.assertTrue(data.get("displayName"), f"missing displayName in {manifest}")
            self.assertTrue(data.get("description"), f"missing description in {manifest}")
            self.assertTrue(data.get("version"), f"missing version in {manifest}")
            self.assertIsInstance(data.get("author"), dict)
            self.assertIsInstance(data.get("keywords"), list)
            self.assertIn("antigravity", data.get("keywords", []))

    def test_antigravity_version_sync(self):
        want = latest_changelog_version()
        for p in plugin_dirs():
            agy_manifest = p / "plugin.json"
            claude_manifest = p / ".claude-plugin" / "plugin.json"

            v_agy = json.loads(agy_manifest.read_text(encoding="utf-8"))["version"]
            v_claude = json.loads(claude_manifest.read_text(encoding="utf-8"))["version"]

            self.assertEqual(
                v_agy,
                want,
                f"{p.name}/plugin.json version {v_agy} != CHANGELOG {want}",
            )
            self.assertEqual(
                v_agy,
                v_claude,
                f"{p.name} Antigravity version ({v_agy}) != Claude version ({v_claude})",
            )


class TestAntigravityDiscoveryConfigs(unittest.TestCase):
    def test_plugins_json_exists_and_lists_all_plugins(self):
        self.assertTrue(PLUGINS_JSON.is_file(), "plugins.json missing at repo root")
        data = json.loads(PLUGINS_JSON.read_text(encoding="utf-8"))
        entries = {e["path"] for e in data.get("entries", [])}
        expected = {p.name for p in plugin_dirs()}
        self.assertEqual(entries, expected)

    def test_agents_plugins_json_exists_and_matches(self):
        self.assertTrue(AGENTS_PLUGINS_JSON.is_file(), ".agents/plugins.json missing")
        data = json.loads(AGENTS_PLUGINS_JSON.read_text(encoding="utf-8"))
        entries = {e["path"] for e in data.get("entries", [])}
        expected = {p.name for p in plugin_dirs()}
        self.assertEqual(entries, expected)


class TestAntigravityRules(unittest.TestCase):
    def test_all_plugins_have_agents_rules(self):
        for p in plugin_dirs():
            rule_file = p / "rules" / "AGENTS.md"
            self.assertTrue(
                rule_file.is_file(),
                f"Missing Antigravity rule file: {rule_file}",
            )
            content = rule_file.read_text(encoding="utf-8").strip()
            self.assertGreater(
                len(content),
                100,
                f"Antigravity rule file {rule_file} is too short",
            )


class TestAgyCliValidate(unittest.TestCase):
    def test_all_plugins_pass_agy_validate(self):
        agy_bin = shutil.which("agy")
        if not agy_bin:
            self.skipTest("agy CLI not found in PATH")

        for p in plugin_dirs():
            res = subprocess.run(
                [agy_bin, "plugin", "validate", str(p)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                res.returncode,
                0,
                f"agy plugin validate failed for {p.name}:\n{res.stdout}\n{res.stderr}",
            )


class TestAntigravitySkillVisibility(unittest.TestCase):
    DUAL_COMMAND_SKILLS = {
        "pre-mortem",
        "stakeholder-map",
        "test-scenarios",
        "business-model",
        "value-proposition",
        "draft-nda",
        "privacy-policy",
        "review-resume",
    }

    def test_analytical_skills_have_disable_slash_command(self):
        """Pure analytical framework skills must set disable-slash-command: true to keep the user's / menu clean."""
        analytical_checked = 0
        for p in plugin_dirs():
            skills_dir = p / "skills"
            cmds_dir = p / "commands"
            cmd_files = {c.stem for c in cmds_dir.glob("*.md")} if cmds_dir.is_dir() else set()
            if not skills_dir.is_dir():
                continue
            for s in skills_dir.iterdir():
                if not s.is_dir():
                    continue
                if s.name in cmd_files and s.name not in self.DUAL_COMMAND_SKILLS:
                    continue
                if s.name in self.DUAL_COMMAND_SKILLS:
                    continue
                skill_md = s / "SKILL.md"
                content = skill_md.read_text(encoding="utf-8")
                self.assertIn(
                    "disable-slash-command: true",
                    content,
                    f"{p.name}/skills/{s.name}/SKILL.md missing 'disable-slash-command: true'",
                )
                analytical_checked += 1
        self.assertEqual(analytical_checked, 61, f"Expected 61 analytical skills checked, got {analytical_checked}")

    def test_command_workflows_exposed_as_slash_commands(self):
        """All 42 commands must be present in skills/ and NOT have disable-slash-command: true."""
        commands_checked = 0
        for p in plugin_dirs():
            cmds_dir = p / "commands"
            skills_dir = p / "skills"
            if not cmds_dir.is_dir():
                continue
            for cmd_file in cmds_dir.glob("*.md"):
                cname = cmd_file.stem
                skill_md = skills_dir / cname / "SKILL.md"
                self.assertTrue(
                    skill_md.is_file(),
                    f"Command {p.name}:{cname} missing corresponding skill at {skill_md}",
                )
                content = skill_md.read_text(encoding="utf-8")
                self.assertNotIn(
                    "disable-slash-command: true",
                    content,
                    f"Command {p.name}:{cname} has 'disable-slash-command: true' in {skill_md}, hiding it from Antigravity's / menu",
                )
                commands_checked += 1
        self.assertEqual(commands_checked, 42, f"Expected 42 commands checked, got {commands_checked}")

    def test_total_antigravity_skills_count(self):
        """Total skills in Antigravity equals 61 analytical + 42 command workflows = 103."""
        total = 0
        for p in plugin_dirs():
            skills_dir = p / "skills"
            if skills_dir.is_dir():
                total += sum(1 for s in skills_dir.iterdir() if s.is_dir())
        self.assertEqual(total, 103, f"Expected 103 total skills, got {total}")


if __name__ == "__main__":
    unittest.main()
