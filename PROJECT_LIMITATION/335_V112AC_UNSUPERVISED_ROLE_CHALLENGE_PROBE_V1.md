# V1.12AC Unsupervised Role-Challenge Probe V1

## Summary
- `20` cohort rows were clustered with:
  - `10` stage-window features
  - `33` evidence-axis features
- Preferred clustering family:
  - `agglomerative_clustering`
- Result:
  - `2` supportive clusters
  - `2` challenging clusters

## What The Probe Supported
- A clean `pending quiet-window` pocket exists.
  - `300620 / 300548 / 000988`
  - This means the current decision to keep them explicit and excluded remains correct.
- A diffusion-oriented extension cluster also exists.
  - `002281 / 603083 / 688205 / 301205 / 300570`
  - This broadly supports the current `adjacent + branch-extension` reading during diffusion-led windows.

## What The Probe Challenged
- Late-cycle `late_extension` rows and `spillover` rows partially cluster together.
  - This means maturity-driven breadth and A-share spillover are not perfectly separable in data-side structure.
- Core rows and advanced-component branch rows also partially cluster together.
  - This means late high-quality branch rows may share the same markup-strength signature as core rows in some windows.

## Review-Only Candidate Structures
- `candidate_core_markup_strength_signature`
- `candidate_diffusion_extension_signature`
- `candidate_quiet_window_pending_signature`
- `candidate_late_cycle_maturity_spillover_signature`

These are not formal labels or formal roles. They are review-only candidate structures.
