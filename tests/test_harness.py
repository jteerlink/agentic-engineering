import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# ponytail: deliberately absent paths; GLOSSARY.md is created lazily, .scratch/ is gitignored
ABSENT_OK = {"GLOSSARY.md", ".scratch", "docs/features", "validate_harness.py"}


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
                if p not in ABSENT_OK:
                    self.assertTrue((ROOT / p).exists(), f"{doc} names `{p}`, which does not exist. Fix the path or the doc.")

    def test_skill_md_assets_exist(self):
        for p in re.findall(r"<skill-dir>/([\w./-]+)", (ROOT / "SKILL.md").read_text()):
            if "<" not in p:
                self.assertTrue((ROOT / p.rstrip("/")).exists(), f"SKILL.md references <skill-dir>/{p}, which does not exist.")

    def test_codex_mirrors_point_to_claude_files(self):
        msg = "Codex must read the Claude files, not a copy (docs/adr/0001-claude-files-are-the-single-source.md)."
        self.assertEqual(os.readlink(ROOT / ".agents/skills"), "../.claude/skills", msg)
        self.assertEqual((ROOT / "CLAUDE.md").read_text().splitlines()[0], "@AGENTS.md", msg)
        for toml in ("assets/agents/harness-verifier.toml", ".codex/agents/harness-verifier.toml"):
            self.assertIn("Read `.claude/agents/harness-verifier.md`", (ROOT / toml).read_text(), f"{toml}: {msg}")

    def test_installed_files_have_no_markers(self):
        for d in (".claude", ".codex"):
            for f in (ROOT / d).rglob("*"):
                if f.is_file():
                    self.assertNotIn("{{repo:", f.read_text(), f"{f.relative_to(ROOT)} has an unfilled marker; fill it from this repo's facts.")

    def test_verifier_model_pinned_to_opus(self):
        for f in ("assets/agents/harness-verifier.md", ".claude/agents/harness-verifier.md"):
            front = (ROOT / f).read_text().split("---")[1]
            self.assertIn("\nmodel: opus\n", front, f"{f}: pin `model: opus` so the Router never downgrades verification.")

    def test_adapted_skills_keep_attribution(self):
        for f in (ROOT / "assets/skills").glob("*/SKILL.md"):
            self.assertIn("MIT License, Copyright (c) 2026 Matt Pocock", f.read_text(), f"{f.relative_to(ROOT)} lost its MIT attribution comment.")


if __name__ == "__main__":
    unittest.main()
