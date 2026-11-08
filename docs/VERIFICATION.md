# 验证与验收方案

## 1. 来源与日期

- 来源：仓库 CI 反馈与本轮修复要求；不包含外部文章事实。
- 日期：2026-10-25（仓库基准日期，非文章发布时间）。
- 性质：本文件是可执行验收清单，不新增事实性结论；未实际运行的项目均标注为“待执行”。

## 2. 验收维度与通过条件

| 维度 | 可执行命令 | 通过条件 | 证据 | 费用/人力 | 备选方案 |
| --- | --- | --- | --- | --- | --- |
| 效果 | `npm test` | 退出码 0，stdout 含“简报校验通过: 22 条选题, 6 个专题” | 完整 stdout | 0 元，0.2 小时 | 若失败，先跑 `python3 scripts/check-brief.js` 定位；不跳过失败项 |
| 结构 | `python3 scripts/batch_index.py` | 退出码 0，stdout 恰好 12 行且等于 `known_keys()` | 12 行去重键 | 0 元，0.1 小时 | 行数不符时回退新增行并重跑 |
| 单测 | `npm run test:python` | 退出码 0；`-v` 日志显示全部测试名及 `OK`；失败数为 0 | 用例列表与通过数 | 0 元，0.5 小时 | 仅 Node 环境可用时，先跑 `npm test` 并记录 Python 待执行 |
| 安全 | 见第 3 节命令 | 绝对路径、`..`、隐藏/敏感目录、不存在路径、反斜杠、符号链接逃逸均被拒绝；合法正斜杠路径通过 | stderr 关键字与退出码 | 0 元，0.5 小时 | 平台不支持符号链接时跳过该条并标注原因，不伪造通过 |
| 稳定性 | 连续运行 `npm test` 与 `npm run test:python` 各 2 次 | 相同输入 stdout 完全一致，退出码一致 | 前后输出 diff 为空 | 0 元，0.3 小时 | 不一致时保留两次日志并阻断合并 |
| 并发与清理 | `npm run test:python` 中的并发/清理用例 | 4 次并发输出集合大小为 1；`find . -maxdepth 1 -name 'tmp-check-brief*'` 无输出 | 用例名与 find 输出 | 0 元，0.2 小时 | 有残留时先人工删除并记录残留路径，再重跑 |
| 性能 | 不做结论 | 仅记录上一轮 CI `medianMs=118, runs=3, samples=[113,118,161]`；无改动前后基线，不得宣称收益 | CI 原始记录 | 0 元 | 如需性能结论，按第 5 节补前后各 3 次耗时，否则标注“不做性能结论” |

## 3. 安全边界命令与预期

- 绝对路径：`MACHINE_HEART_ROOT=/etc node scripts/check-brief.js`，预期非 0，stderr 含“必须是相对于仓库根目录的相对路径”。
- 父目录逃逸：`MACHINE_HEART_ROOT=.. node scripts/check-brief.js`，预期非 0，stderr 含“不能使用 .. 逃逸仓库根目录”。
- 隐藏目录：`MACHINE_HEART_ROOT=.git node scripts/check-brief.js`，预期非 0，stderr 含“不能指向隐藏目录或敏感路径”。
- 不存在路径：`MACHINE_HEART_ROOT=definitely-missing-dir node scripts/check-brief.js`，预期非 0，stderr 含“MACHINE_HEART_ROOT 无法解析”。
- 反斜杠：`MACHINE_HEART_ROOT='sub\\dir' node scripts/check-brief.js`，预期非 0，stderr 含“只能使用 / 作为路径分隔符”。该脚本契约仅接受 POSIX 风格相对路径；Windows 调用方使用 `/`，并由 `test_posix_style_relative_root_accepted` 验证正斜杠合法路径可通过。
- 符号链接逃逸：`tests/test_check_brief_security.py` 中目录与文件两条用例，预期非 0，stderr 含“越界或符号链接逃逸”。

## 4. 调用点与错误传播

- `scripts/batch_index.py` 调用点：CLI `python3 scripts/batch_index.py`；`tests/test_batch_index.py` 直接 `import batch_index`；`scripts/check-brief.js` 用正则解析 `ARTICLES` 与文档同步。
- 错误传播：`main()` 捕获 `validate_articles()` 的 `ValueError`，向 stderr 输出 `[INVALID] ...` 并返回 2；成功路径返回 0 且 stdout 为 12 行。新增 `test_main_stdout_matches_known_keys` 与 `test_known_keys_stable_contract` 覆盖成功契约与键格式。
- 兼容路径：现有合法 `ARTICLES` 不变；新增测试只读调用，不修改全局清单；`check-brief.js` 的正则仍匹配原有 `Article(...)` 形式。

## 5. 逐项安排、费用与备选

| 日期 | 动作 | 产出 | 费用/人力 | 备选方案 |
| --- | --- | --- | --- | --- |
| 2026-10-25 | 补本文件与 README/BATCHES 验收说明 | 文档 diff | 0 元，0.5 小时 | 文档与实现不一致时以测试命令为准并回改文档 |
| 2026-10-26 | 运行 `npm test`、`python3 scripts/batch_index.py`、`npm run test:python` 并保存 `-v` 日志 | 命令日志 | 0 元，0.5 小时 | 环境缺 Node/Python 时记录缺失项，不声称通过 |
| 2026-10-26 | 运行第 3 节安全命令与残留检查 | 安全日志 | 0 元，0.3 小时 | 不支持符号链接的平台标注跳过原因 |
| 2026-10-27 | 评审 diff，确认无编造指标、无测试删除 | 评审结论 | 0 元，0.5 小时 | 退回补充证据后再合并 |
| 2026-10-27 | 如需性能结论，记录改动前后各 3 次耗时 | 性能表 | 0 元，0.2 小时 | 不记录则明确“不做性能结论” |

合计：云资源 0 元；人工约 2 小时；不引入第三方依赖。

## 6. 不确定项

- 本文件未实际执行上述命令，执行结果以 CI 日志为准。
- Windows 原生路径分隔符未作为合法输入支持；当前契约是 POSIX 风格 `/`，这是为避免跨平台歧义的有意限制。
- 性能无基线，不能从上一轮 `medianMs=118` 得出任何收益结论。
