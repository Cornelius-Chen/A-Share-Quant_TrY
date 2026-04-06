from pathlib import Path

from a_share_quant.strategy.v128s_commercial_aerospace_failure_library_bootstrap_v1 import (
    V128SCommercialAerospaceFailureLibraryBootstrapAnalyzer,
)


def test_v128s_commercial_aerospace_failure_library_bootstrap_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128SCommercialAerospaceFailureLibraryBootstrapAnalyzer(repo_root).analyze()

    assert result.summary["primary_variant"] == "tail_weakdrift_full"
    assert int(result.summary["failure_case_count"]) >= 1
    assert int(result.summary["intraday_collapse_override_required_count"]) >= 1

    target = next(row for row in result.failure_rows if row["failure_id"] == "20260113_601698")
    assert target["failure_type"] == "intraday_collapse_override_required"
    assert target["signal_label"] == "de_risk_target"
    assert target["pre_open_event_status"] == "no_decisive_event"

    csv_path = repo_root / result.summary["failure_library_csv"]
    assert csv_path.exists()
