from pathlib import Path

from a_share_quant.strategy.v125h_commercial_aerospace_catalyst_event_registry_bootstrap_v1 import (
    V125HCommercialAerospaceCatalystEventRegistryBootstrapAnalyzer,
)


def test_v125h_builds_registry_without_fetch() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125HCommercialAerospaceCatalystEventRegistryBootstrapAnalyzer(repo_root).analyze(skip_fetch=True)
    assert result.summary["historical_source_row_count"] >= 10
    assert result.summary["forward_anchor_row_count"] == 4
