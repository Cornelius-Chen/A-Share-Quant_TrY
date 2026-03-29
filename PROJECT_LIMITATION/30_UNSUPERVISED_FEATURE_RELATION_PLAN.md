# 30. Unsupervised Feature Relation Plan

## Purpose

This file defines a **bounded unsupervised sidecar** for the research system.

It does **not** authorize unsupervised outputs to enter the trading signal
chain directly.

Its purpose is narrower:

- detect feature redundancy
- detect hidden structure among mixed / feature-limited pockets
- test whether current pockets are being flattened by weak feature expression
- provide evidence for the next feature-pack design

## Why Now

The current state after `feature-pack-b` is:

- replay queue is paused
- track A (`002902`) is closed as explanatory-but-not-promotable
- track B (`002466`) is closed as explanatory-but-not-promotable
- `feature-pack-c` is now the next mainline phase

This is exactly the point where unsupervised analysis can help:

- not by generating alpha directly
- but by telling us whether current feature geometry is too weak,
  too redundant, or too compressed

## Hard Boundaries

The unsupervised sidecar may:

- cluster pockets
- cluster feature vectors
- compute correlation / redundancy structure
- compute principal axes or other low-dimensional summaries
- suggest candidate feature groups for future packs

The unsupervised sidecar may **not**:

- emit buy / sell decisions
- override protocol metrics
- replace the family inventory
- promote or demote a strategy candidate by itself
- become a hidden signal engine

## Risk Model

The main risks are:

1. `taxonomy overfitting`
   - every pocket can be made to look structured if clustering is overused

2. `false latent structure`
   - non-stationary A-share pockets may cluster for path reasons that do not
     generalize

3. `implementation drag`
   - heavy ML tooling can destabilize the lightweight research stack

4. `signal-chain contamination`
   - unsupervised outputs may be misread as ready-made tradable features

## Mitigations

To avoid those risks, follow these rules:

1. use unsupervised analysis only as a **sidecar**
2. keep outputs report-only until a later protocol decision explicitly upgrades
   them
3. start with simple geometry:
   - correlation
   - redundancy clustering
   - PCA / axis summaries
   - pocket clustering
4. require every unsupervised result to answer one concrete question:
   - what decision boundary changed?
   - what feature pack does this justify?
5. treat "no stable latent structure found" as a valid outcome

## Implementation Constraints

Current environment note:

- `numpy` imports successfully
- `pandas` / `sklearn` transitively raise `NumPy 2.x` compatibility warnings in
  the current local environment

So the first implementation should prefer:

- pure `numpy`
- small JSON-in / JSON-out analysis tools
- no mandatory new runtime dependency for the main repo

Do **not** make the repo depend on a heavy unsupervised stack just to start
this work.

## Phase Order

### Phase U1: Lightweight Geometry

Goal:

- understand feature relation structure without changing runtime risk

Allowed methods:

- correlation matrix
- feature redundancy graph
- PCA via `numpy.linalg.svd`
- simple distance-based pocket grouping

Primary targets:

- `theme_q4 / 002902 / B`
- `theme_q2 / 002466 / C`
- family inventory feature summaries

Success signal:

- at least one current suspect pocket becomes easier to explain in terms of
  compressed or missing feature geometry

### Phase U2: Pocket Clustering

Only start if U1 yields useful structure.

Goal:

- test whether `mixed_existing_families` and `stacked_family_pocket`
  candidates naturally separate into more than one latent subgroup

Success signal:

- clustering changes the next feature-pack design

### Phase U3: Stronger Embedding (Optional)

Only start if U1 and U2 both produce high-value evidence.

This phase is optional and should not begin automatically.

## Immediate Recommendation

Right now the correct ordering is:

1. start `feature-pack-c`
2. keep unsupervised work as a report-only sidecar
3. if needed, implement only **U1 lightweight geometry**

That means:

- do not pause `feature-pack-c` for a larger ML branch
- do not introduce heavy dependencies yet
- do not treat unsupervised outputs as direct strategy features

## Exit Conditions

Stop the unsupervised sidecar early if:

- it only reproduces already-known family labels
- it does not change any feature-pack decision
- it needs heavy dependency expansion to make progress

Continue only if it clearly improves:

- feature-pack prioritization
- pocket interpretation quality
- or family/inventory boundary confidence

## U1 First Read

The first lightweight geometry run is now available:
[u1_lightweight_geometry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u1_lightweight_geometry_v1.json)

Current result:

- `case_count = 2`
- `row_count = 8`
- `active_feature_count = 11`
- `pc1_explained_variance_ratio = 0.386599`
- `case_centroid_distance = 4.080383`
- `separation_reading = cases_geometrically_separable`

Most important takeaways:

1. the two current suspect pockets are not one blended local-causal problem
2. concept-support geometry is the main separator on `pc1`
3. late-quality / resonance geometry is the main separator on `pc2`
4. the top redundancy pairs are obvious:
   - `challenger_margin_gap <-> top_score_gap`
   - `primary_concept_weight <-> concept_concentration_ratio`

So U1 has already produced a decision-changing result:

- do **not** open a blended `feature-pack-d`
- do **not** treat `002902` and `002466` as one combined next-stage pocket
- keep unsupervised work bounded unless a larger suspect set appears

This means U1 has succeeded as a sidecar. It improved interpretation quality
without touching the signal chain.

## U2 Readiness

The first U2 readiness gate is now available:
[u2_pocket_clustering_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u2_pocket_clustering_readiness_v1.json)

Current result:

- `suspect_count = 2`
- `thinning_signal = true`
- `feature_pack_c_closed = true`
- `u1_cases_geometrically_separable = true`
- `u2_ready = false`
- `recommended_next_phase = hold_u2_and_wait_for_larger_or_less_separable_suspect_set`

So the correct next move is **not** to open pocket clustering right now.

U2 should stay parked until at least one of these changes:

1. the suspect set grows materially
2. a new suspect batch is less separable than the current two-pocket split
3. a future feature-pack decision genuinely depends on latent subgrouping
