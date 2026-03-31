# V1.12Z CPO Bounded Cycle Reconstruction Pass

正式 report:
- `reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json`

## 本轮在做什么

这轮不是训练，也不是信号生成。

这轮是在回答一个更基础但更关键的问题：

**我们现在这套 CPO 地基，能不能被串成一条完整、可复述、可审计、保留歧义的周期叙事。**

## 本轮冻结下来的核心结果

- `10` 个 reconstructed stage windows
- `6` 条 catalyst threads
- `11` 条 role transition rows
- `5` 条 board overlay rows
- `3` 条 spillover overlay rows
- `9` 条 residual ambiguity rows

同时仍然明确：

- `formal_training_still_forbidden = true`
- `execution_still_forbidden = true`

## 最重要的判断

### 1. 这轮 CPO 不是一段单调上涨

它更像：

1. `pre_ignition_watch`
2. `ignition`
3. 第一轮 `main_markup`
4. 第一轮 `diffusion`
5. 第一轮 `divergence_and_decay`
6. 第二轮 `re_ignition / markup`
7. `deep_reset_quiet_window`
8. 第三轮 `major_markup`
9. 晚段 `laggard_catchup`
10. 最终 `divergence_and_decay`

也就是说：

**这是一个多波段、多角色切换、多层催化叠加的周期。**

### 2. 核心三只票各自承担不同功能

- `300308`
  - 最干净的 leader anchor
- `300502`
  - 最强 high-beta core expression
- `300394`
  - upstream platform confirmation

如果没有这三种角色同时成立，周期容易被误读成：
- 纯情绪
- 纯 beta
- 或纯单股行情

### 3. 相邻 cohort 不是一锅

当前 reconstruction 给出的 reading 是：

- `603083 / 688205 / 301205`
  - 更像 high-beta module extension
- `002281`
  - 更像 domestic optics platform bridge
- `300570`
  - 更像 connector / MPO branch
- `688498 / 688313`
  - 更像 advanced component cluster
- `300757`
  - 更像 packaging / process enabler
- `601869 / 600487 / 600522`
  - 更像 late-cycle fiber-cable extension

这说明：

**“相关股”不能平铺。**
它们在周期里的作用、时点、纯度都不同。

### 4. spillover 不能删，但也不能混进 core truth

当前结论是：

- `000070 / 603228`
  - 保留为 A-share spillover factor candidates
- `001267`
  - 保留为 weak name-bonus memory

所以：

**噪音不是废物，但也不是核心事实。**

它更像：
- 阶段成熟度指示器
- 晚段情绪外溢指示器

### 5. 板块层信息是 amplifier，不是起点本身

本轮冻结的 board overlays：

- `concept_index_strength_daily`
- `cohort_breadth_daily`
- `turnover_pressure_daily`
- `cross_board_resonance_daily`
- `anchor_event_overlap_daily`

它们的正确位置不是：
- 直接替代角色判断

而是：
- 放大
- 确认
- 区分阶段成熟度

## 本轮仍然保留的 9 个歧义

分三类：

### 1. pending adjacent role split
- `300620`
- `300548`
- `000988`

### 2. board operational gaps
- board vendor selection
- breadth formula
- turnover normalization

### 3. calendar operational gaps
- expected window fill rule
- confidence tier mapping
- calendar rollforward process

这很重要，因为这轮没有为了“讲通”把歧义静默删除。

## 这轮真正证明了什么

证明的是：

**CPO 这条线现在已经足够支撑 bounded cohort map 和 bounded labeling review。**

但还没有证明：

- 可以自动训练
- 可以自动开 signal
- 可以直接部署

## 下一步

当前最合理的下一步是：

- owner review
- 然后在此基础上二选一：
  - `bounded cohort map`
  - `bounded labeling pilot`

不是直接跳到训练权开放。
