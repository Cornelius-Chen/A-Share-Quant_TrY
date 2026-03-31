# V1.12Z Model Payoff Probe V1

正式 report：

- `reports/analysis/v112z_model_payoff_probe_v1.json`

## 关键结果

### 1. 我们的 guardrail baseline

- `test_accuracy = 0.4628`
- `non_overlap_trade_probe`
  - `trade_count = 27`
  - `avg_forward_return_20d = 0.2234`
  - `hit_rate = 0.7407`
  - `avg_max_drawdown_20d = -0.0975`
  - `profit_factor = 7.9942`

这说明：

- 当前白箱 guardrail 不是没用
- 它在 frozen pilot 上已经能抓到相当不错的周期段
- 但它的回撤质量和 profit factor 仍明显落后于主力黑箱

### 2. 主力黑箱 GBDT

- `test_accuracy = 0.5655`
- `non_overlap_trade_probe`
  - `trade_count = 27`
  - `avg_forward_return_20d = 0.2377`
  - `hit_rate = 0.8148`
  - `avg_max_drawdown_20d = -0.0826`
  - `profit_factor = 13.7131`

这是当前最重要的结果。

它说明在同一 frozen pilot 上：

- 黑箱不只是分类更准
- 它抓到的样本在收益质量上也更好
- 更关键的是：
  - 命中率更高
  - 平均回撤更浅
  - `profit_factor` 明显更强

所以当前 `GBDT` 确实更像“周期吸收主力”。

### 3. secondary black-box: small MLP

- `test_accuracy = 0.5744`
- `non_overlap_trade_probe`
  - `trade_count = 27`
  - `avg_forward_return_20d = 0.2391`
  - `hit_rate = 0.8889`
  - `avg_max_drawdown_20d = -0.0851`
  - `profit_factor = 13.0739`

它也很强，但当前我仍不建议把它排到 `GBDT` 前面。

原因：

- `GBDT` 更稳
- 对 tabular heterogeneous features 更自然
- 更适合当前这条线反复做 residual analysis 和 mechanism memo

所以现阶段：

**MLP 是强对照，不是主力。**

## 正确解读

这轮不能被误读成：

- 已经可以部署
- 已经可以训练放开
- 已经可以直接做信号

它真正证明的是：

**在当前 frozen optical-link pilot 上，黑箱主力已经在收益质量、回撤控制、盈亏比三个方向都显示出相对优势。**

这很重要，因为它支持了 `V1.12Z operational charter` 里的那条核心判断：

**黑箱应该作为主发现层。**

## 下一步意义

现在最值得继续做的不是立刻扩模型家族，而是：

1. 跑 `bounded cycle reconstruction pass`
2. 看 `GBDT` 比 guardrail 多抓到的到底是哪类机制
3. 把这部分机制翻译回：
   - stage
   - role
   - catalyst
   - spillover
   - chronology
   语言

也就是：

**先让黑箱继续帮我们吃透周期，再把它发现的东西反补回研究层。**

