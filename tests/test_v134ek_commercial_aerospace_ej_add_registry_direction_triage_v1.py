from pathlib import Path

from a_share_quant.strategy.v134ej_commercial_aerospace_intraday_add_supervision_registry_v1 import (
    V134EJCommercialAerospaceIntradayAddSupervisionRegistryV1Analyzer,
    write_report as write_registry_report,
)
from a_share_quant.strategy.v134ek_commercial_aerospace_ej_add_registry_direction_triage_v1 import (
    V134EKCommercialAerospaceEJAddRegistryDirectionTriageV1Analyzer,
)


def test_v134ek_commercial_aerospace_ej_add_registry_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    registry = V134EJCommercialAerospaceIntradayAddSupervisionRegistryV1Analyzer(repo_root).analyze()
    write_registry_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ej_commercial_aerospace_intraday_add_supervision_registry_v1",
        result=registry,
    )
    result = V134EKCommercialAerospaceEJAddRegistryDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_intraday_add_registry_bootstrap_and_shift_next_to_point_in_time_add_seed_feed"
    )
