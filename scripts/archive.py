#!/usr/bin/env python3
"""机器之心本轮文章归档与简报校验。

本模块只依赖 Python 标准库，提供三件事：
1. 本轮三篇新文章的静态清单（标题、链接、分类、日期、摘要）；
2. 生成稳定、可解析的归档记录（幂等，不访问网络、不写文件）；
3. 校验文章条目必填字段，缺失或格式错误时返回非零退出码。

注意：文章标题、链接与摘要来自外部搜索简报，属不可信数据，
仅作归档索引使用，引用前需回源核实。
"""

from __future__ import annotations

import sys
from typing import Dict, List

# 归档日期：与 README.md / docs/ROADMAP.md 中标注的整理日期保持一致。
ARCHIVE_DATE = "2026-10-25"

REQUIRED_FIELDS = ("title", "url", "category", "date", "summary")

ARTICLES: List[Dict[str, str]] = [
    {
        "title": "对谈千问蒋冠军：从模型、记忆到生态，Personal Agent的技术架构如何搭建？",
        "url": "https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072404&idx=1&sn=1de487a458c1d282c00b4a696aae70ee",
        "category": "智能体",
        "date": ARCHIVE_DATE,
        "summary": "系统讨论 Personal Agent 从模型、记忆到生态的搭建思路。",
    },
    {
        "title": "刚刚，百度开源全新预训练基模，还是主打效率的Flash",
        "url": "https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072404&idx=2&sn=4dafbecc77de04a45e65aa78c40e6b16",
        "category": "基础模型",
        "date": ARCHIVE_DATE,
        "summary": "百度开源全新预训练基模文心 5.5 Flash Base，主打效率。",
    },
    {
        "title": "不做Token化，也不搞双系统！多模态模型有了第三条路",
        "url": "https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072404&idx=3&sn=215382bbb92aebdbef3c201ac3e33851",
        "category": "多模态",
        "date": ARCHIVE_DATE,
        "summary": "提出不依赖 Token 化与双系统的连续统一多模态模型新路径。",
    },
]


def validate_articles(articles: List[Dict[str, str]]) -> List[str]:
    """返回错误列表；空列表表示校验通过。"""
    errors: List[str] = []
    if not articles:
        errors.append("文章清单为空")
        return errors
    for i, article in enumerate(articles, start=1):
        name = "文章 " + str(i)
        for field in REQUIRED_FIELDS:
            value = article.get(field, "")
            if not isinstance(value, str) or not value.strip():
                errors.append(name + " 缺少字段: " + field)
        url = article.get("url", "")
        if url and not (url.startswith("http://") or url.startswith("https://")):
            errors.append(name + " 链接格式错误: " + url)
    return errors


def build_archive_records(articles: List[Dict[str, str]] | None = None) -> List[str]:
    """生成稳定排序的归档记录，重复调用输出一致。"""
    items = ARTICLES if articles is None else articles
    records: List[str] = []
    for article in items:
        records.append(
            "[ARCHIVE] date={date} category={category} title={title} url={url}".format(
                date=article.get("date", ""),
                category=article.get("category", ""),
                title=article.get("title", ""),
                url=article.get("url", ""),
            )
        )
    return records


def main(argv: List[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if "--validate" in args:
        errors = validate_articles(ARTICLES)
        if errors:
            for e in errors:
                print("[ERROR] " + e, file=sys.stderr)
            return 1
        print("[VALIDATE] ok articles=" + str(len(ARTICLES)))
        return 0
    for record in build_archive_records():
        print(record)
    return 0


if __name__ == "__main__":
    sys.exit(main())
