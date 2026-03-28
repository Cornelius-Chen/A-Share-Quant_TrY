# A-Share Quant Repository Architecture Plan

## 目的

本文件定义仓库在实验室阶段的目标结构和模块职责，保证后续代码实现不偏离研究治理体系。

---

## 核心原则

1. 目录结构服务研究流程，而不是相反
2. 公共底座与策略逻辑必须分离
3. 配置、数据、实验、报告、审计必须有稳定落点
4. 策略家族必须共用底层模块，不允许各写一套

---

## 目标结构

建议第一轮结构如下：

```text
a_share_quant/
|- constitution/
|- config/
|- data/
|- scripts/
|- experiments/
|  |- runs/
|- reports/
|- src/
|  |- a_share_quant/
|     |- common/
|     |- data/
|     |- regime/
|     |- trend/
|     |- strategy/
|     |- portfolio/
|     |- risk/
|     |- backtest/
|     |- audit/
|- tests/
```

---

## 模块职责

### constitution/

职责：

1. 放置项目级硬约束和机器可读规则
2. 与 `PROJECT_LIMITATION/` 的文档层保持对应关系

### config/

职责：

1. 外置实验配置
2. 存放协议版本、策略配置、数据配置、成本配置、回测配置

### data/

职责：

1. 数据输入和中间数据产物落点
2. 不在此目录放业务逻辑

### scripts/

职责：

1. 放置可复用的命令行脚本
2. 例如初始化 run、跑回测、汇总报告

### experiments/runs/

职责：

1. 保存结构化实验注册信息
2. 每次 run 都有唯一记录

### reports/

职责：

1. 保存面向人阅读的回测和验证报告

### src/a_share_quant/common/

职责：

1. 公共类型
2. 配置加载
3. 时间与路径工具
4. 共享数据结构

### src/a_share_quant/data/

职责：

1. 数据加载器
2. universe 过滤
3. 板块映射
4. 字段标准化

### src/a_share_quant/regime/

职责：

1. 样本切分
2. 进攻许可
3. 主线板块打分

### src/a_share_quant/trend/

职责：

1. 个股分层
2. 趋势过滤
3. 入场规则
4. 持有逻辑
5. 退出逻辑

### src/a_share_quant/strategy/

职责：

1. Strategy A/B/C 封装
2. 调用底层模块而不复制底层逻辑

### src/a_share_quant/portfolio/

职责：

1. 仓位、资金、订单意图层
2. 为以后接近实盘的路径预留组合管理接口

### src/a_share_quant/risk/

职责：

1. 预交易检查
2. 风险限制判断
3. 即使 V1 离线，也要预留架构位置

### src/a_share_quant/backtest/

职责：

1. 回测引擎
2. 成本模型
3. 涨跌停与不可成交模型
4. 指标计算
5. 报告生成

### src/a_share_quant/audit/

职责：

1. run 注册
2. 配置快照
3. 结果索引
4. 版本与留痕

### tests/

职责：

1. 保障底座和协议实现不回归
2. 优先覆盖数据、回测、指标、核心逻辑

---

## 依赖方向约束

建议遵循以下依赖方向：

1. `strategy -> trend/regime/portfolio/backtest`
2. `trend -> common/data`
3. `regime -> common/data`
4. `backtest -> common`
5. `audit -> common`
6. `risk -> common`

尽量避免：

1. `backtest -> strategy`
2. `data -> strategy`
3. `strategy` 之间相互依赖

---

## 第一轮实现优先级

1. `common`
2. `data`
3. `backtest`
4. `audit`
5. `regime`
6. `trend`
7. `strategy`
8. `risk`
9. `portfolio`

说明：

`risk` 和 `portfolio` 虽不是 V1 研究主线，但必须留出接口位置，避免后续架构漂移。

---

## 一句话原则

架构的目标不是“看起来完整”，而是保证研究结论可以自然演化为工程资产。
