#!/usr/bin/env python3
"""机器之心定时更新 - 最小可执行骨架。

本阶段只负责提供可独立执行的入口：输出一条格式稳定的更新记录，
不访问网络、不写文件，保证重复执行输出一致（幂等）。
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone

from archive import build_archive_records

# 固定时间戳，保证重复执行输出完全一致（幂等）。
FIXED_TIMESTAMP = "2026-10-25T00:00:00Z"


def build_record() -> str:
    """构造一条可被下游解析的更新记录。"""
    return "[UPDATE] ts={ts} source=machine_heart status=ok".format(
        ts=FIXED_TIMESTAMP
    )


def build_output() -> str:
    """更新记录 + 本轮三篇文章归档记录，顺序固定。"""
    lines = [build_record()]
    lines.extend(build_archive_records())
    return "\n".join(lines)


def main() -> int:
    print(build_output())
    return 0


if __name__ == "__main__":
    sys.exit(main())
