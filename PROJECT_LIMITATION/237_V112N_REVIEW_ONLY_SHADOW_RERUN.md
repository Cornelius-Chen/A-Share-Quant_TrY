# V1.12N Review-Only Shadow Rerun

- Mission: rerun the frozen pilot with the `V1.12M` inner-draft pieces turned into review-only shadow flags.
- Input basis:
  - `v112m_mixed_stall_inner_draft_v1.json`
  - `v112b_pilot_dataset_freeze_v1.json`
  - `v112g_baseline_readout_v2.json`
  - `v112g_gbdt_pilot_v2.json`
- Boundary:
  - same dataset
  - same labels
  - same split
  - no formal schema change

## Main Result

- `3` shadow features were added.
- baseline did **not** improve.
- GBDT did **not** improve.
- The phase closes as a useful negative result.
