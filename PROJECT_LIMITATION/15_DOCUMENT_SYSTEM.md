# A-Share Quant Document System

## 目的

本文件用于说明 `PROJECT_LIMITATION/` 内各文件的职责边界，避免文档越来越多但彼此重叠。

---

## 文档分层

### 一、边界层

负责定义项目是什么、什么不能做。

1. [01_PROJECT_CHARTER.md](./01_PROJECT_CHARTER.md)
2. [02_RESEARCH_PROTOCOL.md](./02_RESEARCH_PROTOCOL.md)
3. [constitution_rules.yaml](./constitution_rules.yaml)
4. [risk_limits.yaml](./risk_limits.yaml)
5. [EXECUTION_PROCESS.MD](./EXECUTION_PROCESS.MD)

### 二、研究治理层

负责定义按什么顺序研究、研究什么、不研究什么。

1. [03_RESEARCH_ROADMAP.md](./03_RESEARCH_ROADMAP.md)
2. [04_RESEARCH_DIRECTIONS.md](./04_RESEARCH_DIRECTIONS.md)
3. [06_PROTOCOL_EVOLUTION_POLICY.md](./06_PROTOCOL_EVOLUTION_POLICY.md)

### 三、实验治理层

负责定义实验如何留痕、如何比较、如何复盘。

1. [05_EXPERIMENT_STANDARD.md](./05_EXPERIMENT_STANDARD.md)
2. [07_DECISION_LOG.md](./07_DECISION_LOG.md)
3. [08_RESEARCH_JOURNAL.md](./08_RESEARCH_JOURNAL.md)
4. [14_POSTMORTEM_LOG.md](./14_POSTMORTEM_LOG.md)

### 四、数据与指标层

负责定义数据口径和结果解释语义。

1. [09_DATA_CONTRACT.md](./09_DATA_CONTRACT.md)
2. [10_METRICS_SPEC.md](./10_METRICS_SPEC.md)

### 五、策略晋级层

负责定义从实验室研究到验证、跟踪、实盘准备的门槛。

1. [11_PROMOTION_GATES.md](./11_PROMOTION_GATES.md)
2. [12_VALIDATION_STANDARD.md](./12_VALIDATION_STANDARD.md)
3. [13_STRATEGY_LIFECYCLE.md](./13_STRATEGY_LIFECYCLE.md)

### 六、架构与未来扩展层

负责定义代码结构与未来增强方法的接入边界。

1. [16_REPO_ARCHITECTURE_PLAN.md](./16_REPO_ARCHITECTURE_PLAN.md)
2. [17_FUTURE_ML_POLICY.md](./17_FUTURE_ML_POLICY.md)

---

## 使用顺序建议

阅读顺序建议如下：

1. `01_PROJECT_CHARTER.md`
2. `02_RESEARCH_PROTOCOL.md`
3. `03_RESEARCH_ROADMAP.md`
4. `04_RESEARCH_DIRECTIONS.md`
5. `09_DATA_CONTRACT.md`
6. `10_METRICS_SPEC.md`
7. `05_EXPERIMENT_STANDARD.md`
8. `06_PROTOCOL_EVOLUTION_POLICY.md`
9. `11_PROMOTION_GATES.md`
10. `12_VALIDATION_STANDARD.md`
11. `13_STRATEGY_LIFECYCLE.md`
12. `16_REPO_ARCHITECTURE_PLAN.md`
13. `17_FUTURE_ML_POLICY.md`
14. `07_DECISION_LOG.md`
15. `08_RESEARCH_JOURNAL.md`
16. `14_POSTMORTEM_LOG.md`

---

## 一句话原则

边界文件决定方向，治理文件决定研究质量，晋级文件决定项目能否真正走向盈利。
