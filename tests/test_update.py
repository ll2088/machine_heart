#!/usr/bin/env python3
"""scripts/update.py 骨架脚本的验收测试。"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "update.py"
CONFIG = ROOT / "config.json"
RECORD_PATTERN = re.compile(r"^\[UPDATE\]")


def run_script() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


def snapshot_workspace() -> dict:
    return {
        str(p.relative_to(ROOT)): p.stat().st_mtime_ns
        for p in ROOT.rglob("*")
        if p.is_file() and ".git" not in p.parts
    }


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
        self.assertIn("config.json", readme)
        self.assertIn("interval", readme)
        self.assertIn("source", readme)
        self.assertIn("退出码", roadmap)
        self.assertIn("## 阶段 1 完成标准", roadmap)

    def test_config_file_read(self) -> None:
        self.assertTrue(CONFIG.exists())
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        result = run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("source={0}".format(data["source"]), result.stdout)
        self.assertIn("interval={0}".format(data["interval"]), result.stdout)

    def test_config_change_reflected(self) -> None:
        original = CONFIG.read_text(encoding="utf-8")
        try:
            CONFIG.write_text(
                json.dumps({"interval": 42, "source": "custom_source"}),
                encoding="utf-8",
            )
            result = run_script()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("source=custom_source", result.stdout)
            self.assertIn("interval=42", result.stdout)
        finally:
            CONFIG.write_text(original, encoding="utf-8")

    def test_invalid_json_returns_error(self) -> None:
        original = CONFIG.read_text(encoding="utf-8")
        try:
            CONFIG.write_text("{not json", encoding="utf-8")
            result = run_script()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("[ERROR]", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
        finally:
            CONFIG.write_text(original, encoding="utf-8")

    def test_invalid_field_type_returns_error(self) -> None:
        original = CONFIG.read_text(encoding="utf-8")
        try:
            CONFIG.write_text(
                json.dumps({"interval": "soon", "source": "x"}),
                encoding="utf-8",
            )
            result = run_script()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("interval", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
        finally:
            CONFIG.write_text(original, encoding="utf-8")

    def test_no_file_writes(self) -> None:
        before = snapshot_workspace()
        result = run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        after = snapshot_workspace()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
