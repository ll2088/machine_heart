#!/usr/bin/env python3
"""机器之心定时更新 - 最小可执行骨架。

本阶段只负责提供可独立执行的入口：输出一条格式稳定的更新记录，
不访问网络、不写文件，保证重复执行输出一致（幂等）。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# 固定时间戳，保证重复执行输出完全一致（幂等）。
FIXED_TIMESTAMP = "2026-10-25T00:00:00Z"

# 配置文件路径与文档声明的默认值。
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
DEFAULT_INTERVAL = 3600
DEFAULT_SOURCE = "machine_heart"


class ConfigError(Exception):
    """配置文件缺失或非法时抛出的可读错误。"""


def load_config(path: Path = CONFIG_PATH) -> dict:
    """读取配置；文件缺失时使用默认值，非法内容抛出 ConfigError。"""
    if not path.exists():
        return {"interval": DEFAULT_INTERVAL, "source": DEFAULT_SOURCE}
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError("无法读取配置文件 {0}: {1}".format(path, exc)) from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError("配置文件 {0} 不是合法 JSON: {1}".format(path, exc)) from exc
    if not isinstance(data, dict):
        raise ConfigError("配置文件 {0} 顶层必须是对象".format(path))
    interval = data.get("interval", DEFAULT_INTERVAL)
    source = data.get("source", DEFAULT_SOURCE)
    if isinstance(interval, bool) or not isinstance(interval, int) or interval <= 0:
        raise ConfigError("配置项 interval 必须是正整数，实际为 {0!r}".format(interval))
    if not isinstance(source, str) or not source.strip():
        raise ConfigError("配置项 source 必须是非空字符串，实际为 {0!r}".format(source))
    return {"interval": interval, "source": source}


def build_record(config: dict) -> str:
    """构造一条可被下游解析的更新记录。"""
    return "[UPDATE] ts={ts} source={source} interval={interval} status=ok".format(
        ts=FIXED_TIMESTAMP,
        source=config["source"],
        interval=config["interval"],
    )


def main() -> int:
    try:
        config = load_config()
    except ConfigError as exc:
        print("[ERROR] {0}".format(exc), file=sys.stderr)
        return 1
    record = build_record(config)
    print(record)
    return 0


if __name__ == "__main__":
    sys.exit(main())
