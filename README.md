# machine_heart
autojump 目标项目：机器之心定时更新

## 脚本运行方式

最小可执行骨架脚本位于 `scripts/update.py`，仅依赖 Python 标准库：

```bash
python3 scripts/update.py
```

脚本正常退出时退出码为 0，并在 stdout 输出至少一条以 `[UPDATE]` 开头的更新记录，例如：

```
[UPDATE] ts=2026-10-25T00:00:00Z source=machine_heart status=ok
```

脚本不访问网络、不写文件，重复执行输出一致，可安全用于定时任务重跑。

## 选题简报

本节整理原有 10 篇、已归档两个 mid 批次 6 篇、本轮新增两个 mid 批次 6 篇与最新两个 mid 批次 6 篇（共 28 篇，来源为微信公众号文章链接）为可执行的选题池。每条选题包含标题、来源链接、一句话摘要与推荐理由；摘要与理由基于搜索简报的研判，未经原文二次核实，引用前需回源确认。选题条目数与 `scripts/batch_index.py` 的 `ARCHIVED_ARTICLES` 登记条数（当前 18 条去重键）由 `scripts/check-brief.js` 运行时动态校验，不再硬编码；去重键与补采安排见 docs/BATCHES.md。

### 选题 1：PyTorch、JAX 都被点名，Softmax 曝出隐藏 Bug

- 标题：PyTorch、JAX都被点名！Softmax曝出隐藏Bug，Gemini立功
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651069889&idx=1&sn=f243963ab47a3c32471ca7d3319ef4c6
- 一句话摘要：PyTorch 与 JAX 两大主流框架中被点名的 Softmax 实现存在隐藏正确性问题，据称由 Gemini 协助发现。
- 推荐理由：涉及主流框架正确性、影响面广、时效性强，适合作为技术快讯优先跟进，但需先核实触发条件、受影响版本与官方修复状态。

### 选题 2：谷歌开源 TorchTPU，TPU 成为 PyTorch 原生设备

- 标题：谷歌开源TorchTPU！TPU成PyTorch原生设备，CUDA最深的护城河开始松动
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651069794&idx=2&sn=ae62dbad6234b3c4c7359543936974c7
- 一句话摘要：谷歌开源 TorchTPU，使 TPU 成为 PyTorch 原生设备，摘要称覆盖 4917 个模型、97% 对齐 GPU。
- 推荐理由：直接关系训练硬件选型格局，数据具体、可验证，适合做数据核对型深度解读。

### 选题 3：阿里千问 TRACE 用 FP4 加速强化学习

- 标题：FP4 W/A+FP4 KV的强化学习也能「又快又稳」：阿里千问提出TRACE，Rollout最高加速5.4倍
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651069672&idx=3&sn=6b461b4dbff4fd3f156ce081b60ac69e
- 一句话摘要：阿里千问提出 TRACE，在 FP4 W/A 与 FP4 KV 下实现强化学习 Rollout 最高 5.4 倍加速。
- 推荐理由：量化方案与加速比明确，对 RL 训练效率优化有直接参考价值，适合性能优化类选题。

### 选题 4：Agent 自我进化，微软与 UCSB 让 Agent 自读论文改代码

- 标题：行业首个Pro Agent问世！「AI祖师爷」Kevin Knight空降中国谈AI跃迁
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651069672&idx=1&sn=cda1b3d3e5fb5179e1e999897a41ca67
- 一句话摘要：报道行业首个 Pro Agent 相关进展，并涉及 Kevin Knight 来华谈 AI 跃迁；搜索简报同时提及微软与 UCSB 的 Agent 自读论文、改代码研究。
- 推荐理由：Agent 能力边界探索是当前主线之一，但本条标题与摘要内容存在错位，需回源确认具体成果归属后再定稿。

### 选题 5：MemT 1.0 把长期记忆做成模型内生能力

