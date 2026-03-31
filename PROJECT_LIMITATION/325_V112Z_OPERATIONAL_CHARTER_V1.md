# V1.12Z Operational Charter V1

## 冻结结果

正式 report：

- `reports/analysis/v112z_operational_charter_v1.json`

当前冻结的关键结论有：

1. `cycle absorption` 是当前第一目标  
   不是先追求漂亮的 explainable factor list。

2. `hist_gradient_boosting_classifier` 是当前最合适的黑箱主力  
   原因是：
   - 已在同数据集 sidecar 对照中胜出
   - 适合 tabular 异质特征
   - 计算开销足够低，支持多轮 bounded rerun

3. 白箱层的角色被正式定义成：
   - `guardrail`
   - `audit baseline`
   而不是主力预测器

4. `owner-facing narrative reconstruction` 被写成硬要求  
   也就是：
   - 如果最后不能把周期用语言讲清楚
   - 那就不算真正吃透

5. formal training 仍然关闭  
   当前这版 charter 只为 reconstruction 和后续 bounded labeling / benchmark 做准备。

## 三层结构

### 1. 周期重建层

要完成：

- stage ordering
- catalyst ordering
- core / adjacent / branch role transitions
- board chronology overlays
- spillover / weak-memory overlays

### 2. 黑箱吸收层

当前建议的模型分层：

- 主力黑箱：
  - `HistGradientBoosting / GBDT family`
- 次级黑箱：
  - `small MLP`
- 暂缓：
  - `TCN / Transformer / deeper sequence families`

### 3. 翻译验收层

任何黑箱发现都必须回答：

- 它出现在哪个阶段
- 对应什么角色或结构变化
- 它更像催化、扩散、承接还是退潮信号
- 为什么不是后验幻觉

## 无泄漏规则

当前 charter 明确冻结：

- 只允许时间切分
- 所有催化与事件必须按 point-in-time 可见性挂接
- 不允许用完整周期后验去回填前期特征
- mixed-role / spillover / pending rows 必须显式保留
- 黑箱不能自动宣布真值、label、feature promotion

## 当前最自然的下一步

`V1.12Z` 现在已经不缺目标定义，缺的是执行：

**直接跑 `bounded cycle reconstruction pass`。**

