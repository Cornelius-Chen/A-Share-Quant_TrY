from pathlib import Path

from a_share_quant.strategy.v125k_commercial_aerospace_ijk_event_control_triage_v1 import (
    V125KCommercialAerospaceIJKEventControlTriageReport,
    write_report,
)


def test_v125k_freezes_replay_as_blocked() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125KCommercialAerospaceIJKEventControlTriageReport(
        summary={"allow_first_lawful_replay_now": False},
        reviewer_rows=[],
        interpretation=[],
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="_tmp_v125k_triage_test",
        result=result,
    )
    assert output_path.exists()
    output_path.unlink()
