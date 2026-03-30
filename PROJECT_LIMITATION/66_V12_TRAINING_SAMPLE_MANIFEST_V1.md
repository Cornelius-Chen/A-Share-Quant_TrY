# 66. V12 Training Sample Manifest V1

## Purpose

After the expansion-design step, the repo still needs one more narrow artifact:

**what exactly should the next bounded training branch request?**

This manifest answers that question.

## Manifest Logic

The branch now freezes three training-class postures:

1. `opening_led`
2. `persistence_led`
3. `carry_row_present`

The key point is that the manifest is not a search list for any more rows.
It is a bounded request list tied to the already accepted class design.

## Frozen Counts

### Opening-led

Current posture:

1. freeze the current count
2. request zero additional rows
3. reject new opening clones as a reason to keep training moving

### Persistence-led

Current posture:

1. request only clean persistence rows
2. do not use mixed hold examples
3. treat persistence as a secondary but still real expansion need

### Carry-row-present

Current posture:

1. request additional true carry rows
2. treat carry as the primary expansion target
3. reject relabelling from penalty-track or deferred basis examples

## Why This Matters

The previous design said the branch should not cheat.

This manifest makes that operational by freezing:

1. the class counts that should stay flat
2. the class counts that should expand
3. the allowed and forbidden sources for that expansion

## Intended Next Step

The next step after this manifest is not a larger model.

It is:

1. bind future refresh work to this manifest
2. collect new true carry rows
3. collect new clean persistence rows
4. reopen bounded model work only after those rows exist