- 标题：刚刚，你每天在用的Skills发生了一件大事
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651069672&idx=2&sn=068a7cc38c194f505ebebf54e913d5fc
- 一句话摘要：搜索简报称 MemT 1.0 发布，将长期记忆做成模型内生能力，指向递归自我改进；本条链接标题指向 Skills 相关更新，需回源核对。
- 推荐理由：与 Agent 记忆主线呼应，属长期跟踪方向，但标题与摘要对应关系不确定，引用前必须核实。

### 选题 6：田渊栋新公司首个模型，AI 全程参与不到 4 个月造出

- 标题：Muse 能否帮 Meta 打赢翻身仗？
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651069889&idx=2&sn=961329a6795b7ba229a01c9f08a20237
- 一句话摘要：搜索简报提及田渊栋新公司首个模型由 AI 全程参与、不到 4 个月从零造出；本条链接标题指向 Meta Muse，二者对应关系需回源确认。
- 推荐理由：人物动向与模型研发速度具话题性，适合轻量资讯池，但需先厘清标题与摘要的错位。

### 选题 7：人大等团队开源 TabClustPFN，表格聚类开箱即用

- 标题：聚类也能「开箱即用」了！人大等团队开源TabClustPFN，给张表格就能自动分组
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651069889&idx=3&sn=be03ed61a5b5eccacdb6e68cce1c5210
- 一句话摘要：人大等团队开源 TabClustPFN，面向表格数据实现开箱即用的自动聚类分组。
- 推荐理由：开源工具类内容实用性强，适合工具推荐与实测类选题。

### 选题 8：Physical AI 下一轮 Scaling 为什么是 Physics

- 标题：RoboTwin第一、RoboDojo领跑：Physical AI的下一轮Scaling，为什么是Physics？
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651069794&idx=1&sn=27a6d06d4f43e6c032d7f79db1222815
- 一句话摘要：以 RoboTwin 第一、RoboDojo 领跑为引，讨论 Physical AI 下一轮 Scaling 中 Physics 的作用。
- 推荐理由：具身智能与物理仿真方向观点型内容，适合作为趋势解读素材。

### 选题 9：NeurIPS 26 从声音到回应，AI 如何理解并表达共情

- 标题：NeurIPS 26 | 从声音到回应，AI如何理解并表达共情？
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651069794&idx=3&sn=24de4df712471843cfc352f370b7d213
- 一句话摘要：NeurIPS 2026 论文方向介绍，聚焦 AI 在语音交互中理解与表达共情的能力。
- 推荐理由：学术会议论文类内容，适合归入论文速览与专题跟踪。

### 选题 10：腾讯元宝搜索首发实测（含福利激活码）

- 标题：首发实测！鹅厂刚开放的「元宝搜索」，给开发者减负了！（附福利激活码）
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651069516&idx=1&sn=2c2aa87e6fc360179ea20a6253cd2bd4
- 一句话摘要：对腾讯元宝搜索进行首发实测，面向开发者场景，文末附福利激活码。
- 推荐理由：产品实测类内容，含推广属性，应归入轻量资讯池并与纯技术内容区分。

### 选题 11：纵横9米高空的机器人，跑出3.3个马拉松，一座大仓的极速28小时

- 标题：纵横9米高空的机器人，跑出3.3个马拉松，一座大仓的极速28小时
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072640&idx=1&sn=e52b59c8ea12a5344d99ebea6098370e
- 一句话摘要：报道仓储机器人在 9 米高空连续作业 28 小时，并以 3.3 个马拉松等指标描述长时运行能力；量化口径需回源核实。
- 推荐理由：具身智能落地侧的长时运行证据，优先精读；时长、里程、成功率以原文为准。

### 选题 12：让机器人学会「一口气干完一件活」

- 标题：让机器人学会「一口气干完一件活」
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072640&idx=2&sn=b87d67bebe76dda38cc9eb5123d49239
- 一句话摘要：讨论机器人长程规划与连续任务执行，把从单步演示到连续完成一件活视为能力分水岭；技术细节待核实。
- 推荐理由：对应具身智能从演示走向连续任务的关键瓶颈，适合归入机器人落地跟踪。

