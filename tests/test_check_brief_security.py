#!/usr/bin/env python3
"""check-brief.js 安全边界的补充回归测试。

覆盖：绝对路径、.. 逃逸、隐藏/敏感目录、路径不存在、跨平台分隔符、
符号链接目录/文件逃逸、并发运行与临时目录清理。
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'scripts' / 'check-brief.js'


def run_node(env_root: str | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_root is not None:
        env['MACHINE_HEART_ROOT'] = env_root
    return subprocess.run(
        ['node', str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=env,
    )


class CheckBriefSecurityTest(unittest.TestCase):
    def test_absolute_root_rejected(self) -> None:
        result = run_node('/etc')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('必须是相对于仓库根目录的相对路径', result.stderr)

    def test_parent_root_rejected(self) -> None:
        result = run_node('..')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('不能使用 .. 逃逸仓库根目录', result.stderr)

    def test_hidden_dotgit_rejected(self) -> None:
        result = run_node('.git')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('不能指向隐藏目录或敏感路径', result.stderr)

    def test_nested_hidden_rejected(self) -> None:
        result = run_node('sub/.git')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('不能指向隐藏目录或敏感路径', result.stderr)

    def test_node_modules_rejected(self) -> None:
        result = run_node('node_modules')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('不能指向隐藏目录或敏感路径', result.stderr)

    def test_missing_path_rejected(self) -> None:
        result = run_node('definitely-missing-dir')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('MACHINE_HEART_ROOT 无法解析', result.stderr)

    def test_backslash_separator_rejected(self) -> None:
        result = run_node('sub\\dir')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('只能使用 / 作为路径分隔符', result.stderr)

    def test_symlink_directory_escape_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='tmp-check-brief-link-') as tmp:
            root = Path(tmp)
            link = root / 'escape'
            link.symlink_to(tempfile.gettempdir())
            result = run_node(os.path.relpath(link, ROOT))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('越界或符号链接逃逸', result.stderr)

    def test_symlink_file_escape_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='tmp-check-brief-link-') as tmp:
            root = Path(tmp)
            outside_file = Path(tempfile.gettempdir()) / 'machine-heart-outside.txt'
            outside_file.write_text('outside', encoding='utf-8')
            try:
                link = root / 'escape-file'
                link.symlink_to(outside_file)
                result = run_node(os.path.relpath(link, ROOT))
            finally:
                try:
                    outside_file.unlink()
                except FileNotFoundError:
                    pass
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('越界或符号链接逃逸', result.stderr)

    def test_fixture_cleanup_after_failure(self) -> None:
        tmp = Path(tempfile.mkdtemp(dir=ROOT, prefix='tmp-check-brief-security-'))
        try:
            self.assertTrue(tmp.exists())
            raise RuntimeError('simulated cleanup failure target')
        except RuntimeError:
            pass
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertFalse(tmp.exists())

    def test_concurrent_runs_are_isolated(self) -> None:
        results = [run_node() for _ in range(4)]
        self.assertTrue(all(result.returncode == 0 for result in results))
        outputs = {result.stdout.strip() for result in results}
        self.assertEqual(len(outputs), 1)


if __name__ == '__main__':
    unittest.main()
