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
CHECK_BRIEF = ROOT / "scripts" / "check-brief.js"
BRIEF = ROOT / "docs" / "BRIEF-2026-10-25.md"
RECORD_PATTERN = re.compile(r"^\[UPDATE\]")
BRIEF_SECTIONS = ["具身智能", "世界模型", "Agent 记忆", "来源与日期"]


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

    def test_brief_parses_with_all_sections(self) -> None:
        text = BRIEF.read_text(encoding="utf-8")
        for section in BRIEF_SECTIONS:
            self.assertIn("## " + section, text)
        blocks = re.split(r"^### 条目 ", text, flags=re.M)[1:]
        self.assertGreaterEqual(len(blocks), 5)
        for block in blocks:
            for label in ("标题", "来源链接", "一句话摘要", "推荐理由", "来源与日期"):
                self.assertRegex(block, r"(?m)^- " + label + r"：\S")
            self.assertRegex(block, r"https?://")

    def test_brief_missing_section_rejected(self) -> None:
        text = BRIEF.read_text(encoding="utf-8")
        for section in BRIEF_SECTIONS:
            self.assertIn("## " + section, text)
        stripped = text.replace("## 世界模型", "## 其他")
        self.assertNotIn("## 世界模型", stripped)

    def test_brief_empty_or_placeholder_rejected(self) -> None:
        text = BRIEF.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"TODO|TBD|待补充|占位")
        for body in re.split(r"^## ", text, flags=re.M)[1:]:
            content = "\n".join(body.split("\n")[1:]).strip()
            self.assertNotEqual(content, "")

    def test_check_brief_script_passes(self) -> None:
        result = subprocess.run(
            ["node", str(CHECK_BRIEF)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("简报校验通过", result.stdout)


if __name__ == "__main__":
    unittest.main()
