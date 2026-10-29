#!/usr/bin/env python3
"""scripts/update.py 骨架脚本的验收测试。"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "update.py"
RECORD_PATTERN = re.compile(r"^\[UPDATE\]")


def run_script() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


class UpdateScriptTest(unittest.TestCase):
    def test_exit_code_zero(self) -> None:
        result = run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_output_has_update_record(self) -> None:
        result = run_script()
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        records = [line for line in lines if RECORD_PATTERN.match(line)]
        self.assertGreaterEqual(len(records), 1)

    def test_idempotent_output(self) -> None:
        first = run_script()
        second = run_script()
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.returncode, second.returncode)

    def test_docs_structure(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("scripts/update.py", readme)
        self.assertIn("## 脚本运行方式", readme)
        self.assertIn("退出码", roadmap)
        self.assertIn("## 阶段 1 完成标准", roadmap)

    def test_brief_has_date_links_and_entries(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## 简报落地", readme)
        brief = readme.split("## 简报落地")[1].split("\n## ")[0]
        self.assertRegex(brief, r"\d{4}-\d{2}-\d{2}")
        self.assertIn("https://", brief)
        rows = [line for line in brief.splitlines() if re.match(r"^\|\s*\d+\s*\|", line)]
        self.assertGreaterEqual(len(rows), 3)

    def test_check_brief_rejects_missing_section(self) -> None:
        import tempfile
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "scripts").mkdir()
            shutil.copy(ROOT / "scripts" / "check-brief.js", root / "scripts" / "check-brief.js")
            (root / "README.md").write_text("# 无小节\n", encoding="utf-8")
            (root / "docs" / "ROADMAP.md").write_text("# 无清单\n", encoding="utf-8")
            result = subprocess.run(
                ["node", str(root / "scripts" / "check-brief.js")],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_dry_run_no_file_writes(self) -> None:
        before = {p: p.stat().st_mtime for p in ROOT.rglob("*") if p.is_file()}
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[DRY-RUN]", result.stdout)
        after = {p: p.stat().st_mtime for p in ROOT.rglob("*") if p.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
