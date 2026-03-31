# V1.12AM CPO Extremely Small Core-Skeleton Training Pilot V1

## What This Pilot Tries
- learn only the current core skeleton:
  - `phase_progression_label`
  - `role_state_label`
  - `catalyst_sequence_label`
- compare:
  - `nearest_centroid_guardrail`
  - `hist_gradient_boosting_classifier`

## Why This Exists
- to avoid infinite audit before any failure exposure
- to test whether the current skeleton is learnable at all
- to keep the scope narrow enough that failure is interpretable
