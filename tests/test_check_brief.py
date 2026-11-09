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
        shutil.copy2(ROOT / 'docs' / 'VERIFICATION.md', tmp / 'docs' / 'VERIFICATION.md')
        shutil.copy2(ROOT / 'scripts' / 'batch_index.py', tmp / 'scripts' / 'batch_index.py')
        shutil.copy2(ROOT / 'package.json', tmp / 'package.json')
        for rel, content in (mutate or {}).items():
            (tmp / rel).write_text(content, encoding='utf-8')

    def _run_node_with_root(self, root: Path) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        rel = os.path.relpath(root, ROOT)
        env['MACHINE_HEART_ROOT'] = rel
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
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='tmp-check-brief-') as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            pkg = (root / 'package.json').read_text(encoding='utf-8')
            pkg = pkg.replace('"private": true,', '"private": true,\n  "dependencies": {"left-pad": "1.0.0"},')
            (root / 'package.json').write_text(pkg, encoding='utf-8')
            result = self._run_node_with_root(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('package.json 引入了第三方依赖', result.stderr)

    def test_batch_index_out_of_sync_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='tmp-check-brief-') as tmp:
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
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='tmp-check-brief-') as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            batches = (root / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
            batches = batches.replace('machine_heart:2651072888:1', 'machine_heart:2651072888:9')
            (root / 'docs' / 'BATCHES.md').write_text(batches, encoding='utf-8')
            result = self._run_node_with_root(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('docs/BATCHES.md 缺少去重键', result.stderr)

    def test_absolute_root_rejected(self) -> None:
        env = os.environ.copy()
        env['MACHINE_HEART_ROOT'] = '/etc'
        result = subprocess.run(
            ['node', str(SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            env=env,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('必须是相对于仓库根目录的相对路径', result.stderr)

    def test_parent_root_rejected(self) -> None:
        env = os.environ.copy()
        env['MACHINE_HEART_ROOT'] = '..'
        result = subprocess.run(
            ['node', str(SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            env=env,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('不能使用 .. 逃逸仓库根目录', result.stderr)

    def test_hidden_root_rejected(self) -> None:
        env = os.environ.copy()
        env['MACHINE_HEART_ROOT'] = '.git'
        result = subprocess.run(
            ['node', str(SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            env=env,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('不能指向隐藏目录或敏感路径', result.stderr)


    def test_verification_missing_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='tmp-check-brief-') as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            (root / 'docs' / 'VERIFICATION.md').unlink()
            result = self._run_node_with_root(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('docs/VERIFICATION.md 缺少关键验收内容', result.stderr)

    def test_verification_missing_key_snippet_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='tmp-check-brief-') as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            verification = (root / 'docs' / 'VERIFICATION.md').read_text(encoding='utf-8')
            verification = verification.replace('不做性能结论', '性能结论待定')
            (root / 'docs' / 'VERIFICATION.md').write_text(verification, encoding='utf-8')
            result = self._run_node_with_root(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('docs/VERIFICATION.md 缺少关键验收内容: 不做性能结论', result.stderr)

    def test_new_batch_articles_pass(self) -> None:
        result = run_node()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('简报校验通过', result.stdout)

    def test_missing_topic_tag_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='tmp-check-brief-') as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            batches = (root / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
            batches = batches.replace('| 物理验证 |', '| 待定 |')
            (root / 'docs' / 'BATCHES.md').write_text(batches, encoding='utf-8')
            result = self._run_node_with_root(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('缺少主题标签', result.stderr)

    def test_batch_index_invalid_article_format_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='tmp-check-brief-') as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            (root / 'scripts' / 'batch_index.py').write_text(
                'SOURCE = "machine_heart"\nARTICLES = (Article("bad", 0, "标题", "产业与生态", "https://mp.weixin.qq.com/x", "观点"),)\n',
                encoding='utf-8',
            )
            result = self._run_node_with_root(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('batch_index.py 登记条数与 BATCHES 硬编码不一致', result.stderr)


if __name__ == '__main__':
    unittest.main()
