from pathlib import Path

from a_share_quant.strategy.v112t_cpo_spillover_truth_check_v1 import (
    V112TCPOSpilloverTruthCheckAnalyzer,
    load_json_report,
)


def test_v112t_spillover_truth_check_preserves_review_categories() -> None:
    analyzer = V112TCPOSpilloverTruthCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112t_phase_charter_v1.json")),
        registry_payload=load_json_report(Path("reports/analysis/v112p_cpo_full_cycle_information_registry_v1.json")),
    )
    assert result.summary["reviewed_spillover_row_count"] == 3
    assert result.summary["candidate_a_share_spillover_factor_count"] == 2
    assert result.summary["pure_name_bonus_or_board_follow_count"] == 1
