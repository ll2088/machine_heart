#!/usr/bin/env python3
"""校验 Node 简报脚本的退出码与幂等输出。"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'scripts' / 'check-brief.js'


def run_node() -> subprocess.CompletedProcess:
    return subprocess.run(
        ['node', str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


class CheckBriefTest(unittest.TestCase):
    def test_exit_code_zero(self) -> None:
        result = run_node()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('简报校验通过', result.stdout)

    def test_idempotent_output(self) -> None:
        first = run_node()
        second = run_node()
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.returncode, second.returncode)

    def test_no_traceback(self) -> None:
        result = run_node()
        self.assertNotIn('Traceback', result.stdout)
        self.assertNotIn('TypeError', result.stderr)


if __name__ == '__main__':
    unittest.main()
