# Prompt Quality Lab

[![CI](https://github.com/burriedalien666/prompt-quality-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/burriedalien666/prompt-quality-lab/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个面向 LLM 输出的离线质量评测工具：把模型输出保存为 JSONL，就能比较候选版本与基线版本，并在质量下降时让 CI 失败。

项目当前处于 `0.1.x` 实验阶段。现有主线专注于三件事：结果可复现、中文评测可用、质量门禁能直接接入工程流程。

## 为什么做这个项目

Prompt 改了几句话、模型版本升级，或者推理参数换了一组，输出都可能悄悄退化。人工抽查很难稳定复现，在线评测又会受 API 费用、网络和模型波动影响。

Prompt Quality Lab 把“生成”和“评分”拆开：模型输出只需保存一次，之后可以在本地反复评测，不需要 API Key，也不会再次调用模型。它适合放在提交前检查或 CI 中，回答一个简单问题：**这次改动至少没有比基线更差吗？**

适合的场景：

- Prompt 或模型版本变更后的回归检查
- 中文客服、问答、摘要等文本输出的离线比较
- 小型评测集的可复现实验
- 需要以退出码阻止低质量版本合并的 CI 流程

暂时不适合：

- 代替人工评审开放式创作质量
- 直接运行大模型推理或托管评测数据
- 把字符重合度当作事实正确性的完整判断

## 五分钟跑通

要求 Python 3.10 或更高版本。

```bash
git clone https://github.com/burriedalien666/prompt-quality-lab.git
cd prompt-quality-lab
python -m venv .venv
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -e .
```

macOS / Linux：

```bash
source .venv/bin/activate
python -m pip install -e .
```

运行仓库自带的中英文示例：

```bash
pqlab evaluate examples/quality/candidate.jsonl --baseline examples/quality/baseline.jsonl --gate-metric character_f1 --min-score 0.90 --min-improvement 0
```

预期结果：

```text
Quality report
Samples: 4
Exact match: 0.7500
Token F1: 0.7500
Character F1: 0.9643
Gate metric: Character F1
Status: PASS
Exact match delta: +0.7500
Token F1 delta: +0.5500
Character F1 delta: +0.2265
```

这里的数值来自仓库内四条演示数据，只用于说明评测流程，不代表通用模型基准。具体样本和逐条结果见 [examples/quality](examples/quality/README.md)。

## 输入格式

输入文件采用 JSONL：一行一个 JSON 对象，至少包含 `expected` 和 `actual`。建议提供稳定的 `id`，便于定位失败样本。

```json
{"id":"zh-refund","expected":"退款申请已通过","actual":"退款申请通过"}
{"id":"en-password","expected":"Reset link sent","actual":"Reset sent"}
```

字段名可以替换：

```bash
pqlab evaluate outputs.jsonl --expected-field reference --actual-field response --id-field case_id
```

格式错误、缺少字段或基线与候选样本数不同都会返回非零退出码，并给出所在行或错误原因。

## 三个确定性指标

| 指标 | 计算方式 | 更适合 |
| --- | --- | --- |
| `exact_match` | 忽略大小写和多余空白后完全相同 | 标签、短答案、固定格式 |
| `token_f1` | 按空白切词，计算词项重合的 F1 | 英文句子、已有分词文本 |
| `character_f1` | 移除空白后按 Unicode 字符计算 F1 | 中文、日文及无空格短文本 |

中文句子通常没有词间空格。例如“退款申请已通过”和“退款申请通过”在 `token_f1` 下会被视为两个完全不同的 token，而 `character_f1` 能反映它们的大部分字符仍然重合。这也是本项目默认示例选择字符级门禁的原因。

这些指标全部是确定性的，同一份输入会得到同一份结果。它们适合回归检测，但不能单独证明回答真实、无偏或安全。

## 配置质量门禁

`--gate-metric` 决定哪一个指标用于判定通过与否：

```bash
# 候选字符 F1 至少达到 0.90
pqlab evaluate candidate.jsonl --gate-metric character_f1 --min-score 0.90

# 候选字符 F1 不得低于基线
pqlab evaluate candidate.jsonl --baseline baseline.jsonl --gate-metric character_f1 --min-improvement 0

# 要求相比基线至少提升 0.02
pqlab evaluate candidate.jsonl --baseline baseline.jsonl --gate-metric character_f1 --min-improvement 0.02
```

门禁不通过时命令退出码为 `1`。输入文件无效时同样返回非零退出码，因此可以直接交给 CI 判断。

生成机器可读报告：

```bash
pqlab evaluate candidate.jsonl --baseline baseline.jsonl --format json --output quality-report.json
```

JSON 报告包含聚合分数、逐条分数、基线差值、门禁配置、`passed` 状态和失败原因。

## 接入 GitHub Actions

仓库自己的 CI 就使用同一条命令。项目中可以加入如下步骤：

```yaml
- name: Run offline LLM quality gate
  run: >-
    pqlab evaluate
    examples/quality/candidate.jsonl
    --baseline examples/quality/baseline.jsonl
    --gate-metric character_f1
    --min-score 0.90
    --min-improvement 0
```

这一步不访问模型服务，也不需要在仓库 Secrets 中保存模型密钥。

## 上游优化能力

本仓库保留了 Meta prompt-ops 的 Prompt 优化模块。只做离线评测时不安装重型模型依赖；需要使用原有优化流程时再安装可选依赖：

```bash
python -m pip install -e ".[optimize]"
prompt-ops migrate --config configs/facility-simple.yaml
```

优化流程可能需要模型服务和对应的 API Key，离线 `pqlab evaluate` 不需要。

## 项目结构

```text
src/prompt_ops/core/quality.py     核心指标与基线比较
src/prompt_ops/interfaces/cli.py  命令行入口
tests/unit/test_quality*.py       评测与 CLI 回归测试
examples/quality/                 可直接运行的中英文样本
.github/workflows/ci.yml          格式、测试和质量门禁
```

## 项目来源与改动边界

Prompt Quality Lab 是 [Meta prompt-ops](https://github.com/meta-llama/prompt-ops) 的下游工程扩展，继续使用原项目的 MIT License，并保留上游代码中的版权声明。

本仓库新增和重点维护的部分包括：

- JSONL 离线评测命令与 JSON / 文本报告
- Exact Match、Token F1 和面向中文的 Character F1
- 基线回归、绝对阈值和 CI 退出码
- 无重型 AI 依赖的评测安装路径
- 中文使用文档、示例和维护流程

更详细的来源说明见 [NOTICE](NOTICE)。这一区分很重要：仓库不会把上游已有能力包装成本项目原创成果。

## 后续计划

近期优先级是结构化 JSON 输出、失败样本摘要和更严格的基线样本对齐。完整计划见 [ROADMAP.md](ROADMAP.md)。

如果你想提交问题或改动，请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。维护方式和版本检查清单记录在 [MAINTAINERS.md](MAINTAINERS.md)。

## License

本项目使用 [MIT License](LICENSE)。上游归属信息见 [NOTICE](NOTICE)。
