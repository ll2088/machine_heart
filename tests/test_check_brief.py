#!/usr/bin/env python3
"""校验 Node 简报脚本的退出码与幂等输出。"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
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
    def _write_fixture(self, tmp: Path, mutate: dict[str, str] | None = None) -> None:
        (tmp / 'docs').mkdir()
        (tmp / 'scripts').mkdir()
        shutil.copy2(ROOT / 'README.md', tmp / 'README.md')
        shutil.copy2(ROOT / 'docs' / 'ROADMAP.md', tmp / 'docs' / 'ROADMAP.md')
        shutil.copy2(ROOT / 'docs' / 'BATCHES.md', tmp / 'docs' / 'BATCHES.md')
        shutil.copy2(ROOT / 'scripts' / 'batch_index.py', tmp / 'scripts' / 'batch_index.py')
        shutil.copy2(ROOT / 'package.json', tmp / 'package.json')
        for rel, content in (mutate or {}).items():
            (tmp / rel).write_text(content, encoding='utf-8')

    def _run_node_with_root(self, root: Path) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env['MACHINE_HEART_ROOT'] = str(root)
        return subprocess.run(
            ['node', str(SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            env=env,
        )

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

    def test_package_dependency_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            pkg = (root / 'package.json').read_text(encoding='utf-8')
            pkg = pkg.replace('"private": true,', '"private": true,\n  "dependencies": {"left-pad": "1.0.0"},')
            (root / 'package.json').write_text(pkg, encoding='utf-8')
            result = self._run_node_with_root(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('package.json 引入了第三方依赖', result.stderr)

    def test_batch_index_out_of_sync_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            (root / 'scripts' / 'batch_index.py').write_text(
                'SOURCE = "machine_heart"\nARTICLES = ()\n',
                encoding='utf-8',
            )
            result = self._run_node_with_root(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('batch_index.py 登记条数与 BATCHES 硬编码不一致', result.stderr)

    def test_batches_missing_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            batches = (root / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
            batches = batches.replace('machine_heart:2651072888:1', 'machine_heart:2651072888:9')
            (root / 'docs' / 'BATCHES.md').write_text(batches, encoding='utf-8')
            result = self._run_node_with_root(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('docs/BATCHES.md 缺少去重键', result.stderr)


if __name__ == '__main__':
    unittest.main()
