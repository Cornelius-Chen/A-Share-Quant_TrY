# V1.12BP CPO Selector Maturity Fusion Pilot V1

## Key Numbers

- `neutral_return_delta = -0.0563`
- `neutral_drawdown_delta = -0.1496`
- `bk_return_delta = -5.3192`
- `bk_drawdown_delta = +0.1579`
- `aggressive_return_delta = +0.6513`

## Owner-Level Interpretation

This is the first lawful fusion line where:

- selector quality is reused from the best bounded selector search
- internal maturity overlay is consumed as an actual downstream filter
- market regime remains only a helper layer

The most important conclusion is not that fusion won.

The most important conclusion is:

**internal maturity overlay helps compress BK-style risk, but current fusion still does not beat neutral selective discipline.**

That means the next bottleneck is still not raw selector strength.

It is more likely:

- gate structure
- condition decomposition
- maturity / congestion condition precision

Formal training and formal signal rights remain closed.
