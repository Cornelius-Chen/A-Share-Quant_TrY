from a_share_quant.strategy.v124u_commercial_aerospace_rst_triage_v1 import (
    V124UCommercialAerospaceRSTTriageReport,
)


def test_v124u_status_blocked_before_core_thinning() -> None:
    result = V124UCommercialAerospaceRSTTriageReport(
        summary={"allow_control_extraction_now": False},
        reviewer_rows=[],
        interpretation=[],
    )
    assert result.as_dict()["summary"]["allow_control_extraction_now"] is False
