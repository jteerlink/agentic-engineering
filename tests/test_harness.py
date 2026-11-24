import json
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/agentic-engineering"  # the installer skill the plugins ship
# ponytail: deliberately absent paths; GLOSSARY.md is created lazily, .scratch/ is gitignored
ABSENT_OK = {"GLOSSARY.md", ".scratch", "docs/features", "validate_harness.py"}
# Skills written here, not adapted from mattpocock/skills, so they carry no MIT attribution
ORIGINAL_SKILLS = {"run-tickets"}


def named_paths(text):
    for tok in re.findall(r"`([^`\s]+)`", text):
        if re.search(r"[<{*~@]", tok) or tok.startswith(("/", "-")):
            continue
        if "/" in tok or re.search(r"\.(md|toml|yaml|py)$", tok):
            yield tok.rstrip("/")


class Harness(unittest.TestCase):
    def test_docs_paths_exist(self):
        for doc in ("AGENTS.md", "ARCHITECTURE.md"):
            for p in named_paths((ROOT / doc).read_text()):
                if p not in ABSENT_OK and p.split("/")[0] not in ABSENT_OK:
                    self.assertTrue((ROOT / p).exists(), f"{doc} names `{p}`, which does not exist. Fix the path or the doc.")

    def test_skill_md_assets_exist(self):
        for p in re.findall(r"<skill-dir>/([\w./-]+)", (SKILL / "SKILL.md").read_text()):
            if "<" not in p:
                self.assertTrue((SKILL / p.rstrip("/")).exists(), f"SKILL.md references <skill-dir>/{p}, which does not exist.")

    def test_codex_mirrors_point_to_claude_files(self):
        msg = "Codex must read the Claude files, not a copy (docs/adr/0001-claude-files-are-the-single-source.md)."
        self.assertEqual(os.readlink(ROOT / ".agents/skills"), "../.claude/skills", msg)
        self.assertEqual((ROOT / "CLAUDE.md").read_text().splitlines()[0], "@AGENTS.md", msg)
        for toml in (SKILL / "assets/agents/auditor.toml", ROOT / ".codex/agents/auditor.toml"):
            self.assertIn("Read `.claude/agents/auditor.md`", toml.read_text(), f"{toml}: {msg}")

    def test_installed_files_have_no_markers(self):
        for d in (".claude", ".codex"):
            for f in (ROOT / d).rglob("*"):
                if f.is_file():
                    self.assertNotIn("{{repo:", f.read_text(), f"{f.relative_to(ROOT)} has an unfilled marker; fill it from this repo's facts.")

    def test_auditor_model_pinned_to_opus(self):
        for f in (SKILL / "assets/agents/auditor.md", ROOT / ".claude/agents/auditor.md"):
            front = f.read_text().split("---")[1]
            self.assertIn("\nmodel: opus\n", front, f"{f}: pin `model: opus` so verification always runs on the strongest model.")

    def test_skill_md_lists_every_skill(self):
        text = (SKILL / "SKILL.md").read_text()
        description = text.split("---")[1]
        output = text.split("## Output")[1]
        for f in (SKILL / "assets/skills").glob("*.md"):
            for where, part in (("description", description), ("Output", output)):
                self.assertIn(f.stem, part, f"SKILL.md {where} does not name `{f.stem}`; Install, Output and description change together (AGENTS.md).")

    def test_dashboard_is_self_contained(self):
        f = SKILL / "assets/dashboard.html"
        self.assertTrue(f.exists(), "assets/dashboard.html is missing.")
        html = f.read_text()
        self.assertNotRegex(html, r"(src|href)=[\"']?https?:", "The dashboard must not load anything from the network; inline it.")
        self.assertNotIn("innerHTML", html, "Ticket text is untrusted; render it with textContent, never innerHTML.")

    def test_adapted_skills_keep_attribution(self):
        for f in (SKILL / "assets/skills").glob("*.md"):
            if f.stem in ORIGINAL_SKILLS:
                continue
            self.assertIn("MIT License, Copyright (c) 2026 Matt Pocock", f.read_text(), f"{f.relative_to(ROOT)} lost its MIT attribution comment.")

    def test_plugin_ships_one_skill(self):
        # Codex scans a plugin's skills/ recursively, so a template named SKILL.md would ship as a live skill.
        found = sorted(str(f.relative_to(ROOT)) for f in (ROOT / "skills").rglob("SKILL.md"))
        self.assertEqual(found, ["skills/agentic-engineering/SKILL.md"], "Templates under assets/skills/ are <name>.md, never SKILL.md.")

    def test_plugin_manifests_agree(self):
        name = re.search(r"^name: (.+)$", (SKILL / "SKILL.md").read_text(), re.M).group(1)
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        for f in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
            self.assertEqual([p["name"] for p in json.loads((ROOT / f).read_text())["plugins"]], [name], f)
        self.assertEqual((claude["name"], codex["name"]), (name, name), "Plugin names must match the skill name.")
        self.assertEqual(claude["version"], codex["version"], "Bump the Claude and Codex plugin versions together.")


if __name__ == "__main__":
    unittest.main()
