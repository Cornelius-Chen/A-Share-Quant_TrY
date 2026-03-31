# V1.12BK CPO Tree/Ranker Search

Current result:
- 3 cheap tree/ranker variants were tested on the lawful 10-row CPO layer
- best variant: `random_forest_overlay_ranker`
- best variant total return: `7.511`
- best variant max drawdown: `-0.5181`
- best variant profit factor: `4.5602`
- best variant hit rate: `0.6316`
- best variant cash ratio: `0.2759`
- neutral baseline total return: `2.2481`
- neutral baseline max drawdown: `-0.2106`
- beats neutral without materially worse drawdown: `false`

Reading:
- random forest is the best of the three cheap tree variants on return
- however, the drawdown is materially worse than neutral selective
- this means the branch is useful as a bounded model-zoo probe, but not yet a replacement for the current neutral track

