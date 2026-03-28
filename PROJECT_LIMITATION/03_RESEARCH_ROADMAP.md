# A-Share Quant V1 Research Roadmap

## 定位

本文件定义项目在实验室阶段的研究推进顺序、阶段目标、交付物和阶段出口条件。

它回答的问题不是“最终最强策略是什么”，而是：

1. 当前应该先研究什么
2. 为什么按这个顺序推进
3. 什么结果才算当前阶段完成
4. 什么条件下允许进入下一阶段

---

## 总体原则

1. 先底座，后策略
2. 先协议，后优化
3. 先可复现，后追求复杂度
4. 先建立研究资产，再追求单次亮眼结果
5. 任何阶段都不能绕开 [02_RESEARCH_PROTOCOL.md](./02_RESEARCH_PROTOCOL.md)

---

## 当前阶段定位

当前阶段为：

**实验室阶段的工程化研究系统建设**

阶段目标：

1. 建立可运行、可复现、可审计的研究底座
2. 固化主线趋势研究协议
3. 建立标准化实验与结果记录体系
4. 为未来模拟跟踪、小规模实盘和更复杂模型预留架构接口

当前阶段不追求：

1. 立即得出最终最优策略
2. 直接接券商或实盘
3. 以回测美观为核心目标

---

## 阶段划分

### Phase 0: Governance Foundation

目标：

1. 固化项目边界
2. 固化研究协议
3. 固化数据、实验、指标、晋级、复盘标准

交付物：

1. `PROJECT_LIMITATION/` 下的治理文档全集
2. 决策日志模板
3. 研究日志模板
4. 实验注册要求

出口条件：

1. 关键边界、研究方法和升级规则已文档化
2. 任何后续代码开发都能映射到明确文档

### Phase 1: Research Backbone

目标：

1. 建立最小可运行回测底座
2. 建立统一数据加载、股票池过滤、成本和涨跌停模型
3. 建立实验注册与报告输出

优先模块：

1. `data/loaders.py`
2. `data/universe.py`
3. `backtest/engine.py`
4. `backtest/cost_model.py`
5. `backtest/limit_model.py`
6. `audit/run_registry.py`

出口条件：

1. 至少一条端到端回测主链路可以运行
2. 所有 run 都有配置、指标和输出记录
3. 回测结果可重复

### Phase 2: Regime and Mainline Detection

目标：

1. 建立上涨阶段切分
2. 建立进攻许可机制
3. 建立主线板块打分

优先模块：

1. `regime/sample_segmenter.py`
2. `regime/attack_permission_engine.py`
3. `regime/mainline_sector_scorer.py`

出口条件：

1. 至少支持三类样本切分方式
2. 主线板块打分可追踪、可解释
3. 各样本段记录完整

### Phase 3: Intra-Mainline Hierarchy and Trend Logic

目标：

1. 建立主线内部个股分层
2. 建立趋势过滤候选集
3. 建立入场候选集

优先模块：

1. `trend/leader_hierarchy_ranker.py`
2. `trend/trend_filters.py`
3. `trend/entry_rules.py`

出口条件：

1. 龙头 / 中军 / 高质量补涨 / 杂毛分层可复现
2. 趋势过滤与入场规则可统一比较

### Phase 4: Strategy Families

目标：

1. 在同一底座上实现三套主线策略
2. 确保三套策略可直接比较

优先模块：

1. `strategy/mainline_trend_a.py`
2. `strategy/mainline_trend_b.py`
3. `strategy/mainline_trend_c.py`

出口条件：

1. 三套策略共用同一底座
2. 三套策略输出相同格式报告

### Phase 5: Holding, Exit, Metrics, Reporting

目标：

1. 建立持有与退出研究框架
2. 实现核心指标和报告
3. 对不同样本分段结果做一致性分析

优先模块：

1. `trend/holding_engine.py`
2. `trend/exit_guard.py`
3. `backtest/metrics.py`
4. `backtest/report.py`

出口条件：

1. 必须实现 `mainline_capture_ratio`
2. 必须实现 `missed_mainline_count`
3. 报告能支撑策略比较与复盘

### Phase 6: Validation and Tracking

目标：

1. 进行样本外、滚动、walk-forward 验证
2. 建立研究结果的稳定性判断
3. 开始模拟跟踪准备

出口条件：

1. 候选策略满足 [11_PROMOTION_GATES.md](./11_PROMOTION_GATES.md)
2. 回测与跟踪偏差有解释框架

### Phase 7: Small-Live Readiness

目标：

1. 将风险、预交易检查和执行流程从架构预留转向可用状态
2. 准备小规模、严格受控的实盘试运行

出口条件：

1. 满足 [constitution_rules.yaml](./constitution_rules.yaml)
2. 满足 [risk_limits.yaml](./risk_limits.yaml)
3. 满足 [13_STRATEGY_LIFECYCLE.md](./13_STRATEGY_LIFECYCLE.md)

---

## 阶段内工作顺序

每个阶段内统一遵循以下顺序：

1. 明确协议版本
2. 明确候选集
3. 外置配置
4. 统一实现
5. 跑标准实验
6. 记录结果
7. 决策是否升级、保留或淘汰

---

## 阶段暂停条件

出现以下情况时，应暂停推进并先修复：

1. 数据语义不清或存在明显污染风险
2. 指标定义不一致
3. 实验记录不完整
4. 回测主链路无法稳定复现
5. 结果改善无法解释来源

---

## 一句话原则

实验室阶段最重要的不是“尽快找到最强策略”，而是建立一套可以持续逼近最强策略的工程化研究机制。
