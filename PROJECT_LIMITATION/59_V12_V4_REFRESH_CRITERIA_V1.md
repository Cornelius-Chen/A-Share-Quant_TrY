# 59. V1.2 V4 Refresh Criteria V1

## Purpose

This file freezes symbol-selection criteria for the next `V1.2` refresh before
any `v4` manifest is written.

The goal is:

1. keep `V1.2` on the carry-row-diversity track
2. prevent drift into generic sample growth
3. prevent drift into pure capture-opening expansion

## Inputs

This criteria layer reads:

1. [v12_next_refresh_entry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_next_refresh_entry_v1.json)
2. [v12_next_refresh_factor_diversity_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_next_refresh_factor_diversity_design_v1.json)
3. [carry_observable_schema_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_observable_schema_v1.json)
4. [carry_factor_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_pilot_v1.json)

## Current Artifact

The criteria artifact is:

- [v12_v4_refresh_criteria_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_v4_refresh_criteria_v1.json)

## Current Read

The current criteria layer freezes six rules.

### Inclusion

1. each symbol must target exactly one primary row-diversity gap
2. each symbol must be observable under the bounded carry schema
3. the batch must plausibly increase future carry-score dispersion
4. symbols must be new versus the combined reference base

### Exclusion

1. exclude pure opening-led clones as the primary admission reason
2. exclude generic sample-growth additions

## What This Means

`V1.2` can now move forward to a `v4` manifest without losing the current
factorization discipline.

But this file also means:

1. the next manifest must follow these criteria
2. replay stays closed while the manifest is being drafted
3. `v4` should still be read as a carry-row-diversity refresh first

## Immediate Next Step

The next step after this criteria freeze is:

1. draft `market_research_v4_carry_row_diversity_refresh` manifest entries
2. map each proposed symbol to one primary row-diversity target
3. reject any candidate that only adds another opening-led clone
