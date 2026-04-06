from a_share_quant.strategy.v125b_commercial_aerospace_xyza_control_surface_triage_v1 import (
    V125BCommercialAerospaceXYZAControlSurfaceTriageReport,
)


def test_v125b_replay_blocked() -> None:
    result = V125BCommercialAerospaceXYZAControlSurfaceTriageReport(
        summary={"allow_first_lawful_replay_now": False},
        reviewer_rows=[],
        interpretation=[],
    )
    assert result.as_dict()["summary"]["allow_first_lawful_replay_now"] is False
