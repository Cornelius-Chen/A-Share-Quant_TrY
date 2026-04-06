from pathlib import Path

from a_share_quant.strategy.v134ik_commercial_aerospace_board_event_alignment_supervision_audit_v1 import (
    V134IKCommercialAerospaceBoardEventAlignmentSupervisionAuditV1Analyzer,
)


def test_v134ik_board_event_alignment_supervision_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134IKCommercialAerospaceBoardEventAlignmentSupervisionAuditV1Analyzer(repo_root).analyze()

    assert report.summary["event_seed_count"] == 6
    assert report.summary["aligned_board_supportive_count"] == 1
    assert report.summary["turning_point_alignment_count"] == 1
    assert report.summary["pre_turn_watch_count"] == 1
    assert report.summary["lockout_misaligned_count"] == 2
    assert report.summary["raw_only_alignment_absent_count"] == 1
