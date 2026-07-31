# 安全说明

## 支持范围

在首个稳定版本发布前，只维护 `main` 分支上的最新代码。旧提交不会单独回补安全修复。

## 报告安全问题

如果问题可能泄露 API Key、私有评测数据、文件路径或其他敏感信息，请不要创建公开 Issue。请先打开仓库 Security 页面；若页面提供 `Report a vulnerability`，使用该入口私密提交：

https://github.com/burriedalien666/prompt-quality-lab/security

报告中请包含：

- 受影响的版本或提交
- 最小复现步骤
- 可能造成的影响
- 已做脱敏处理的日志或样本

普通崩溃、错误提示或不涉及敏感数据的输入校验问题可以使用 Bug 模板公开提交。

## 数据与密钥

`pqlab evaluate` 只读取本地文件，不需要 API Key，也不会主动上传评测数据。上游 `prompt-ops migrate` 可以连接第三方模型服务；使用该能力时，应通过环境变量或本地 `.env` 管理密钥，并确认 `.env` 不会被提交。
