#!/usr/bin/env python3
"""scripts/update.py 骨架脚本的验收测试。"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
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


def run_check_brief(brief_path: Path | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if brief_path is not None:
        env['BRIEF_PATH'] = str(brief_path)
    return subprocess.run(
        ['node', str(CHECK_BRIEF)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=env,
    )


def write_temp_brief(content: str) -> Path:
    fd, name = tempfile.mkstemp(suffix='.md', prefix='brief-')
    os.close(fd)
    p = Path(name)
    p.write_text(content, encoding='utf-8')
    return p


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

    def test_brief_parse_accepts_valid_temp_input(self) -> None:
        # 显式覆盖「简报解析」分支：合法输入应通过校验。
        text = BRIEF.read_text(encoding="utf-8")
        tmp = write_temp_brief(text)
        try:
            result = run_check_brief(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("简报校验通过", result.stdout)
        finally:
            tmp.unlink(missing_ok=True)

    def test_brief_missing_section_rejected(self) -> None:
        text = BRIEF.read_text(encoding="utf-8")
        for section in BRIEF_SECTIONS:
            self.assertIn("## " + section, text)
        stripped = text.replace("## 世界模型", "## 其他")
        self.assertNotIn("## 世界模型", stripped)

    def test_brief_missing_section_fails_check(self) -> None:
        # 显式覆盖「缺失小节」分支：check-brief.js 必须非零退出并指出缺失小节名。
        text = BRIEF.read_text(encoding="utf-8")
        stripped = text.replace("## 世界模型", "## 其他")
        tmp = write_temp_brief(stripped)
        try:
            result = run_check_brief(tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("世界模型", result.stderr)
        finally:
            tmp.unlink(missing_ok=True)

    def test_brief_empty_or_placeholder_rejected(self) -> None:
        text = BRIEF.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"TODO|TBD|待补充|占位")
        for body in re.split(r"^## ", text, flags=re.M)[1:]:
            content = "\n".join(body.split("\n")[1:]).strip()
            self.assertNotEqual(content, "")

    def test_brief_empty_section_fails_check(self) -> None:
        # 显式覆盖「空内容」分支：构造空小节，check-brief.js 必须非零退出并指出小节名。
        text = BRIEF.read_text(encoding="utf-8")
        broken = text.replace("## 世界模型\n", "## 世界模型\n\n", 1)
        # 清空世界模型小节正文，直到下一个二级小节。
        broken = re.sub(r"(## 世界模型\n)(.*?)(?=\n## )", r"\1\n", broken, flags=re.S)
        tmp = write_temp_brief(broken)
        try:
            result = run_check_brief(tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("世界模型", result.stderr)
        finally:
            tmp.unlink(missing_ok=True)

    def test_brief_placeholder_fails_check(self) -> None:
        # 显式覆盖「占位符」分支：条目内出现 TODO 时校验失败。
        text = BRIEF.read_text(encoding="utf-8")
        broken = text.replace("- 一句话摘要：", "- 一句话摘要：TODO ", 1)
        tmp = write_temp_brief(broken)
        try:
            result = run_check_brief(tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("占位符", result.stderr)
        finally:
            tmp.unlink(missing_ok=True)

    def test_check_brief_script_passes(self) -> None:
        result = run_check_brief()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("简报校验通过", result.stdout)

    def test_update_idempotent_three_runs(self) -> None:
        # 显式覆盖「幂等」分支：连续三次运行退出码为 0 且输出完全一致。
        outputs = []
        for _ in range(3):
            result = run_script()
            self.assertEqual(result.returncode, 0, result.stderr)
            outputs.append(result.stdout)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1], outputs[2])


if __name__ == "__main__":
    unittest.main()
