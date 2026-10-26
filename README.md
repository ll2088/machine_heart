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
