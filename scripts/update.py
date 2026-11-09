#!/usr/bin/env python3
"""机器之心定时更新 - 最小可执行骨架。

本阶段只负责提供可独立执行的入口：输出一条格式稳定的更新记录，
不访问网络、不写文件，保证重复执行输出一致（幂等）。
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone

# 固定时间戳，保证重复执行输出完全一致（幂等）。
FIXED_TIMESTAMP = "2026-10-25T00:00:00Z"


BATCH_MID = "2651073140"

ARCHIVED_ARTICLES = (
    ("2651073140", 1, "AI Scientists「终极大考」，全球首个真实湿实验的Physical AI Verifier来了", "物理验证"),
    ("2651073140", 2, "你的AI同事，已经开始用「云电脑」上班了", "云电脑智能体"),
    ("2651073140", 3, "让AI「摸懂」物理世界，首个触觉推理模型Touch-R1，入选NeurIPS 2026", "触觉推理"),
)


def build_record() -> str:
    """构造一条可被下游解析的更新记录。"""
    return "[UPDATE] ts={ts} source=machine_heart status=ok".format(
        ts=FIXED_TIMESTAMP
    )


def build_archive_lines() -> list[str]:
    """按固定顺序输出本轮三篇文章的归档行，保证幂等。"""
    return [
        "[ARCHIVE] key=machine_heart:{mid}:{idx} tag={tag} title={title}".format(
            mid=mid, idx=idx, tag=tag, title=title
        )
        for mid, idx, title, tag in ARCHIVED_ARTICLES
    ]


def main() -> int:
    record = build_record()
    print(record)
    for line in build_archive_lines():
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
