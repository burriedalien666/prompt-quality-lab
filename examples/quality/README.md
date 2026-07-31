# 中英文质量门禁示例

这个目录保存一组很小、可以人工核对的演示数据，用来说明基线比较的完整流程。

- `baseline.jsonl`：一次较早的模型输出，四条都没有完全命中参考答案。
- `candidate.jsonl`：候选版本，退款、英文回复和 JSON 路由结果完全命中；配送回复仍缺少“下午”。

运行：

```bash
pqlab evaluate examples/quality/candidate.jsonl --baseline examples/quality/baseline.jsonl --gate-metric character_f1 --min-score 0.90 --min-improvement 0 --format json
```

当前样本的聚合结果：

| 版本 | Exact Match | Token F1 | Character F1 |
| --- | ---: | ---: | ---: |
| baseline | 0.0000 | 0.2000 | 0.7378 |
| candidate | 0.7500 | 0.7500 | 0.9643 |
| 差值 | +0.7500 | +0.5500 | +0.2265 |

命令以 `character_f1` 作为门禁指标。候选值达到 `0.90`，并且没有低于基线，因此退出码为 `0`。

这四条记录只用于演示，不是模型排行榜或统计意义上的评测集。实际项目应把固定测试集加入版本控制，把每次待发布模型的输出保存为新的候选文件。