### 选题 13：世界模型「云游戏」问世，李飞飞World Labs出品

- 标题：世界模型「云游戏」问世，李飞飞World Labs出品
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072640&idx=3&sn=52917d7d6f2663f8f3276ce4ae36cbb6
- 一句话摘要：报道 World Labs 以云游戏形态交付世界模型/空间智能产品；交互形态与算力成本待核实。
- 推荐理由：世界模型产品化样本，适合建立技术卡片并记录与主流方案差异。

### 选题 14：对谈千问蒋冠军：从模型、记忆到生态，Personal Agent的技术架构如何搭建？

- 标题：对谈千问蒋冠军：从模型、记忆到生态，Personal Agent的技术架构如何搭建？
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072404&idx=1&sn=1de487a458c1d282c00b4a696aae70ee
- 一句话摘要：从模型、记忆到生态拆解 Personal Agent 技术架构的一手对谈；观点属受访者，需回源核实。
- 推荐理由：Agent 生态主线的一手材料，适合归档并提炼记忆与生态架构要点。

### 选题 15：刚刚，百度开源全新预训练基模，还是主打效率的Flash

- 标题：刚刚，百度开源全新预训练基模，还是主打效率的Flash
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072404&idx=2&sn=4dafbecc77de04a45e65aa78c40e6b16
- 一句话摘要：报道百度开源文心 5.5 Flash Base 预训练基模，主打效率；参数、协议与推理成本未核实。
- 推荐理由：可能影响中小团队基座选型与推理成本结构，需核实开源协议、参数规模与评测口径。

### 选题 16：不做Token化，也不搞双系统！多模态模型有了第三条路

- 标题：不做Token化，也不搞双系统！多模态模型有了第三条路
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072404&idx=3&sn=215382bbb92aebdbef3c201ac3e33851
- 一句话摘要：介绍不做 Token 化、不采用双系统的连续统一多模态架构第三条路线；评测口径待核实。
- 推荐理由：架构层面的差异化路线，需核实其与主流 Token 化/双系统方案的真实差异。

### 选题 17：ICLR 2027首轮评审，槽点有点多

- 标题：ICLR 2027首轮评审，槽点有点多
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072888&idx=1&sn=653a56cbd49310e83158f277d56a993b
- 一句话摘要：机器之心汇总 ICLR 2027 首轮评审中的吐槽，涉及评审质量与“AI味”评语等争议；具体评审规则与样本未核实。
- 推荐理由：学术生态观察与观点类素材，适合趋势参考而非技术深度材料；会议名称与时间需核对。

### 选题 18：GPT-6.1 Sol参与活体大脑手术！三轮定位，一次比一次准

- 标题：GPT-6.1 Sol参与活体大脑手术！三轮定位，一次比一次准
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072888&idx=2&sn=7451fe12fd75fc3295e0e71c0235040a
- 一句话摘要：报道 GPT-6.1 Sol 参与活体大脑手术，称三轮定位逐步更准；涉及医疗安全，细节与真实性需独立核验。
- 推荐理由：高影响力应用案例，但风险高，应先交叉核验原始来源，不直接采信媒体表述。

### 选题 19：英伟达等重新设计VLA推理！机器人动作提速3.4倍

- 标题：英伟达等重新设计VLA推理！机器人动作提速3.4倍
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072888&idx=3&sn=75cf566a70af17c8a5cfa30d459aab8b
- 一句话摘要：英伟达等重构 VLA 推理，报道称机器人动作提速 3.4 倍；方法、基线、测试条件待回源。
- 推荐理由：具身智能推理效率的实质性优化，技术跟踪价值最高，优先精读方法与实验。

### 选题 20：陶大程教授最新技术文章：一台机器人犯过的错，怎样让另一台少走弯路？

