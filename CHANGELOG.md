# 更新记录

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 的结构。正式发布前的改动统一记录在 `Unreleased`。

## Unreleased

### Added

- 离线 JSONL 输出评测命令 `pqlab evaluate`
- Exact Match、Token F1 与 Unicode Character F1
- 候选版本和基线版本的质量回归门禁
- JSON 与文本两种报告格式
- 可直接运行的中英文评测示例
- GitHub Actions 离线质量检查

### Changed

- 项目定位调整为 Prompt Quality Lab
- 主 README、示例说明与贡献流程改为中文
- AI 优化依赖改为可选安装，离线评测保持轻量

### Fixed

- 修复 JSON 指标读取原始字符串时丢失默认值的问题
- 更新字段映射和优化 fallback 的过期测试契约
