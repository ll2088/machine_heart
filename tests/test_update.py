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

    def test_readme_has_usage_section(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## 使用说明", readme)
        section = readme.split("## 使用说明")[1].split("## ")[0]
        self.assertGreater(len(section.strip()), 0)

    def test_batches_doc_has_batch_index_section(self) -> None:
        batches = (ROOT / "docs" / "BATCHES.md").read_text(encoding="utf-8")
        self.assertIn("## 批次索引", batches)
        section = batches.split("## 批次索引")[1].split("## ")[0]
        self.assertGreater(len(section.strip()), 0)

    def test_update_script_archives_articles_without_duplicates(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import batch_index  # noqa: E402

        keys = batch_index.known_keys()
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), 18)
        for article in batch_index.NEW_ARTICLES:
            self.assertIn(batch_index.dedup_key(article.mid, article.idx), keys)
        for article in batch_index.LATEST_ARTICLES:
            self.assertIn(batch_index.dedup_key(article.mid, article.idx), keys)

    def test_repeated_runs_do_not_duplicate_archive_entries(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import batch_index  # noqa: E402

        first = batch_index.known_keys()
        second = batch_index.known_keys()
        self.assertEqual(first, second)
        self.assertEqual(len(first), len(set(first)))

    def test_update_script_archives_latest_articles(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import batch_index  # noqa: E402

        keys = batch_index.known_keys()
        for article in batch_index.LATEST_ARTICLES:
            self.assertIn(batch_index.dedup_key(article.mid, article.idx), keys)
        self.assertEqual(len(keys), len(batch_index.ARCHIVED_ARTICLES))

    def test_repeated_runs_keep_archive_count_stable(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import batch_index  # noqa: E402

        counts = {len(batch_index.known_keys()) for _ in range(3)}
        self.assertEqual(counts, {len(batch_index.ARCHIVED_ARTICLES)})

    def test_batches_doc_has_required_sections(self) -> None:
        batches = (ROOT / "docs" / "BATCHES.md").read_text(encoding="utf-8")
        self.assertIn("## 批次索引", batches)
        section = batches.split("## 批次索引")[1].split("## ")[0]
        self.assertGreater(len(section.strip()), 0)

    def test_roadmap_has_roadmap_section(self) -> None:
        roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("## 路线图", roadmap)
        section = roadmap.split("## 路线图")[1].split("## ")[0]
        self.assertGreater(len(section.strip()), 0)


if __name__ == "__main__":
    unittest.main()
