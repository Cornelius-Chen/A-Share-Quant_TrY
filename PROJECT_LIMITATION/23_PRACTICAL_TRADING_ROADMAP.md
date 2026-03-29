# Practical Trading Roadmap

## Purpose

This file separates:

- `research system V1`
- `practical trading readiness`

The project should not confuse "can run research and backtests well" with
"can safely trade capital."

## Current Truth

As of the current freeze state:

1. The repo is strong enough as a research and backtest platform.
2. The repo is not yet ready for automatic live trading.
3. The missing parts are no longer research governance or backtest plumbing.
4. The missing parts are execution, risk enforcement, live tracking, and operational control.

## Practical Progression

### Stage A: Research V1

Status: essentially complete

What it means:

1. Data ingestion and derived research tables exist.
2. Standardized backtest and experiment comparison exist.
3. Shared default, challengers, gates, and freeze state are explicit.

What it does not mean:

1. no broker connection
2. no live order routing
3. no real pre-trade blocking
4. no live risk enforcement

### Stage B: Execution Foundation

Goal:

Build the minimum real execution foundation without starting live trading.

Must include:

1. real `pretrade_check`
2. real `risk_engine`
3. order intent model
4. execution session state
5. broker adapter interface
6. audit fields for submitted / acknowledged / rejected / canceled orders

Minimum deliverables:

1. `signal -> pretrade_check -> risk_engine -> order_intent`
2. broker-neutral adapter contract
3. execution event log schema
4. failure-handling policy

### Stage C: Shadow Readiness

Goal:

Run the strategy in live time without sending money to market.

Must include:

1. live market data clock
2. daily signal generation in production schedule
3. shadow order generation
4. live-vs-backtest tracking
5. exception alerting
6. operator intervention path

Success condition:

1. shadow output is stable
2. tracking deviation is explainable
3. no silent failures in daily operation

### Stage D: Small-Live Readiness

Goal:

Allow tightly controlled real-money trading with tiny capital.

Must include:

1. broker connection
2. account state synchronization
3. order submission / acknowledgement / rejection handling
4. position reconciliation
5. risk-limits enforcement from `risk_limits.yaml`
6. manual kill-switch and operator override

Success condition:

1. small capital only
2. limited symbols / limited concurrent positions
3. live deviation remains inside policy range

### Stage E: Controlled Scale-Up

Goal:

Increase capital only after stable live evidence.

Must include:

1. post-trade attribution
2. live-vs-shadow-vs-backtest gap review
3. recurring postmortem discipline
4. staged capital release

## Minimum Modules Still Missing For Real Trading

These are the clearest blockers today:

1. real [pretrade_check.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/risk/pretrade_check.py)
2. real [risk_engine.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/risk/risk_engine.py)
3. broker adapter layer
4. order / execution event model
5. live scheduler
6. shadow tracking service
7. reconciliation and fail-safe controls

## Practical Readiness Rule

The repo should not be described as "tradable" until Stage C is complete.

Why:

At that point the system has at least proven it can operate in real time,
under real clocks, with real operational constraints, without yet risking money.

## One-Line Rule

`Research-ready` is not `trading-ready`; the bridge between them is execution discipline, not more backtest cleverness.
