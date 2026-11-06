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
ARCHIVE_SCRIPT = ROOT / "scripts" / "archive.py"
RECORD_PATTERN = re.compile(r"^\[UPDATE\]")
ARCHIVE_PATTERN = re.compile(r"^\[ARCHIVE\]")

sys.path.insert(0, str(ROOT / "scripts"))
import archive  # noqa: E402


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

    def test_archive_records_contain_three_articles(self) -> None:
        result = run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        records = [l for l in result.stdout.splitlines() if ARCHIVE_PATTERN.match(l)]
        self.assertEqual(len(records), 3)
        joined = "\n".join(records)
        self.assertIn("Personal Agent", joined)
        self.assertIn("百度开源全新预训练基模", joined)
        self.assertIn("多模态", joined)
        self.assertIn("date=2026-10-25", joined)

    def test_archive_idempotent_no_duplicates(self) -> None:
        first = run_script()
        second = run_script()
        self.assertEqual(first.stdout, second.stdout)
        records = [l for l in second.stdout.splitlines() if ARCHIVE_PATTERN.match(l)]
        self.assertEqual(len(records), len(set(records)))

    def test_validate_ok(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ARCHIVE_SCRIPT), "--validate"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_missing_field_fails(self) -> None:
        broken = [dict(archive.ARTICLES[0])]
        broken[0].pop("summary")
        errors = archive.validate_articles(broken)
        self.assertTrue(errors)
        self.assertTrue(any("summary" in e for e in errors))

    def test_validate_bad_url_fails(self) -> None:
        broken = [dict(archive.ARTICLES[0])]
        broken[0]["url"] = "not-a-url"
        errors = archive.validate_articles(broken)
        self.assertTrue(any("链接格式错误" in e for e in errors))

    def test_validate_empty_fails(self) -> None:
        self.assertTrue(archive.validate_articles([]))


if __name__ == "__main__":
    unittest.main()
