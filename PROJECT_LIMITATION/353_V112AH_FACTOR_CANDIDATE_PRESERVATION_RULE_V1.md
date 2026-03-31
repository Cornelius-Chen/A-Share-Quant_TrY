# V1.12AH Factor Candidate Preservation Rule V1

## What Must Be Preserved
- `design_ready_review_candidate`
- `speculative_family_member`
- `overlay_only_candidate`
- `suppressed_duplicate` as shadow alias
- `preserved_blind_spot`
- `pending_ambiguous_candidate`

## What Counts As A Legitimate Drop Reason
- explicit leakage
- exact duplicate with explicit stronger owner mapping
- point-in-time impossibility
- repeated zero-value confirmation across later bounded experiments

## What Does Not Count As A Legitimate Drop Reason
- "too noisy for now"
- "not neat enough"
- "not promotable yet"
- "hard to explain today"

## Why This Matters
- some A-share specific factors may first appear as spillover, board-follow, name-bonus, or noisy adjacent structures
- over-cleaning can destroy the very mechanisms later experiments are supposed to discover
