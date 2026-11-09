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

    def test_three_articles_archived_with_tags(self) -> None:
        result = run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        for tag in ('物理验证', '云电脑智能体', '触觉推理'):
            self.assertIn('tag=' + tag, result.stdout)
        self.assertEqual(result.stdout.count('[ARCHIVE]'), 3)

    def test_archive_idempotent(self) -> None:
        first = run_script()
        second = run_script()
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stdout.count('[ARCHIVE]'), 3)

    def test_batch_index_contains_batch(self) -> None:
        sys.path.insert(0, str(ROOT / 'scripts'))
        try:
            import batch_index
        finally:
            sys.path.pop(0)
        keys = batch_index.known_keys()
        for idx in (1, 2, 3):
            self.assertIn('machine_heart:2651073140:' + str(idx), keys)

    def test_docs_structure(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("scripts/update.py", readme)
        self.assertIn("## 脚本运行方式", readme)
        self.assertIn("退出码", roadmap)
        self.assertIn("## 阶段 1 完成标准", roadmap)


if __name__ == "__main__":
    unittest.main()
