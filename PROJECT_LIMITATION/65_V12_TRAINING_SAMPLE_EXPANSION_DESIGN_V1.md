# 65. V12 Training Sample Expansion Design V1

## Purpose

This design answers a narrow but important question:

**after the first bounded training pilot and its readiness check, where should
the next training samples come from?**

## Current Constraint

The branch already knows:

1. opening-led samples are no longer scarce
2. persistence-led samples are still thin
3. carry rows are still the main scarcity
4. carry rows also remain duplicated

## Key Rule

The repo must not enlarge the carry class by relabelling neighboring factor
families just because they are directionally similar.

That means:

1. `preemptive_loss_avoidance_shift` is not a direct carry substitute
2. `delayed_entry_basis_advantage` is not a direct carry substitute

Both remain useful, but only under their own bounded evaluation posture.

## Expansion Posture

### Opening-led

Current posture:

1. hold current count
2. do not chase more opening clones

### Persistence-led

Current posture:

1. expand only when new clean persistence rows appear
2. do not add mixed hold cases just to balance the class

### Carry-row-present

Current posture:

1. primary expansion target
2. expand via future refresh rows
3. do not collapse adjacent factor families into the carry class

## Why This Matters

Without this rule, the branch could cheat:

1. inflate the carry class artificially
2. make the training pilot look richer than it really is
3. weaken the meaning of the carry lane itself

This design prevents that.

## Intended Next Step

The correct next move after this design is:

1. define a bounded training-sample manifest
2. request new true carry rows and clean persistence rows
3. keep strategy-level ML and news-branch training closed until that manifest is satisfied