- 标题：陶大程教授最新技术文章：一台机器人犯过的错，怎样让另一台少走弯路？
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072774&idx=1&sn=17484407e18d75fca1e41a09be82bc03
- 一句话摘要：陶大程团队技术文章讨论跨机器人经验复用与“双脑协同”，目标是从真实交互沉淀可复用物理经验；论文细节待核实。
- 推荐理由：机器人学习泛化的重要方向，适合建立技术卡片并纳入专题跟踪。

### 选题 21：State of AI 2026：AGI 2027 真的会来吗？

- 标题：State of AI 2026：AGI 2027 真的会来吗？
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072774&idx=2&sn=8b8a1f19a5fb23e7b97328ab977f5e6e
- 一句话摘要：汇总 State of AI 2026 对 AGI 时间表的预测与年度趋势判断；属观点类，预测口径待核实。
- 推荐理由：宏观背景与选题风向参考，不作为事实性结论引用。

### 选题 22：NeurIPS 2026 | 从「先出题」到「先探索」：重新思考Tool-Calling Agent的训练数据合成

- 标题：NeurIPS 2026 | 从「先出题」到「先探索」：重新思考Tool-Calling Agent的训练数据合成
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651072774&idx=3&sn=7907f035a6b5b83908acc800cf7b3d96
- 一句话摘要：介绍 Tool-Calling Agent 训练数据合成从“先出题”转向“先探索”的新思路，涉及可验证 Agent 学习的数据构造；方法与实验待回源。
- 推荐理由：对 Agent 研发有参考价值，适合与专题二、专题五联动；会议时间与命名需核对。

### 选题 23：后GPT-6时代，具身数据怎么做？Ropedia发布Xperience 2，给出下一代数据基石金标准

- 标题：后GPT-6时代，具身数据怎么做？Ropedia发布Xperience 2，给出下一代数据基石金标准
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651074362&idx=1&sn=c3ceac43168f01cb87b9bb3c28fa9877
- 一句话摘要：Ropedia 发布 Xperience 2，提出后 GPT-6 时代具身数据构建的下一代标准；数据规模、采集协议与评测口径待回源。
- 推荐理由：具身数据标准是行业关键问题，方向性强，适合优先精读并建立技术卡片。

### 选题 24：斯坦福让GPT-6 Astra直接修改机器人参数：只动65行词嵌入，修复一类指令失灵

- 标题：斯坦福让GPT-6 Astra直接修改机器人参数：只动65行词嵌入，修复一类指令失灵
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651074362&idx=2&sn=5a8b2bef8739a7443d5e57b276c4d80a
- 一句话摘要：报道斯坦福用 GPT-6 Astra 仅修改 65 行词嵌入，将指令成功率从 74.3% 提升到 87.5%；方法与基线待回源。
- 推荐理由：轻量模型干预带来可量化提升，方法论价值高，但 GPT-6 Astra 命名与数据口径需核实。

### 选题 25：ICSE 2027 | 清华提出CoACT：降低Coding Agent 33% Token开销

- 标题：ICSE 2027 | 清华提出CoACT：降低Coding Agent 33% Token开销
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651074362&idx=3&sn=da18bc335c6b6345ee976e60b4009347
- 一句话摘要：清华提出 CoACT，通过上下文压缩降低 Coding Agent 33% Token 开销；会议命名与实验条件待核实。
- 推荐理由：Agent 成本优化是工程落地核心问题，33% 节省有直接参考价值，适合纳入成本优化专题。

### 选题 26：10秒生成4K图：MiniMax再次拿出开源SOTA

- 标题：10秒生成4K图：MiniMax再次拿出开源SOTA
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651074135&idx=1&sn=94195be03009adcb3b3e390782573b38
- 一句话摘要：MiniMax 开源图像生成模型，称 10 秒生成 4K 图并达到 SOTA；速度、分辨率与开源协议待回源。
- 推荐理由：多模态生成进展突出，适合做简短快讯并跟踪开源协议与复现条件。

