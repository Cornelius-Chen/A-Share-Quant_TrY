# A-Share Quant Decision Log

## 目的

本文件记录关键设计决策，保证未来可以追溯“为什么这样做”。

---

## 记录规则

需要记录的决策包括但不限于：

1. 协议升级
2. 研究方向切换
3. 数据口径调整
4. 指标定义变更
5. 回测引擎核心行为变更
6. 策略晋级或淘汰

---

## 模板

### DEC-0001

- Date:
- Title:
- Status: proposed / accepted / superseded / rejected
- Related Protocol Version:
- Related Runs:
- Context:
- Decision:
- Alternatives Considered:
- Expected Benefits:
- Risks:
- Follow-up Actions:

---

## Entries

### DEC-0001

- Date: 2026-03-28
- Title: Establish lab-stage governance baseline before code implementation
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: Existing repo only had charter, protocol, constitution, execution process, and risk limits. The project target is engineering-grade profitability, not a one-off backtest repo.
- Decision: Add governance, roadmap, research direction, experiment, evolution, data, metrics, validation, promotion, lifecycle, postmortem, repository architecture, and future ML policy documents before substantial code implementation.
- Alternatives Considered: Start coding the backtest skeleton immediately and add governance later.
- Expected Benefits: Reduce methodological drift, create durable research assets, and make later implementation choices auditable.
- Risks: Slightly slower initial coding start.
- Follow-up Actions: Use the new document set as the baseline for repository architecture and implementation sequencing.
