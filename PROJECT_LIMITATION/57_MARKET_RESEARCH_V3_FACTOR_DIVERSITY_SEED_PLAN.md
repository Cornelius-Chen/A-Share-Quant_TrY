# 57. Market Research v3 Factor Diversity Seed Plan

## Purpose

This file defines the next refresh seed after `market_research_v2_refresh`.

It is not a generic market expansion pack.

Its job is to add **factor-row diversity** for the first bounded
`carry_in_basis_advantage` lane inside `V1.2`.

## Why This Seed Exists

The first carry factor cycle has already progressed through:

1. registry admission
2. factor-evaluation protocol
3. bounded first pass
4. row-isolated design
5. observable schema
6. scoring design
7. report-only pilot

The current bottleneck is no longer lane admission.

The bottleneck is that the current carry evidence still comes from only two
fully isomorphic rows.

## Design Rule

`market_research_v3_factor_diversity_seed` should:

1. add only new symbols versus the combined `v1 + v2_seed + v2_refresh` base
2. expand for carry-row diversity rather than general sample size
3. cover all four current diversity targets before bootstrap
4. remain liquid and interpretable enough for bounded follow-up analysis

## Diversity Targets

The next refresh seed is designed around four target gaps:

1. `basis_spread_diversity`
2. `carry_duration_diversity`
3. `exit_alignment_diversity`
4. `cross_dataset_carry_reuse`

These targets are intentionally narrower than the earlier archetype-driven
`v2_seed` and `v2_refresh` designs.

## Current Seed

The current proposed seed universe is:

1. `002049`
2. `600584`
3. `300014`
4. `600438`
5. `600050`
6. `601888`
7. `000625`
8. `603993`

This list is designed to widen carry evidence across technology, new energy,
telecom, consumer, auto, and resources contexts.

## Current Status

The manifest gate has now passed:

1. all `8` symbols are new versus the combined reference base
2. all four row-diversity targets are covered
3. the seed is now ready for free-data bootstrap

Key evidence:

- [market_research_v3_factor_diversity_seed_manifest_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_research_v3_factor_diversity_seed_manifest_v1.json)

The pack has now moved beyond manifest status:

1. free-data bootstrap completed
2. sector / concept / derived tables were rebuilt in the correct order
3. the pack now audits as `baseline_ready = true`
4. the first A/B/C suite run is complete

Additional evidence:

- [market_research_data_audit_v3_factor_diversity_seed.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v3_factor_diversity_seed.json)
- [20260330T005408Z_70e5fe8c_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260330T005408Z_70e5fe8c_comparison.json)

The first active `v3` lane has now also been narrowed enough to classify its
structure:

1. `market_research_v3_factor_diversity_seed / 2024_q4 / mainline_trend_c`
   is the first active specialist lane
2. `002049` is the current top positive driver inside that lane
3. the earliest decisive edge is a specialist-only `opening` on `2024-11-05`
4. the checked late window does not show a clean `persistence` edge
5. the correct current reading is therefore `opening-led first lane`, not
   `carry breakthrough`

Additional evidence:

- [market_v3_factor_diversity_q4_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v3_factor_diversity_q4_trade_divergence_capture_c_v1.json)
- [market_v3_factor_diversity_q4_symbol_timeline_002049_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v3_factor_diversity_q4_symbol_timeline_002049_capture_c_v1.json)
- [market_v3_factor_diversity_q4_specialist_window_opening_002049_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v3_factor_diversity_q4_specialist_window_opening_002049_v1.json)
- [market_v3_factor_diversity_q4_specialist_window_persistence_002049_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v3_factor_diversity_q4_specialist_window_persistence_002049_v1.json)

This first-lane reading has now also been checked against the wider `V1.2`
phase posture:

1. the first `v3` lane does not change the primary `V1.2` bottleneck
2. the main bottleneck still remains missing carry row diversity
3. the second `v3` lane therefore stays closed

Additional evidence:

- [market_v3_q4_first_lane_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v3_q4_first_lane_acceptance_v1.json)
- [v12_bottleneck_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_bottleneck_check_v1.json)

## Success Condition

This step should be treated as successful when:

1. the manifest contains only new symbols versus the combined reference base
2. all four row-diversity targets are covered
3. the seed is immediately runnable through the standard free-data bootstrap
4. the resulting manifest report is green before any bootstrap begins

## Immediate Next Step

The next step after this seed plan is:

1. compare `market_research_v3_factor_diversity_seed` against the current
   research map
2. open only the first specialist lane that can change the current carry
   row-diversity reading
3. only then decide whether the new pack adds enough carry row diversity to
   reopen the carry lane as something stronger than a report-only micro-pilot
4. keep the second `v3` lane closed until a later lane does more than repeat
   the current opening-led reading
5. keep `V1.2` on the factor-row-diversity track unless a later lane changes
   the current carry reading