### 选题 27：Grok Bot 1.0正式发布！马斯克教AI和你的团队一起工作

- 标题：Grok Bot 1.0正式发布！马斯克教AI和你的团队一起工作
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651074135&idx=2&sn=2019b2d7e4f158bb07852a889f5a7b17
- 一句话摘要：报道 Grok Bot 1.0 正式发布，切入 AI 协作办公场景；产品能力与定价待核实。
- 推荐理由：产品化动向值得跟踪，适合归入产业生态快讯，不作为技术结论引用。

### 选题 28：64张B300、不到5天，FireFlash比肩Fable 5与GPT-6Sol，单任务成本低30倍！

- 标题：64张B300、不到5天，FireFlash比肩Fable 5与GPT-6Sol，单任务成本低30倍！
- 来源链接：https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2651074135&idx=3&sn=f702c61a40c6ebe66be517d551e8d6b6
- 一句话摘要：FireFlash 公开长程智能体 RL 完整配方，称 64 张 B300、不到 5 天完成训练，单任务成本低 30 倍；训练条件与对比基线待回源。
- 推荐理由：智能体训练成本优化参考价值高，适合纳入 Agent 成本优化专题并跟踪开源/论文进展。

## 使用说明

本节说明如何运行定时更新脚本、如何归档新批次文章，以及如何执行校验。

1. 运行更新脚本：`python3 scripts/update.py`，正常退出码为 0，stdout 输出一条 `[UPDATE]` 记录；脚本不访问网络、不写文件，可重复执行。
2. 归档新批次：在 `scripts/batch_index.py` 的 `NEW_ARTICLES` 中追加 `Article(mid, idx, title, mainline, url, kind)`，去重键固定为 `machine_heart:<mid>:<idx>`，只追加不覆盖。
3. 同步文档：在 `docs/BATCHES.md` 的「批次索引」小节登记去重键与主线，并在本文件「选题简报」新增对应选题条目。
4. 执行校验：`npm test` 校验 README 选题/专题结构、`docs/BATCHES.md` 去重键与 `scripts/batch_index.py` 一致性；`npm run test:python` 运行 Python 单元测试。
5. 回源核实：所有量化指标、开源协议与会议命名在引用前必须回源确认，未核实前保持「待核实」状态。

## 专题跟踪

以下六个专题与 docs/ROADMAP.md 中的「专题跟踪清单」逐条对应，名称保持一致，便于跨文档核对。

### 专题一：框架正确性与硬件生态

- 覆盖选题：选题 1（Softmax 隐藏 Bug）、选题 2（TorchTPU）。
- 跟踪要点：核实 Softmax Bug 的触发条件、受影响版本与官方修复进展；整理 TorchTPU 的模型覆盖数与性能对齐数据。
- 产出形式：技术快讯 + 数据核对型解读。
- 优先级：高。

### 专题二：Agent 自我进化与长期记忆

- 覆盖选题：选题 4（Agent 自读论文改代码）、选题 5（MemT 1.0）、选题 22（Tool-Calling Agent 数据合成，技术类）。
- 跟踪要点：合并 Agent 自我进化、长期记忆、科研自动化三条线索；回源确认各成果的机构归属与发布时间。
- 产出形式：专题综述，按周更新进展。
- 优先级：高。

### 专题三：训练效率与量化加速

- 覆盖选题：选题 3（TRACE FP4 强化学习加速）、选题 19（VLA 推理提速，技术类；推理效率相邻）。
- 跟踪要点：摘录 TRACE 的 FP4 W/A 与 FP4 KV 方案要点及 5.4 倍加速的测试条件。
- 产出形式：性能优化类要点摘录。
- 优先级：中。

### 专题四：具身智能与机器人落地

