# CPO 数据收集与研究过程记录 V1

## 目的

这份记录不是单纯的 phase 列表，而是把 `CPO / optical-link` 这条线从**正式开启数据收集**到**进入 bounded experiment 入口**的全过程整理成可复用的方法文档。目标有三个：

1. 给论文写作提供一份可直接引用的过程底稿。
2. 解释每一步为什么要做，以及为什么当时**不能直接训练**。
3. 给后续其他板块训练提供一套尽量少绕弯子的研究顺序。

## 研究边界

- 本记录的主时间窗从 `V1.12P` 开始。
- `V1.12O` 作为前置背景保留，因为它完成了从三只锚点训练草案到 `CPO deep archetype scope` 的切换。
- 当前终点是 `V1.12Z`：
  - `bounded cycle reconstruction` 已合法开启
  - 但 actual reconstruction pass 还未执行
  - formal training 仍未打开

## 总体方法论

这条线的核心思路不是“先挑几只票训练”，而是：

1. 先把 `CPO` 从狭义 pilot 提升成完整周期研究对象。
2. 先解决**遗漏风险**，再解决**纯度问题**。
3. 先完成 registry、schema、cohort、chronology、spillover 的分层治理。
4. 对规则层拆不干净的问题，允许使用 bounded sidecar / subagent 去做候选分裂或挑战。
5. 直到剩余问题主要变成“只能在实验里暴露”，才打开 bounded experiment。

一句话概括：

**先把信息地基做成“可追查、可审阅、可保留噪音”的结构，再进入实验。**

## 阶段总览

### 前置背景：V1.12O

`V1.12O Optical-Link Deep Archetype Scope` 的作用是把 `CPO` 从旧的三票训练草案，抬升成一个深度 archetype：

- `3` 个 validated local seeds：
  - `300308`
  - `300502`
  - `300394`
- `6` 个 review-only adjacent candidates
- `8` 个 bounded study dimensions

这一步的重要意义不是扩池，而是改变研究单位：

**从“单次训练试验”切成“完整 archetype study”。**

### Step 1: V1.12P Full-Cycle Information Registry

这是 `CPO` 正式数据收集的起点。

做成的事：

- 建立了 `full-cycle information registry`
- 收了 `20` 个 cohort rows
- 建了 `6` 个信息层
- 固定了 `10` 个 source anchors
- 明确保留弱相关、映射、噪音行，不提前删除

当时解决的问题：

- 不再只看“易中天”三只核心票
- 不再只看消息或业绩单层
- 开始把：
  - 核心票
  - 补涨 / 后排
  - 延申分支
  - 弱相关 / 名字红利 / 板块跟风
  全部纳入同一个 registry

这一步为什么重要：

**研究真正怕的不是“少一条新闻”，而是漏掉一整层东西。**

### Step 2: V1.12Q Registry Schema Hardening

这一步不是继续收对象，而是先把信息结构立法。

做成的事：

- 冻结了 `6` 个周期阶段，包含 `pre_ignition_watch`
- 冻结了 `9` 个信息层
- 冻结了 `5` 个对象桶
- 冻结了 `38` 个 review-first feature slots
- 冻结了 `5` 个可并行、不会越界的 subagent 收集任务

对象桶分成：

- `A`: 核心 seeds / 龙头中军
- `B`: adjacent candidates / 补涨后排
- `C`: 产业链延申分支
- `D`: 弱相关映射 / 名字炒作 / 情绪跟风
- `E`: 指数、板块、情绪、流动性、技术路线事件

这一步解决的问题：

- 防止信息越收越多但结构越来越乱
- 防止后续“平铺堆新闻”
- 给并行收集和未来迁移提供统一挂载面

### Step 3: V1.12Q 并行收集草稿批次

这是第一次在 `CPO` 线上用 subagent / sidecar 风格的**低治理权并行收集**。

做成的事：

- 形成 `parallel_collection_draft_batch_v1`
- 收到：
  - `14` 个 adjacent / branch official anchors
  - `6` 个 chronology source anchors
  - `10` 个 future catalyst calendar anchors

这里的 subagent 工作性质是：

- `execution`
- `structuring`
- 不负责主线判断
- 不负责定义标签或 feature
- 只负责把信息先挂进 frozen schema

