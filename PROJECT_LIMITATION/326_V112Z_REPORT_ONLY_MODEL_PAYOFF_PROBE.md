# V1.12Z Report-Only Model Payoff Probe

## 目的

在 `V1.12Z` 真正进入 reconstruction pass 之前，先用当前 frozen optical-link pilot 做一轮：

- 同一数据集
- 同一时间切分
- 同一正样本定义

下的**收益/回撤质量探针**。

这不是实盘回测，也不是正式训练放开。  
它的作用只是：

1. 先看当前 guardrail baseline 和黑箱模型在收益质量上谁更强。
2. 判断黑箱是否真的更接近“吃透周期”，而不只是分类分数更高。
3. 为后续 reconstruction / labeling / residual memo 提供一个更像交易的对照面。

## 模型设置

当前比较的 3 个模型：

- `guardrail_nearest_centroid_v2`
- `hist_gradient_boosting_classifier_v2`
- `small_mlp_classifier_v2`

全部使用：

- 同一 frozen pilot dataset
- 同一 time split
- 同一正样本定义：`carry_constructive`

## 指标层

每个模型都给两套读数：

1. `conditional_carry_payoff`
   - 所有被判成 `carry_constructive` 的测试样本

2. `non_overlap_trade_probe`
   - 更像交易的探针
   - 对同一 symbol 使用 `20` 日 holding cooldown
   - 避免单 symbol 日频样本完全重叠

这第二套更值得看，但仍然只是 bounded approximation，不等于正式交易回测。

