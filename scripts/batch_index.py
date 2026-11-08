#!/usr/bin/env python3
'''机器之心批次去重键与已知文章清单。

去重键固定为 source:mid:idx；同批次补采只追加新 idx，不覆盖已读。
'''

from __future__ import annotations

from typing import NamedTuple

SOURCE = 'machine_heart'


class Article(NamedTuple):
    mid: str
    idx: int
    title: str
    mainline: str
    url: str
    kind: str = '待核实'


ARTICLES = (
    Article('2651072640', 1, '纵横9米高空的机器人，跑出3.3个马拉松，一座大仓的极速28小时', '具身智能与机器人', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072640&idx=1&sn=e52b59c8ea12a5344d99ebea6098370e'),
    Article('2651072640', 2, '让机器人学会「一口气干完一件活」', '具身智能与机器人', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072640&idx=2&sn=b87d67bebe76dda38cc9eb5123d49239'),
    Article('2651072640', 3, '世界模型「云游戏」问世，李飞飞World Labs出品', '前沿模型与架构', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072640&idx=3&sn=52917d7d6f2663f8f3276ce4ae36cbb6'),
    Article('2651072404', 1, '对谈千问蒋冠军：从模型、记忆到生态，Personal Agent的技术架构如何搭建？', '产业与生态', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072404&idx=1&sn=1de487a458c1d282c00b4a696aae70ee'),
    Article('2651072404', 2, '刚刚，百度开源全新预训练基模，还是主打效率的Flash', '产业与生态', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072404&idx=2&sn=4dafbecc77de04a45e65aa78c40e6b16'),
    Article('2651072404', 3, '不做Token化，也不搞双系统！多模态模型有了第三条路', '前沿模型与架构', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072404&idx=3&sn=215382bbb92aebdbef3c201ac3e33851'),
    Article('2651072888', 1, 'ICLR 2027首轮评审，槽点有点多', '产业与生态', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072888&idx=1&sn=653a56cbd49310e83158f277d56a993b', '观点'),
    Article('2651072888', 2, 'GPT-6.1 Sol参与活体大脑手术！三轮定位，一次比一次准', '前沿模型与架构', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072888&idx=2&sn=7451fe12fd75fc3295e0e71c0235040a', '技术'),
    Article('2651072888', 3, '英伟达等重新设计VLA推理！机器人动作提速3.4倍', '具身智能与机器人', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072888&idx=3&sn=75cf566a70af17c8a5cfa30d459aab8b', '技术'),
    Article('2651072774', 1, '陶大程教授最新技术文章：一台机器人犯过的错，怎样让另一台少走弯路？', '具身智能与机器人', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072774&idx=1&sn=17484407e18d75fca1e41a09be82bc03', '技术'),
    Article('2651072774', 2, 'State of AI 2026：AGI 2027 真的会来吗？', '产业与生态', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072774&idx=2&sn=8b8a1f19a5fb23e7b97328ab977f5e6e', '观点'),
    Article('2651072774', 3, 'NeurIPS 2026 | 从「先出题」到「先探索」：重新思考Tool-Calling Agent的训练数据合成', '前沿模型与架构', 'https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072774&idx=3&sn=7907f035a6b5b83908acc800cf7b3d96', '技术'),
)


def dedup_key(mid: str, idx: int) -> str:
    if not mid or idx < 1:
        raise ValueError('mid 不能为空且 idx 必须为正整数')
    return f'{SOURCE}:{mid}:{idx}'


def known_keys() -> tuple[str, ...]:
    return tuple(dedup_key(article.mid, article.idx) for article in ARTICLES)


def main() -> int:
    for key in known_keys():
        print(key)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
