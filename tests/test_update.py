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

    def test_archive_records_include_titles_and_date(self) -> None:
        records = archive.build_archive_records()
        self.assertEqual(len(records), 3)
        joined = "\n".join(records)
        self.assertIn("Personal Agent", joined)
        self.assertIn("百度开源全新预训练基模", joined)
        self.assertIn("多模态", joined)
        for record in records:
            self.assertIn("date=" + archive.ARCHIVE_DATE, record)

    def test_validate_missing_field_returns_nonzero(self) -> None:
        broken = [dict(archive.ARTICLES[0])]
        broken[0].pop("category")
        errors = archive.validate_articles(broken)
        self.assertTrue(any("category" in e for e in errors))
        result = subprocess.run(
            [sys.executable, str(ARCHIVE_SCRIPT), "--validate"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_bad_url_returns_nonzero(self) -> None:
        broken = [dict(archive.ARTICLES[0])]
        broken[0]["url"] = "ftp://example.com/a"
        errors = archive.validate_articles(broken)
        self.assertTrue(any("链接格式错误" in e for e in errors))

    def test_archive_records_no_duplicates(self) -> None:
        records = archive.build_archive_records()
        self.assertEqual(len(records), len(set(records)))
        self.assertEqual(records, archive.build_archive_records())

    def test_check_brief_script_passes(self) -> None:
        script = ROOT / "scripts" / "check-brief.js"
        if not script.exists():
            self.skipTest("check-brief.js 不存在")
        result = subprocess.run(
            ["node", str(script)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_docs_structure_keywords(self) -> None:
        """文档结构检查：README 含三篇关键词，ROADMAP 含 2025 日期口径。"""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("Personal Agent", readme)
        self.assertIn("百度Flash", readme)
        self.assertIn("多模态", readme)
        self.assertIn("2025", roadmap)

    def test_update_twice_no_duplicate_archive(self) -> None:
        """连续运行两次，归档条目数不变且无重复。"""
        first = run_script()
        second = run_script()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        first_records = [l for l in first.stdout.splitlines() if ARCHIVE_PATTERN.match(l)]
        second_records = [l for l in second.stdout.splitlines() if ARCHIVE_PATTERN.match(l)]
        self.assertEqual(len(first_records), len(second_records))
        self.assertEqual(len(second_records), len(set(second_records)))

    def test_check_brief_missing_field_returns_nonzero(self) -> None:
        """check-brief.js 对缺失必填字段的简报返回非零退出码。"""
        script = ROOT / "scripts" / "check-brief.js"
        if not script.exists():
            self.skipTest("check-brief.js 不存在")
        import tempfile
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "scripts").mkdir()
            (tmp_root / "docs").mkdir()
            shutil.copy(str(script), str(tmp_root / "scripts" / "check-brief.js"))
            broken_readme = (
                "# t\n\n## 选题简报\n\n### 选题 1：x\n\n"
                "- 标题：x\n- 来源链接：https://example.com/a\n"
                "- 一句话摘要：x\n"
            )
            (tmp_root / "README.md").write_text(broken_readme, encoding="utf-8")
            (tmp_root / "docs" / "ROADMAP.md").write_text(
                "## 专题跟踪清单\n\n| 专题名称 |\n| --- |\n", encoding="utf-8"
            )
            result = subprocess.run(
                ["node", str(tmp_root / "scripts" / "check-brief.js")],
                capture_output=True,
                text=True,
                cwd=str(tmp_root),
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
