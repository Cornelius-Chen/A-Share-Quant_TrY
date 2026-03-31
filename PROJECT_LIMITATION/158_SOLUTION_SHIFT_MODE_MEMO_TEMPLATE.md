# Solution Shift Mode Memo Template

## Purpose
- Use this memo only after `Solution Shift Mode` is triggered under the long-horizon autonomy policy.
- It replaces automatic micro-phase continuation.

## Allowed Memo Types
- `Data Acquisition Plan`
- `Feature Hypothesis Plan`
- `Method Change Plan`
- `Freeze Recommendation`

## Required Fields
- `memo_type`
- `current_primary_bottleneck_category`
- `why_current_path_no_longer_adds_decision_value`
- `proposed_shift`
- `how_the_shift_changes_the_decision_basis`
- `why_this_is_not_just_more_artifacts`
- `freeze_reason_if_no_viable_shift_exists`

## Hard Rules
- Choose exactly one memo type.
- Do not propose another review / re-review / probe on the same evidence pool unless the memo itself is a method or data-source change that creates a genuinely new decision basis.
- If the memo cannot identify a real change in evidence source, feature definition, or method, the correct output is `Freeze Recommendation`.

## Exploration-Layer Flexibility
- A memo may recommend:
  - a design-first output
  - a trigger-source map
  - a small acquisition plan
  - a feature-definition hypothesis
  - a time-boxed owner-led exception phase
- A memo may not:
  - bypass promotion gates
  - send report-only results into the strategy mainline
  - auto-create a chain of follow-on exploratory phases
