# V1.12E GBDT Attribution Review V1

- Full GBDT result:
  - test accuracy: `0.558`
  - baseline test accuracy: `0.4509`
- Most useful block by hotspot impact:
  - `catalyst_state`
- Key ablation readout:
  - removing `catalyst_state` keeps `major_markup` false positives flat (`125 -> 125`)
  - but blows up `high_level_consolidation` false positives (`1 -> 53`)
- Reading:
  - the first sidecar gain is not generic complexity alone
  - the current hotspot control depends most on the existing catalyst-state block
  - the next useful decision is more likely feature or label refinement than immediate wider model escalation
