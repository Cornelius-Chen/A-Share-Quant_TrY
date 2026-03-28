# A-Share Quant Promotion Gates

## 目的

本文件定义策略和研究结果从一个阶段晋级到下一个阶段时必须满足的门槛。

---

## 核心原则

1. 策略不是因为“看起来不错”而晋级
2. 每次晋级都必须留下证据
3. 晋级必须同时考虑收益、稳定性、可解释性和工程可维护性

---

## 晋级阶段

1. Idea
2. Candidate
3. Baseline
4. Validation-Ready
5. Shadow-Ready
6. Small-Live-Ready

阶段定义详见 [13_STRATEGY_LIFECYCLE.md](./13_STRATEGY_LIFECYCLE.md)。

---

## Gate 1: Idea -> Candidate

必须满足：

1. 有明确假设
2. 与项目主命题相关
3. 不违反 [01_PROJECT_CHARTER.md](./01_PROJECT_CHARTER.md)
4. 已定义实验方式和评估指标

---

## Gate 2: Candidate -> Baseline

必须满足：

1. 在统一协议下完成标准回测
2. 有完整 `run_id`、配置、报告和指标
3. 相比现有 baseline 具备明确改善，或提供新研究价值
4. 改善来源可解释
5. 无明显数据污染或实现错误

---

## Gate 3: Baseline -> Validation-Ready

必须满足：

1. 在多个分段样本中表现不是单点幸运
2. 通过基本样本外检查
3. 关键指标在不同段上没有明显失真
4. 回测行为可由交易明细解释

---

## Gate 4: Validation-Ready -> Shadow-Ready

必须满足：

1. 通过 [12_VALIDATION_STANDARD.md](./12_VALIDATION_STANDARD.md)
2. 策略逻辑、数据口径和指标定义稳定
3. 运行链路具备审计留痕
4. 有明确的失效监控方案

---

## Gate 5: Shadow-Ready -> Small-Live-Ready

必须满足：

1. 满足 [constitution_rules.yaml](./constitution_rules.yaml)
2. 满足 [risk_limits.yaml](./risk_limits.yaml)
3. 有预交易检查、风险引擎和人工接管机制
4. Shadow 跟踪偏差在可解释范围内
5. 满足小资金、小规模、逐步放开的原则

---

## 禁止晋级的情形

1. 只在单一阶段或单一题材表现突出
2. 结果无法复现
3. 指标改善无法解释来源
4. 数据口径不稳定
5. 交易成本和成交约束被弱化后才好看
6. 核心逻辑依赖主观盘中判断

---

## 证据要求

每次晋级至少要附带：

1. 相关 run 列表
2. 指标对比
3. 结论说明
4. 风险项
5. 决策记录

---

## 一句话原则

晋级不是奖励，而是更高责任级别的准入。