- 覆盖选题：选题 11（高空仓储机器人 28 小时）、选题 12（机器人长程规划）、选题 19（VLA 推理提速）、选题 20（跨机器人经验复用）。
- 跟踪要点：记录时长、里程、成功率、人工干预次数等可量化指标；区分厂商口径与第三方复现。
- 产出形式：落地跟踪条目 + 技术卡片。
- 优先级：高。

### 专题五：前沿模型与世界模型架构

- 覆盖选题：选题 13（World Labs 云游戏）、选题 16（连续统一多模态第三条路）、选题 18（GPT-6.1 医疗应用，需核验）、选题 22（Tool-Calling Agent 数据合成）。
- 跟踪要点：记录交互形态、算力成本、评测口径，并与 Token 化/双系统方案对照。
- 产出形式：技术卡片 + 对比表。
- 优先级：高。

### 专题六：产业生态与开源基座

- 覆盖选题：选题 14（Personal Agent 架构）、选题 15（百度文心 5.5 Flash Base）、选题 17（ICLR 2027 评审观点）、选题 21（State of AI 2026 趋势观点）。
- 本轮新增：选题 17（ICLR 2027 评审观点，观点类）、选题 21（State of AI 2026 趋势观点，观点类）；两条均为观点素材，不作为事实性结论引用。
- 跟踪要点：核实开源协议、参数规模、推理成本与 Agent 记忆/生态架构，判断是否纳入基座选型对比表。
- 产出形式：生态动向归档 + 选型备忘。
- 优先级：中。

## 来源与日期

- 内容来源：机器之心微信公众号更新，共 28 篇（原有 10 篇 + 已归档两个 mid 批次 6 篇 + 本轮新增两个 mid 批次 6 篇 + 最新两个 mid 批次 6 篇），链接见各选题条目。
- 批次归档：mid=2651072640、2651072404、2651072888、2651072774、2651074362 与 2651074135 的 idx 1-3 已登记到 docs/BATCHES.md，去重键固定为 machine_heart:<mid>:<idx>；最新 6 篇登记于 scripts/batch_index.py 的 LATEST_ARTICLES。
- 整理日期：2026-10-25（与 docs/ROADMAP.md 生成时间同日；非文章发布时间）。
- 数据性质：摘要与推荐理由来自搜索简报研判，属外部不可信数据，未经原文逐篇核实；标注「需回源确认」的条目在引用前必须二次核实。
- 已知不确定项：选题 4、5、6 的标题与搜索简报摘要存在对应关系不明；选题 17-28 的会议命名、医疗安全表述、VLA 3.4 倍提速条件、跨机器人经验复用、Tool-Calling Agent 数据合成、GPT-6 Astra 成功率、CoACT 33% Token 节省、MiniMax 4K 生成、Grok Bot 1.0 与 FireFlash 成本倍数均需回源确认，不得直接作为事实引用。
- 漏采提示：六个 mid 批次仅确认 idx 1-3，idx=4 及以后是否存在尚未验证，补采步骤见 docs/BATCHES.md。
- 推广内容提示：选题 10 含福利激活码，属厂商推广，应与纯技术内容区分处理。

## 验证与验收

- 验收标准、CI 维度映射、跨平台矩阵与证据模板见 `docs/VERIFICATION.md`。
- 性能不做收益结论：历史 CI 仅有耗时记录，缺少改动前后基线，本文不引用具体耗时作为验收指标。
- 跨平台路径契约：`MACHINE_HEART_ROOT` 仅接受 POSIX 风格相对路径；Windows 调用方使用 `/` 分隔，三平台结果按 `docs/VERIFICATION.md` 矩阵记录，未执行不得填通过。
- 证据要求：PR 附 `npm test`、`npm run test:python`（含 `-v`）完整日志，需含用例名、通过数、失败数 0；并发与清理测试须断言无临时目录残留。
- 文档一致性：`npm test` 同时校验 README、`docs/BATCHES.md`、`docs/VERIFICATION.md` 与 `scripts/batch_index.py` 的关键契约一致。
