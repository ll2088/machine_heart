#!/usr/bin/env python3
'''批次去重键的验收测试。'''

from __future__ import annotations

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
}


class BatchIndexTest(unittest.TestCase):
    def test_known_keys_cover_two_batches(self) -> None:
        keys = batch_index.known_keys()
        self.assertEqual(len(keys), 6)
        self.assertEqual(set(keys), EXPECTED)
        self.assertEqual(len(set(keys)), len(keys))

    def test_articles_unique_by_mid_idx(self) -> None:
        pairs = {(article.mid, article.idx) for article in batch_index.ARTICLES}
        self.assertEqual(len(pairs), 6)

    def test_dedup_key_format(self) -> None:
        self.assertEqual(batch_index.dedup_key('2651072640', 1), 'machine_heart:2651072640:1')

    def test_dedup_key_rejects_invalid(self) -> None:
        with self.assertRaises(ValueError):
            batch_index.dedup_key('', 1)
        with self.assertRaises(ValueError):
            batch_index.dedup_key('2651072640', 0)


if __name__ == '__main__':
    unittest.main()
