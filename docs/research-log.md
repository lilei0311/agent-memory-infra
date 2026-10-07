# Research log

## 2026-10-07

仓库单独拆出。第一阶段只验证：历史任务反馈能否让下一次 retrieval 好于纯向量相似度。

合成样例：最近邻居是重复失败，稍远的 item 是重复成功。policy 应选成功项，baseline 选失败项。

## 2026-10-07 (align-code-with-protocols, direct to main)

对齐代码与 docs/PROTOCOLS.md，跳过 PR 直接提交到 main：

- RetrievalTrace 扩展为单条交互记录：trace_id、task_id、memory_id、retrieved、rank、mode、policy_version，加 used、task_success、user_feedback（缺失信号为 None，不猜测）。
- retrieve() 返回 list[RetrievalTrace]，每个取回项一条记录。
- FeedbackLearner：alpha 只在 policy 选对且不等于 baseline 时推高（成功）或降低（失败）；同选时不变。
- MemoryItem.utility 改为 Laplace 平滑：(success - failure) / (success + failure + 1)，防稀疏反馈打穿。
- policy.py 注释说明 v0.1 是两项式，四权重是文档目标。
- 测试补充：leaner 条件、alpha 不变、失败降低、utility 平滑。

## 2026-10-07 (v0.1 experiment: baseline_vs_policy.py)

合成实验，seed=7，20 轮，k=3。

结果：

  round | baseline_top | policy_top | alpha
  -----+--------------+-----------+------
      1 | near-fail-1  | far-ok-1   | 0.55
      2 | near-fail-1  | far-ok-1   | 0.60
      3 | near-fail-1  | far-ok-1   | 0.65
      5 | near-fail-1  | far-ok-1   | 0.75
     10 | near-fail-1  | far-ok-1   | 1.00
     15 | near-fail-1  | far-ok-1   | 1.25
     20 | near-fail-1  | far-ok-1   | 1.50

  Summary:
    baseline success rate : 0.00
    policy   success rate : 1.00
    alpha trajectory      : 0.50 -> 1.50

Pass criteria:
  1. policy > baseline        : True
  2. alpha rises              : True
  3. policy converges to far-ok : True

Seed sweep (20 seeds, ROUNDS=20): 19/20 fully pass.
Two seeds (0, 10) gave policy success 0.95 instead of 1.00 —
neutral items are coin-flip outcomes, so the gap is noise, not failure.

### Important caveats (read before citing these numbers)

This experiment validates the feedback loop under idealized conditions.
It does NOT yet prove the core hypothesis in the real world.

1. **Ground truth is hand-written.** far-ok items always succeed,
   near-fail items always fail. The experiment shows the policy can
   learn a pattern that was deliberately planted — it does not show
   that historical feedback is useful when the pattern is unknown.

2. **No noise in outcomes.** Real task outcomes are noisy: an Agent
   may fail for reasons unrelated to the retrieved memory, succeed by
   luck, or receive ambiguous user feedback. Under noisy feedback the
   utility signal degrades and alpha updates become less reliable.

3. **No sparsity.** Every retrieved item gets an immediate, clean
   success/failure label. Real deployments have sparse feedback — many
   memories are never reused, and outcomes arrive late or not at all.

4. **Baseline is 0.00 by construction.** The query points directly at
   the near-fail cluster, so relevance-only retrieval is guaranteed to
   fail. A more realistic setup would give baseline a non-trivial
   success rate to beat.

5. **Single scenario.** 10 items in 2D, one query direction, one
   memory distribution. Different distributions (e.g., utility
   correlated with similarity, or anti-correlated) may change results.

## 2026-10-07 (Issue #1 Phase A/B/C)

Locked config: 500 tasks, K=3, seeds 7/11/19/23/42, alpha0=0.5, step=0.05, cap=2.0.
No retune after results. Full table: experiments/results/stage1_issue1.md.

Phase A mean: baseline success 0.0992, adaptive 0.9992. Seed 23 baseline is 0.496 because a neutral outranked near-fail; the other four baseline seeds are 0.00.

Phase B: adaptive success stays about 0.999 through 20% noise and drops to 0.9872 at 30%. Seed 11 at 30% is 0.936. Waste rises slightly.

Phase C: adaptive success stays about 0.999 down to 10% feedback. Waste rises from 0.0015 to 0.0115. Missing feedback does not write a label.

Limitation: alpha hits the cap inside the first 50 tasks, so this control cannot show a later robustness cliff. Do not start cold-start or distribution-shift until review.
