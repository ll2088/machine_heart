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

    def test_archive_records_cover_three_new_articles(self) -> None:
        result = run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        records = [line for line in result.stdout.splitlines() if line.startswith("[ARCHIVE]")]
        self.assertEqual(len(records), 3)
        keys = [record.split("key=", 1)[1].split(" ", 1)[0] for record in records]
        self.assertEqual(
            keys,
            [
                "machine_heart:2651075493:1",
                "machine_heart:2651075493:2",
                "machine_heart:2651075493:3",
            ],
        )

    def test_archive_records_have_title_source_date(self) -> None:
        result = run_script()
        records = [line for line in result.stdout.splitlines() if line.startswith("[ARCHIVE]")]
        for record in records:
            self.assertIn("title=", record)
            self.assertIn("source=machine_heart", record)
            self.assertIn("date=2026-10-25", record)
        joined = "\n".join(records)
        self.assertIn("Sage S2.1 Flash", joined)
        self.assertIn("DeepMind", joined)
        self.assertIn("AI音乐", joined)

    def test_archive_records_idempotent(self) -> None:
        first = run_script()
        second = run_script()
        self.assertEqual(first.stdout, second.stdout)

    def test_archive_records_do_not_duplicate_keys(self) -> None:
        result = run_script()
        records = [line for line in result.stdout.splitlines() if line.startswith("[ARCHIVE]")]
        keys = [record.split("key=", 1)[1].split(" ", 1)[0] for record in records]
        self.assertEqual(len(keys), len(set(keys)))

    def test_archive_records_cover_three_new_articles_with_fields(self) -> None:
        """模拟三篇新文章输入，断言归档条目含标题、来源与日期字段。"""
        result = run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        records = [line for line in result.stdout.splitlines() if line.startswith("[ARCHIVE]")]
        self.assertEqual(len(records), 3)
        expected_titles = (
            "登顶全球第一：这支AI音乐团队，凭什么用18个月打败Suno？",
            "AGI还不是终点，DeepMind开始思考ASI的未来",
            "上海AI Lab开源Sage S2.1 Flash技术报告：四项智能体基准SOTA，科学多模态感知如何融入通用智能体？",
        )
        for record, title in zip(records, expected_titles):
            self.assertIn(f"title={title}", record)
            self.assertIn("source=machine_heart", record)
            self.assertIn("date=2026-10-25", record)

    def test_archive_records_absent_keeps_base_record_and_index(self) -> None:
        """缺少新文章时，基础更新记录保留，且不破坏已有批次索引。"""
        import importlib.util

        spec = importlib.util.spec_from_file_location("update_module", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        original = module.ARCHIVE_ENTRIES
        try:
            module.ARCHIVE_ENTRIES = ()
            self.assertEqual(module.build_archive_records(), [])
            self.assertTrue(module.build_record().startswith("[UPDATE]"))
        finally:
            module.ARCHIVE_ENTRIES = original
        # 已有批次索引不受影响：batch_index 仍登记 15 条。
        sys.path.insert(0, str(ROOT / "scripts"))
        import batch_index  # noqa: E402

        self.assertEqual(len(batch_index.known_keys()), 15)

    def test_missing_archive_entries_keeps_base_record(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("update_module", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        original = module.ARCHIVE_ENTRIES
        try:
            module.ARCHIVE_ENTRIES = ()
            self.assertEqual(module.build_archive_records(), [])
            self.assertTrue(module.build_record().startswith("[UPDATE]"))
        finally:
            module.ARCHIVE_ENTRIES = original


if __name__ == "__main__":
    unittest.main()
