# agent-memory-infra

面向多 Agent 系统的可学习记忆基础设施（Learning Memory Infrastructure）。

定位不是某个 Agent 的 Memory 模块，而是独立的 Memory Policy 实验场。先验证检索策略，再接入多 Agent 总控平台，不一开始耦合业务代码。

## 第一阶段假设

历史任务反馈 → 能否让下一次 Memory Retrieval 比单纯向量相似度更好。

对照：

- baseline：向量相似度
- policy：相似度 + 历史任务反馈学到的权重

## 结构

```
agent-memory-infra/
├── README.md
├── pyproject.toml
├── src/memory_infra/
│   ├── memory.py
│   ├── policy.py
│   ├── retrieval.py
│   ├── learner.py
│   └── trace.py
├── experiments/baseline_vs_policy.py
├── tests/test_memory_policy.py
└── docs/
    ├── architecture.md
    └── research-log.md
```

## 跑实验

```bash
pip install -e ".[dev]"
python experiments/baseline_vs_policy.py
pytest
```
