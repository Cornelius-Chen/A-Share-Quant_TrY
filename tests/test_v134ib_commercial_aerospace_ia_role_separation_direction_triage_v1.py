from pathlib import Path

from a_share_quant.strategy.v134ib_commercial_aerospace_ia_role_separation_direction_triage_v1 import (
    V134IBCommercialAerospaceIARoleSeparationDirectionTriageV1Analyzer,
)


def test_v134ib_role_separation_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134IBCommercialAerospaceIARoleSeparationDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["soft_candidate_count"] == 4
    directions = {row["separated_role"]: row["direction"] for row in report.triage_rows}
    assert directions["event_backed_attention_carrier_candidate"].startswith("retain_as_best_soft_role_candidate")
    assert directions["capital_true_selection"] == "continue_blocked_until_more_than_one_event_backed carrier case exists"
