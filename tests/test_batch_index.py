#!/usr/bin/env python3
'''批次去重键的验收测试。'''

from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

import batch_index  # noqa: E402

EXPECTED = {
    'machine_heart:2651072640:1',
    'machine_heart:2651072640:2',
    'machine_heart:2651072640:3',
    'machine_heart:2651072404:1',
    'machine_heart:2651072404:2',
    'machine_heart:2651072404:3',
    'machine_heart:2651072888:1',
    'machine_heart:2651072888:2',
    'machine_heart:2651072888:3',
    'machine_heart:2651072774:1',
    'machine_heart:2651072774:2',
    'machine_heart:2651072774:3',
    'machine_heart:2651075493:1',
    'machine_heart:2651075493:2',
    'machine_heart:2651075493:3',
}


class BatchIndexTest(unittest.TestCase):
    def test_known_keys_cover_five_batches(self) -> None:
        keys = batch_index.known_keys()
        self.assertEqual(len(keys), 15)
        self.assertEqual(set(keys), EXPECTED)
        self.assertEqual(len(set(keys)), len(keys))

    def test_articles_unique_by_mid_idx(self) -> None:
        pairs = {(article.mid, article.idx) for article in batch_index.ARTICLES}
        self.assertEqual(len(pairs), 15)

    def test_new_batch_2651075493_indexed(self) -> None:
        articles = [
            article for article in batch_index.ARTICLES
            if article.mid == '2651075493'
        ]
        self.assertEqual(len(articles), 3)
        self.assertEqual([article.idx for article in articles], [1, 2, 3])
        self.assertEqual(
            [article.mainline for article in articles],
            ['产业与生态', '产业与生态', '前沿模型与架构'],
        )
        self.assertTrue(all(article.kind == '待核实' for article in articles))

    def test_new_batch_keys_are_unique(self) -> None:
        keys = [
            batch_index.dedup_key(article.mid, article.idx)
            for article in batch_index.ARTICLES
            if article.mid == '2651075493'
        ]
        self.assertEqual(len(keys), len(set(keys)))

    def test_known_keys_order_matches_batches_doc(self) -> None:
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        positions = [batches.index(key) for key in batch_index.known_keys()]
        self.assertEqual(positions, sorted(positions))

    def test_new_articles_have_kind(self) -> None:
        new_articles = [
            article for article in batch_index.ARTICLES
            if article.mid in {'2651072888', '2651072774'}
        ]
        self.assertEqual(len(new_articles), 6)
        self.assertEqual(sum(1 for article in new_articles if article.kind == '技术'), 4)
        self.assertEqual(sum(1 for article in new_articles if article.kind == '观点'), 2)

    def test_dedup_key_format(self) -> None:
        self.assertEqual(batch_index.dedup_key('2651072640', 1), 'machine_heart:2651072640:1')

    def test_dedup_key_rejects_invalid(self) -> None:
        with self.assertRaises(ValueError):
            batch_index.dedup_key('', 1)
        with self.assertRaises(ValueError):
            batch_index.dedup_key('2651072640', 0)
        with self.assertRaises(ValueError):
            batch_index.dedup_key('abc', 1)

    def test_validate_articles_accepts_current(self) -> None:
        batch_index.validate_articles(batch_index.ARTICLES)

    def test_validate_articles_rejects_duplicate(self) -> None:
        articles = (
            batch_index.Article('1', 1, '标题', '具身智能与机器人', 'https://mp.weixin.qq.com/x', '技术'),
            batch_index.Article('1', 1, '另一篇', '产业与生态', 'https://mp.weixin.qq.com/y', '观点'),
        )
        with self.assertRaises(ValueError):
            batch_index.validate_articles(articles)

    def test_validate_articles_rejects_unknown_mainline(self) -> None:
        articles = (batch_index.Article('1', 1, '标题', '未知主线', 'https://mp.weixin.qq.com/x', '技术'),)
        with self.assertRaises(ValueError):
            batch_index.validate_articles(articles)

    def test_validate_articles_rejects_unknown_kind(self) -> None:
        articles = (batch_index.Article('1', 1, '标题', '产业与生态', 'https://mp.weixin.qq.com/x', '八卦'),)
        with self.assertRaises(ValueError):
            batch_index.validate_articles(articles)

    def test_validate_articles_rejects_bad_url(self) -> None:
        articles = (batch_index.Article('1', 1, '标题', '产业与生态', 'ftp://example.com/x', '观点'),)
        with self.assertRaises(ValueError):
            batch_index.validate_articles(articles)

    def test_validate_articles_rejects_non_weixin_url(self) -> None:
        articles = (batch_index.Article('1', 1, '标题', '产业与生态', 'https://example.com/x', '观点'),)
        with self.assertRaises(ValueError):
            batch_index.validate_articles(articles)

    def test_validate_articles_accepts_empty(self) -> None:
        batch_index.validate_articles(())

    def test_validate_articles_rejects_non_sequence(self) -> None:
        with self.assertRaises(ValueError):
            batch_index.validate_articles('not-a-sequence')  # type: ignore[arg-type]

    def test_validate_articles_rejects_wrong_entry_type(self) -> None:
        with self.assertRaises(ValueError):
            batch_index.validate_articles(('not-an-article',))

    def test_validate_articles_rejects_invalid_mid(self) -> None:
        articles = (batch_index.Article('bad', 1, '标题', '产业与生态', 'https://mp.weixin.qq.com/x', '观点'),)
        with self.assertRaises(ValueError):
            batch_index.validate_articles(articles)

    def test_validate_articles_rejects_nonpositive_idx(self) -> None:
        articles = (batch_index.Article('1', 0, '标题', '产业与生态', 'https://mp.weixin.qq.com/x', '观点'),)
        with self.assertRaises(ValueError):
            batch_index.validate_articles(articles)

    def test_validate_articles_rejects_blank_title(self) -> None:
        articles = (batch_index.Article('1', 1, '   ', '产业与生态', 'https://mp.weixin.qq.com/x', '观点'),)
        with self.assertRaises(ValueError):
            batch_index.validate_articles(articles)

    def test_main_invalid_articles_prints_stderr_and_returns_2(self) -> None:
        original = batch_index.ARTICLES
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            batch_index.ARTICLES = (
                batch_index.Article('bad', 1, '标题', '产业与生态', 'https://mp.weixin.qq.com/x', '观点'),
            )
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = batch_index.main()
            self.assertEqual(code, 2)
            self.assertIn('[INVALID]', stderr.getvalue())
            self.assertEqual(stdout.getvalue(), '')
        finally:
            batch_index.ARTICLES = original

    def test_main_idempotent_output(self) -> None:
        buffer1 = io.StringIO()
        buffer2 = io.StringIO()
        with contextlib.redirect_stdout(buffer1):
            code = batch_index.main()
        with contextlib.redirect_stdout(buffer2):
            second = batch_index.main()
        self.assertEqual(code, 0)
        self.assertEqual(second, 0)
        self.assertEqual(buffer1.getvalue(), buffer2.getvalue())
        self.assertEqual(len(buffer1.getvalue().splitlines()), 15)

    def test_main_stdout_matches_known_keys(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = batch_index.main()
        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue().splitlines(), list(batch_index.known_keys()))

    def test_known_keys_stable_contract(self) -> None:
        self.assertEqual(batch_index.dedup_key('2651072888', 3), 'machine_heart:2651072888:3')

    def test_main_rejects_invalid_articles(self) -> None:
        original = batch_index.ARTICLES
        try:
            batch_index.ARTICLES = (batch_index.Article('bad', 0, '', '产业与生态', 'not-url', '观点'),)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                with contextlib.redirect_stderr(io.StringIO()):
                    code = batch_index.main()
            self.assertEqual(code, 2)
        finally:
            batch_index.ARTICLES = original

    def test_readme_contains_all_article_titles(self) -> None:
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for article in batch_index.ARTICLES:
            self.assertIn(article.title, readme)

    def test_readme_topic_count_is_25(self) -> None:
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        blocks = readme.split('### 选题 ')[1:]
        self.assertEqual(len(blocks), 25)

    def test_batches_contains_all_dedup_keys(self) -> None:
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        for key in batch_index.known_keys():
            self.assertIn(key, batches)

    def test_batches_hardcoded_key_count_matches_index(self) -> None:
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        section = batches.split('## 2. 去重键契约', 1)[1].split('## 3.', 1)[0]
        hardcoded = [
            line.strip().lstrip('- ').strip('`')
            for line in section.splitlines()
            if line.strip().startswith('- `machine_heart:')
        ]
        self.assertEqual(len(hardcoded), 15)
        self.assertEqual(hardcoded, list(batch_index.known_keys()))

    def test_batches_new_batch_keys_present(self) -> None:
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        for idx in (1, 2, 3):
            self.assertIn(f'machine_heart:2651075493:{idx}', batches)

    def test_new_batch_indexed_without_duplicates(self) -> None:
        """新增批次被正确索引，且重复运行不产生重复条目。"""
        keys = batch_index.known_keys()
        new_keys = [key for key in keys if key.startswith('machine_heart:2651075493:')]
        self.assertEqual(
            new_keys,
            [
                'machine_heart:2651075493:1',
                'machine_heart:2651075493:2',
                'machine_heart:2651075493:3',
            ],
        )
        self.assertEqual(len(keys), len(set(keys)))
        buffer1 = io.StringIO()
        buffer2 = io.StringIO()
        with contextlib.redirect_stdout(buffer1):
            first = batch_index.main()
        with contextlib.redirect_stdout(buffer2):
            second = batch_index.main()
        self.assertEqual(first, 0)
        self.assertEqual(second, 0)
        self.assertEqual(buffer1.getvalue(), buffer2.getvalue())

    def test_known_keys_order_matches_batches_section_two(self) -> None:
        """批次索引输出顺序与 docs/BATCHES.md 第 2 节硬编码清单顺序一致。"""
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        section = batches.split('## 2. 去重键契约', 1)[1].split('## 3.', 1)[0]
        hardcoded = [
            line.strip().lstrip('- ').strip('`')
            for line in section.splitlines()
            if line.strip().startswith('- `machine_heart:')
        ]
        self.assertEqual(hardcoded, list(batch_index.known_keys()))

    def test_batches_section_two_count_matches_index(self) -> None:
        """第 2 节硬编码去重键数量与 batch_index.py 登记条数一致（单一事实来源）。"""
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        section = batches.split('## 2. 去重键契约', 1)[1].split('## 3.', 1)[0]
        hardcoded = [
            line.strip().lstrip('- ').strip('`')
            for line in section.splitlines()
            if line.strip().startswith('- `machine_heart:')
        ]
        self.assertEqual(len(hardcoded), len(batch_index.known_keys()))
        self.assertEqual(len(hardcoded), 15)

    def test_batches_section_two_keys_equal_index_keys(self) -> None:
        """第 2 节硬编码去重键集合与 batch_index.py 的 known_keys() 完全相等（数量与内容）。"""
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        section = batches.split('## 2. 去重键契约', 1)[1].split('## 3.', 1)[0]
        hardcoded = [
            line.strip().lstrip('- ').strip('`')
            for line in section.splitlines()
            if line.strip().startswith('- `machine_heart:')
        ]
        self.assertEqual(set(hardcoded), set(batch_index.known_keys()))
        self.assertEqual(len(hardcoded), len(set(hardcoded)))

    def test_batches_no_stale_twelve_count(self) -> None:
        """BATCHES.md 中不应残留「12 个去重键」的旧计数表述。"""
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        self.assertNotIn('共 12 个', batches)
        self.assertNotIn('12 个键', batches)
        self.assertNotIn('12 个去重键', batches)

    def test_readme_topic_count_matches_batches_batch_count(self) -> None:
        """README 选题数与 BATCHES 去重键数保持可核对关系（选题数 >= 去重键数）。"""
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        blocks = readme.split('### 选题 ')[1:]
        self.assertGreaterEqual(len(blocks), len(batch_index.known_keys()))
        self.assertEqual(len(batch_index.known_keys()), 15)

    def test_check_brief_reads_expectations_from_sources(self) -> None:
        """check-brief.js 不再硬编码 22/12，期望值从 README 与 batch_index.py 动态读取。"""
        script = (ROOT / 'scripts' / 'check-brief.js').read_text(encoding='utf-8')
        self.assertNotIn('应为 22 条', script)
        self.assertNotIn('12 个', script)
        self.assertIn('countTopics', script)
        self.assertIn('countIndexedArticles', script)
        self.assertIn('extractBatchesSectionTwoKeys', script)

    def test_check_brief_reports_key_diffs(self) -> None:
        """check-brief.js 在数量不一致时输出具体缺失/多余的键名，便于定位漂移。"""
        script = (ROOT / 'scripts' / 'check-brief.js').read_text(encoding='utf-8')
        self.assertIn('missingInBatches', script)
        self.assertIn('extraInBatches', script)
        self.assertIn('BATCHES 第 2 节缺失的键', script)
        self.assertIn('BATCHES 第 2 节多余的键', script)

    def test_batches_section_two_parse_matches_index_exactly(self) -> None:
        """按 check-brief.js 的正则解析第 2 节，结果必须与 known_keys() 完全一致。"""
        import re

        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        section = batches.split('## 2. 去重键契约', 1)[1].split('## 3.', 1)[0]
        pattern = re.compile(r'^\s*-\s*`(machine_heart:[0-9]+:[0-9]+)`\s*$')
        parsed = [
            match.group(1)
            for line in section.splitlines()
            if (match := pattern.match(line)) is not None
        ]
        self.assertEqual(parsed, list(batch_index.known_keys()))
        self.assertEqual(len(parsed), 15)


    def test_validate_articles_rejects_non_string_fields(self) -> None:
        bad_entries = (
            batch_index.Article('1', 1, 123, '产业与生态', 'https://mp.weixin.qq.com/x', '观点'),
            batch_index.Article('1', 1, '标题', 123, 'https://mp.weixin.qq.com/x', '观点'),
            batch_index.Article('1', 1, '标题', '产业与生态', 123, '观点'),
            batch_index.Article('1', 1, '标题', '产业与生态', 'https://mp.weixin.qq.com/x', 123),
        )
        for article in bad_entries:
            with self.assertRaises(ValueError):
                batch_index.validate_articles((article,))

    def test_validate_articles_rejects_empty_mid(self) -> None:
        articles = (batch_index.Article('', 1, '标题', '产业与生态', 'https://mp.weixin.qq.com/x', '观点'),)
        with self.assertRaises(ValueError):
            batch_index.validate_articles(articles)

    def test_main_catches_validate_articles_value_error(self) -> None:
        original = batch_index.ARTICLES
        stderr = io.StringIO()
        try:
            batch_index.ARTICLES = ('not-an-article',)
            with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
                code = batch_index.main()
            self.assertEqual(code, 2)
            self.assertIn('[INVALID]', stderr.getvalue())
        finally:
            batch_index.ARTICLES = original


if __name__ == '__main__':
    unittest.main()
