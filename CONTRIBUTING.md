# 参与贡献

感谢你愿意改进 Prompt Quality Lab。这个项目更看重可复现的小改动，而不是一次加入很多尚未验证的功能。

## 先确认改动范围

当前主要维护：

- JSONL 数据读取与错误提示
- 确定性的文本质量指标
- 基线比较和 CI 门禁
- 中英文示例与文档

上游 Prompt 优化模块仍然保留，但涉及大范围重构时，请先提交功能建议，说明为什么不能在离线评测层独立完成。

安全漏洞或可能包含敏感数据的问题请按 [SECURITY.md](SECURITY.md) 处理，不要直接公开日志、API Key 或原始业务数据。

## 本地环境

只开发离线评测功能：

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

需要运行上游优化模块测试：

```bash
python -m pip install -e ".[dev,optimize]"
```

## 推荐流程

1. 从 `main` 创建短生命周期分支。
2. 行为改动先写一个能够复现问题的失败测试。
3. 用最小实现让测试通过，再整理命名和重复代码。
4. 更新 README、示例或 `CHANGELOG.md` 中受影响的部分。
5. 本地运行与 CI 相同的检查。

```bash
pytest tests -q
black --check src tests
isort --check-only --profile black src tests
pqlab evaluate examples/quality/candidate.jsonl --baseline examples/quality/baseline.jsonl --gate-metric character_f1 --min-score 0.90 --min-improvement 0
```

## 测试原则

- 测试面向用户能观察到的行为，不检查私有实现细节。
- 预期值应人工推导，不能调用被测函数生成预期结果。
- 离线评测测试不得访问网络，也不得依赖 API Key。
- 修复 Bug 时，测试名称要说明它防止哪一种回归。
- 文档改动不需要为了覆盖率硬写测试，但示例命令必须实际运行。

## 提交与 Pull Request

提交信息采用简短前缀：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 只修改文档
- `test:` 只修改测试
- `refactor:` 不改变行为的代码整理
- `chore:` 构建、依赖或维护配置

Pull Request 请保持单一主题，并写清：

- 要解决的问题
- 方案和取舍
- 实际运行过的验证命令及结果
- 是否改变报告字段、CLI 参数或退出码
- 是否包含经过脱敏的示例数据

所有贡献继续使用仓库根目录中的 MIT License。提交代码即表示你有权以该许可证提供相关内容。