这一步的意义：

**subagent 不是替主线思考，而是减少遗漏和重复劳动。**

### Step 4: V1.12R Adjacent Cohort Validation

这是第一次对象池清洗。

做成的事：

- 审了 `14` 个 adjacent / branch-extension rows
- `5` 个保留成 bounded validated review assets
- `9` 个不删除，但留成：
  - `pending split`
  - `role cleanup`
  - `review-only candidate`

这一步回答的问题：

- 哪些相邻对象已经足够干净，可以正式作为研究对象引用
- 哪些其实不是信息不够，而是角色分得太粗

这一步特别重要，因为它明确立了一条原则：

**不轻易丢弃边缘对象，但也不把它们误当成干净 truth set。**

### Step 5: V1.12S Chronology Normalization

这是时间层规范化，而不是继续加事件点。

做成的事：

- 冻结了 `9` 个 chronology segments
- 冻结了 `10` 个 timing gaps
- 冻结了 `10` 个 normalized catalyst-calendar anchors

时间结构不再只是“有 OFC / GTC / 财报 / capex”。

现在能区分：

- `pre_event_watch_window`
- `event_window`
- `post_event_followthrough_window`
- `between_event_quiet_window`
- `pre_earnings_channel_check_window`
- `post_earnings_reset_window`
- `capex_to_order_conversion_window`
- `launch_to_ramp_window`
- `design_win_to_volume_window`

这一步的意义：

**把时间从“事件列表”变成“周期语法”。**

### Step 6: V1.12T Spillover Truth-Check

这是对弱相关、名字红利、板块跟风的第一轮真值审查。

做成的事：

- 审了 `3` 个 mixed-relevance spillover rows
- `0` 个被直接删除
- `2` 个保留为 `A-share spillover factor candidates`
- `1` 个保留为更弱的 `name-bonus / board-follow memory`

这一步解决的问题：

- 噪音不能直接丢
- 但也不能混进更干净的 adjacent cohort

这一步非常符合 A 股研究现实：

**噪音本身也可能是信息，但要先分层。**

### Step 7: V1.12U Foundation Readiness Review

这是 owner-level 的 readiness 判定点。

正式结论：

- `research readiness = yes`
- `formal training readiness = no`

保留的 `4` 个 material gaps：

1. unresolved adjacent role splits
2. missing daily board chronology series
3. future catalyst calendar not operationalized
4. spillover rows not factor-tested

这一步为什么重要：

因为它把“感觉差不多了”变成了正式边界：

**已经足够做 bounded deep research，但还不够放心训练。**

### Step 8: V1.12V Daily Board Chronology Operationalization

这是对 `V112U` 缺口之一的继续攻坚。

做成的事：

- 冻结了 `5` 个 daily board series
- 冻结了 `12` 个 operational columns
- 冻结了 `4` 个 source-precedence tiers

也就是说：

`daily board chronology` 不再只是一个抽象 gap，而是变成了 table spec。

### Step 9: V1.12W Future Catalyst Calendar Operationalization

这是对另一个 `V112U` gap 的继续攻坚。

做成的事：

- 冻结了 `10` 个 recurring forward-visible anchors
- 冻结了 `12` 个 operational calendar columns
- 冻结了 `4` 个 source-precedence tiers

这一步的意义：

**未来可见催化不再只是“知道有哪些会”，而是有了 recurring calendar target。**

### Step 10: V1.12X Spillover Sidecar Probe

这是第一次明确把黑箱 / sidecar 放在正确位置上。

不是让黑箱立法，而是：

**用 bounded sidecar 去探测 spillover 是否具备因子候选资格。**

结果：

- `3` 个 preserved spillover rows 全审过
- `2` 个保留为 bounded A-share spillover-factor candidates：
  - `000070`
  - `603228`
- `1` 个保留为弱 `name-bonus / board-follow memory`：
  - `001267`

这一步的重要原则：

**黑箱可以帮助拆歧义，但不能代替主线宣布真值。**

### Step 11: V1.12Y Adjacent Role-Split Sidecar Probe

这是对 unresolved adjacent rows 的 sidecar 分裂。

结果：

- 审了 `9` 个 unresolved adjacent rows
- `6` 个变成了 split-ready review assets
- `3` 个仍然保留为 still-pending mixed rows

