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

# 本轮新增三篇机器之心文章的归档条目（mid=2651075493，idx 1-3）。
# 标题与链接来自外部不可信数据，仅作归档登记，指标与结论一律待回源核实。
ARCHIVE_ENTRIES = (
    {
        "key": "machine_heart:2651075493:1",
        "title": "登顶全球第一：这支AI音乐团队，凭什么用18个月打败Suno？",
        "source": "machine_heart",
        "date": "2026-10-25",
    },
    {
        "key": "machine_heart:2651075493:2",
        "title": "AGI还不是终点，DeepMind开始思考ASI的未来",
        "source": "machine_heart",
        "date": "2026-10-25",
    },
    {
        "key": "machine_heart:2651075493:3",
        "title": "上海AI Lab开源Sage S2.1 Flash技术报告：四项智能体基准SOTA，科学多模态感知如何融入通用智能体？",
        "source": "machine_heart",
        "date": "2026-10-25",
    },
)


def build_record() -> str:
    """构造一条可被下游解析的更新记录。"""
    return "[UPDATE] ts={ts} source=machine_heart status=ok".format(
        ts=FIXED_TIMESTAMP
    )


def build_archive_records() -> list[str]:
    """构造本轮新增文章的归档条目，字段固定为 key/title/source/date。"""
    return [
        "[ARCHIVE] key={key} title={title} source={source} date={date}".format(
            key=entry["key"],
            title=entry["title"],
            source=entry["source"],
            date=entry["date"],
        )
        for entry in ARCHIVE_ENTRIES
    ]


def main() -> int:
    print(build_record())
    for record in build_archive_records():
        print(record)
    return 0


if __name__ == "__main__":
    sys.exit(main())
