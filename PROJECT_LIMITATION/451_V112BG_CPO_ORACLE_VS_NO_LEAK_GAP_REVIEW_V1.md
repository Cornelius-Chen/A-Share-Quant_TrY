# V1.12BG CPO Oracle-vs-No-Leak Gap Review V1

Current result:
- oracle trade count: `25`
- aggressive trade count: `20`
- return capture ratio: `0.002`
- drawdown penalty vs oracle: `0.3167`
- primary gap axis: `risk_control_and_stage_maturity_filtering`

Frozen recommendations:
- minimum probability margin floor: `0.1845`
- minimum confidence tier: `1.0`
- minimum rollforward state: `0.0`
- maximum turnover state: `1.0`
- minimum weighted breadth ratio: `0.45`
- minimum catalyst presence proxy: `0.35`

Interpretation:
- the remaining shortfall is not just a missing-factor problem
- the aggressive line overtrades into mature, conflicted, or low-quality windows
- the next lawful move is a cash-accepting neutral selective track
