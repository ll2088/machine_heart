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
}


class BatchIndexTest(unittest.TestCase):
    def test_known_keys_cover_four_batches(self) -> None:
        keys = batch_index.known_keys()
        self.assertEqual(len(keys), 12)
        self.assertEqual(set(keys), EXPECTED)
        self.assertEqual(len(set(keys)), len(keys))

    def test_new_articles_are_archived(self) -> None:
        self.assertEqual(len(batch_index.NEW_ARTICLES), 6)
        self.assertEqual(len(batch_index.ARCHIVED_ARTICLES), 12)
        for article in batch_index.NEW_ARTICLES:
            self.assertIn(article, batch_index.ARCHIVED_ARTICLES)

    def test_new_articles_classification(self) -> None:
        by_mainline = {}
        for article in batch_index.NEW_ARTICLES:
            by_mainline.setdefault(article.mainline, []).append(article)
        self.assertEqual(len(by_mainline['具身智能与机器人']), 2)
        self.assertEqual(len(by_mainline['前沿模型与架构']), 2)
        self.assertEqual(len(by_mainline['产业与生态']), 2)
        self.assertEqual(sum(1 for a in batch_index.NEW_ARTICLES if a.kind == '技术'), 4)
        self.assertEqual(sum(1 for a in batch_index.NEW_ARTICLES if a.kind == '观点'), 2)

    def test_new_articles_have_valid_urls(self) -> None:
        for article in batch_index.NEW_ARTICLES:
            self.assertTrue(article.url.startswith('https://'))
            self.assertIn('mp.weixin.qq.com', article.url)
            self.assertIn('mid=' + article.mid, article.url)
            self.assertIn('idx=' + str(article.idx), article.url)

    def test_batches_doc_has_batch_index_section(self) -> None:
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        self.assertIn('## 3. 批次索引', batches)
        self.assertIn('### 3.1 已知批次与文章清单', batches)
        self.assertIn('### 3.2 本轮新增批次', batches)

    def test_batches_doc_lists_new_keys_with_mainline_and_kind(self) -> None:
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        for article in batch_index.NEW_ARTICLES:
            key = batch_index.dedup_key(article.mid, article.idx)
            self.assertIn(key, batches)
            self.assertIn(article.mainline, batches)
            self.assertIn(article.kind, batches)

    def test_articles_unique_by_mid_idx(self) -> None:
        pairs = {(article.mid, article.idx) for article in batch_index.ARTICLES}
        self.assertEqual(len(pairs), 12)

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
        self.assertEqual(len(buffer1.getvalue().splitlines()), 12)

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

    def test_readme_topic_count_is_22(self) -> None:
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        blocks = readme.split('### 选题 ')[1:]
        self.assertEqual(len(blocks), 22)

    def test_batches_contains_all_dedup_keys(self) -> None:
        batches = (ROOT / 'docs' / 'BATCHES.md').read_text(encoding='utf-8')
        for key in batch_index.known_keys():
            self.assertIn(key, batches)


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