这一步没有打开：

- training
- feature promotion
- auto signal

它只是把最大的一团结构性混杂，压成了更小的 residual ambiguity。

### Step 12: 三个 subagent challenge round

在进入实验前，专门做了一轮**反对式审查**。

目的不是让 subagent 给主线定方向，而是：

- 质疑我们是否过度清洗
- 质疑 research-ready 是否被误读成 training-ready
- 质疑剩余 ambiguity 是否还该继续 desk review

三个 challenge 的高价值质疑集中在：

1. **over-cleaning 风险**
   - mixed-role 公司可能被压得过于干净
   - spillover 可能被当污染而不是信号

2. **readiness boundary 不能混**
   - registry 完整性不等于 trainable truth
   - chronology / calendar 虽已 operationalize，但还没自动变成训练资产

3. **有些问题只能在实验里暴露**
   - residual pending rows 能否稳定归类
   - spillover candidate 到底是因子还是纯 board-follow
   - chronology / calendar 进入真实周期重建后是否真有区分力

这轮 challenge 的最重要结论不是提出 blocker，而是：

**没有新的致命 blocker。剩余高价值问题已经从 desk-cleaning 变成 experiment-type question。**

### Step 13: V1.12Z Bounded Cycle Reconstruction Entry

这一步不是已经完成重建，而是合法打开了 reconstruction 实验入口。

做成的事：

- 冻结了 `cycle reconstruction protocol`
- 明确 foundation 已足够支持 bounded reconstruction
- 明确要保留 mixed-role / spillover ambiguity
- 明确仍然不允许自动滑向 training / feature promotion / signal

所以当前真实状态是：

**CPO foundation hardening 已完成一大轮。**

接下来最自然的动作，不再是无限清洗，而是：

**执行 bounded cycle reconstruction pass。**

## Subagent 使用记录

### A. 并行收集型 subagent

用途：

- official-anchor 收集
- chronology source 收集
- future catalyst anchor 收集

特点：

- 重复性高
- 低治理权
- 只负责 draft collection，不改主线判断

### B. sidecar probe

用途：

- spillover 因子候选分层
- adjacent role-split 候选拆分

特点：

- 不是用来宣布真值
- 只用来降低结构性混杂
- 输出是 `candidate / memory / pending` 这类 bounded result

### C. challenge subagents

用途：

- 专门质疑我们是否：
  - 过度清洗
  - 过早训练
  - 误把 registry 完整度当作 trainability

特点：

- 不替主线做结论
- 只用于暴露遗漏和治理盲点

## 为什么没有直接进入训练

这条线在多个阶段都刻意没有自动训练，原因非常一致：

1. `registry complete enough for research` 不等于 `clean enough for training`
2. mixed-role / spillover / board chronology / future calendar 这些层，在训练前必须先有明确结构
3. 如果太早训练，很多 registry ambiguity 会被硬写进标签或样本里

一句话：

**训练要吃的是干净结构；当前阶段先做的是把不干净结构变成可审阅结构。**

## 对后续其他板块的可复用顺序

如果以后做别的板块，建议尽量复用这条顺序：

1. `deep archetype scope`
2. `full-cycle information registry`
3. `registry schema hardening`
4. `parallel collection draft batch`
5. `adjacent cohort validation`
6. `chronology normalization`
7. `spillover truth-check`
8. `foundation readiness review`
9. `operationalize chronology/calendar`
10. `sidecar probe for residual ambiguity`
11. `challenge round`
12. `bounded cycle reconstruction`
13. 之后才讨论 labeling / training

## 当前状态

到本记录为止，`CPO` 线的正式状态可以压成三句话：

1. `CPO foundation is now normed and sufficient for bounded deep research.`
2. `CPO foundation is not yet auto-promoted into formal training rights.`
3. `The next lawful move is bounded cycle reconstruction, not more unbounded cleaning.`

## 当前最值得记住的方法教训

1. **先控制遗漏，再控制纯度。**
2. **噪音不要急着删，先分层保存。**
3. **黑箱可以拆歧义，但不能替主线立法。**
4. **subagent 适合收集、整理、挑战，不适合治理。**
5. **当剩余问题只能在实验里暴露时，就该停止 desk-cleaning。**

