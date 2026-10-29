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


def build_record() -> str:
    """构造一条可被下游解析的更新记录。"""
    return "[UPDATE] ts={ts} source=machine_heart status=ok".format(
        ts=FIXED_TIMESTAMP
    )


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    dry_run = "--dry-run" in args
    record = build_record()
    if dry_run:
        print("[DRY-RUN] " + record)
    else:
        print(record)
    return 0


if __name__ == "__main__":
    sys.exit(main())
