# A-Share Quant Research Journal

## 目的

本文件用于记录每次重要研究改动后的观察、结果和下一步计划。

它不是结构化 run 注册表的替代品，而是面向人的研究叙述层。

---

## 记录规则

以下情况至少应记录一条 journal：

1. 协议版本升级
2. 样本切分逻辑变化
3. 主线定义或打分逻辑变化
4. 个股分层逻辑变化
5. 趋势过滤、入场、持有、退出逻辑变化
6. 成本、滑点、涨跌停成交模型变化
7. 出现显著结果提升或退化
8. 发现严重 bug、数据污染或结论反转

---

## 模板

### JOURNAL-0001

- Date:
- Author:
- Title:
- Related Decision:
- Related Runs:
- Protocol Version:
- Hypothesis:
- What Changed:
- Expected Impact:
- Observed Result:
- Side Effects / Risks:
- Conclusion:
- Next Step:

---

## Entries

### JOURNAL-0001

- Date: 2026-03-28
- Author: Codex
- Title: Build the research governance baseline before starting the first implementation diff
- Related Decision: DEC-0001
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: The project is more likely to stay aligned with profitability goals if governance, data, experiment, and promotion rules are fixed before code grows.
- What Changed: Added roadmap, directions, experiment standard, protocol evolution policy, data contract, metrics spec, promotion gates, validation standard, strategy lifecycle, postmortem log, repository architecture plan, and future ML policy files.
- Expected Impact: Reduce drift, preserve auditability, and make future code review easier.
- Observed Result: Documentation baseline completed; no backtest result yet because implementation has not started.
- Side Effects / Risks: Initial implementation is delayed slightly in exchange for stronger long-term control.
- Conclusion: The delay is justified because the project target is engineering-grade profitability rather than a demo system.
- Next Step: Map repository architecture and code modules to the new governance set, then start building the minimal runnable backbone.
