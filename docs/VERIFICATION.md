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
| 性能 | 不做收益结论 | CI 性能 success 仅表示命令未超时；不采集 medianMs 作为验收指标，无前后基线不得宣称收益 | CI 原始耗时仅参考 | 0 元 | 如需性能结论，按第 5 节补前后各 3 次耗时，否则标注“不做性能结论” |

### 2.1 CI 维度映射

| CI 维度 | 对应验收项 | 可执行命令 | 通过条件 | 证据 |
| --- | --- | --- | --- | --- |
| 效果 | 简报结构、文档一致性 | `npm test` | 退出码 0，stdout 含“简报校验通过: 22 条选题, 6 个专题, 文档一致性通过” | 完整 stdout |
| 性能 | 不做收益结论 | 无收益命令 | 不采集 medianMs、不设收益阈值；只记录“不做性能结论” | 无 |
| 稳定性 | 重复执行与并发隔离 | `npm test`、`npm run test:python` 各 2 次 | 相同输入 stdout 与退出码一致；并发 4 次输出集合大小为 1 | 两次日志 diff 为空 |
| 可用性 | 安全边界与错误传播 | 第 3 节命令、`python3 scripts/batch_index.py` | 非法路径均非 0 且 stderr 含关键字；合法路径返回 0；索引输出 12 行 | stderr 与退出码 |

### 2.2 证据提交模板

PR 必须附以下原始证据，未实际执行的项目标注“未执行”，不得填通过：
1. `npm test` 完整 stdout；
2. `npm run test:python`（含 `-v`）完整日志，需出现 `test_batch_index`、`test_check_brief`、`test_check_brief_security` 的用例名、通过数、失败数 0；
3. `python3 scripts/batch_index.py` 的 12 行去重键；
4. `find . -maxdepth 1 -name 'tmp-check-brief*'` 空输出；
5. 三平台路径用例结果；仅实际跑过的平台填“通过”。

### 2.3 跨平台矩阵（未执行项不得填通过）

| 平台 | 正斜杠相对路径 | 反斜杠拒绝 | 符号链接越权拒绝 | 状态 |
| --- | --- | --- | --- | --- |
| Linux | `test_posix_style_relative_root_accepted` | `test_backslash_separator_rejected` | `test_symlink_directory_escape_rejected` | 待执行/以 CI 日志为准 |
| macOS | 同上 | 同上 | 同上 | 待执行/以 CI 日志为准 |
| Windows | 正斜杠用例 | 反斜杠用例 | 平台支持符号链接时执行 | 待执行/以 CI 日志为准 |

## 3. 安全边界命令与预期

- 绝对路径：`MACHINE_HEART_ROOT=/etc node scripts/check-brief.js`，预期非 0，stderr 含“必须是相对于仓库根目录的相对路径”。
- 父目录逃逸：`MACHINE_HEART_ROOT=.. node scripts/check-brief.js`，预期非 0，stderr 含“不能使用 .. 逃逸仓库根目录”。
- 隐藏目录：`MACHINE_HEART_ROOT=.git node scripts/check-brief.js`，预期非 0，stderr 含“不能指向隐藏目录或敏感路径”。
- 不存在路径：`MACHINE_HEART_ROOT=definitely-missing-dir node scripts/check-brief.js`，预期非 0，stderr 含“MACHINE_HEART_ROOT 无法解析”。
- 反斜杠：`MACHINE_HEART_ROOT='sub\\dir' node scripts/check-brief.js`，预期非 0，stderr 含“只能使用 / 作为路径分隔符”。该脚本契约仅接受 POSIX 风格相对路径；Windows 调用方使用 `/`，并由 `test_posix_style_relative_root_accepted` 验证正斜杠合法路径可通过。
- 符号链接逃逸：`tests/test_check_brief_security.py` 中目录与文件两条用例，预期非 0，stderr 含“越界或符号链接逃逸”。
- 注入面：`MACHINE_HEART_ROOT='sub;touch /tmp/machine-heart-pwned'` 由测试以参数列表传入，不经过 shell；预期非 0 且 stderr 含“MACHINE_HEART_ROOT 无法解析”，标记文件不得生成。
- 权限边界：`.git`、`.github`、`.svn`、`.idea`、`.vscode`、`node_modules`、`__pycache__` 及任意点开头路径段均拒绝；指向仓库内敏感目录的符号链接同样拒绝。

## 4. 调用点与错误传播

- `scripts/batch_index.py` 调用点：CLI `python3 scripts/batch_index.py`；`tests/test_batch_index.py` 直接 `import batch_index`；`scripts/check-brief.js` 用正则解析 `ARTICLES` 与文档同步。
- 错误传播：`main()` 捕获 `validate_articles()` 的 `ValueError`，向 stderr 输出 `[INVALID] ...` 并返回 2；成功路径返回 0 且 stdout 为 12 行。新增 `test_main_stdout_matches_known_keys` 与 `test_known_keys_stable_contract` 覆盖成功契约与键格式。
- 兼容路径：现有合法 `ARTICLES` 不变；新增测试只读调用，不修改全局清单；`check-brief.js` 的正则仍匹配原有 `Article(...)` 形式。
- 异常分支覆盖：`validate_articles()` 对空序列、非序列、非 `Article`、非法 mid/idx、空白标题、非字符串字段、未知主线/属性、非 http(s) URL、非机器之心 URL 均抛 `ValueError`；`main()` 捕获后 stderr 输出 `[INVALID]` 并返回 2。
- 全部调用点验证：CLI 由 `test_main_*` 覆盖；unittest import 由 `test_validate_articles_*` 覆盖；`check-brief.js` 正则解析由 `test_batch_index_out_of_sync_fails` 与非法 Article 格式用例覆盖。

## 5. 逐项安排、费用与备选

| 日期 | 动作 | 产出 | 费用/人力 | 备选方案 |
| --- | --- | --- | --- | --- |
| 2026-10-25 | 补本文件与 README/BATCHES 验收说明 | 文档 diff | 0 元，0.5 小时 | 文档与实现不一致时以测试命令为准并回改文档 |
| 2026-10-26 | 运行 `npm test`、`python3 scripts/batch_index.py`、`npm run test:python` 并保存 `-v` 日志 | 命令日志 | 0 元，0.5 小时 | 环境缺 Node/Python 时记录缺失项，不声称通过 |
| 2026-10-26 | 运行第 3 节安全命令与残留检查 | 安全日志 | 0 元，0.3 小时 | 不支持符号链接的平台标注跳过原因 |
| 2026-10-27 | 评审 diff，确认无编造指标、无测试删除 | 评审结论 | 0 元，0.5 小时 | 退回补充证据后再合并 |
| 2026-10-27 | 性能不采集 medianMs、不设收益阈值；如需结论才记录前后各 3 次耗时 | 性能说明 | 0 元，0.2 小时 | 无基线则明确“不做性能结论” |

合计：云资源 0 元；人工约 2 小时；不引入第三方依赖。

## 6. 不确定项

- 本文件未实际执行上述命令，执行结果以 CI 日志为准。
- Windows 原生路径分隔符未作为合法输入支持；当前契约是 POSIX 风格 `/`，这是为避免跨平台歧义的有意限制。
- 性能无基线；本文件不引用任何具体耗时，CI 性能 success 仅表示命令未超时，不构成收益证明。
