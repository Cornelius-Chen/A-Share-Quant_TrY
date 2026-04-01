from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113p_cpo_full_board_coverage_and_t1_audit_v1 import (
    V113PCPOFullBoardCoverageAndT1AuditAnalyzer,
    load_json_report,
    write_v113p_cpo_full_board_coverage_and_t1_audit_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113PCPOFullBoardCoverageAndT1AuditAnalyzer()
    result = analyzer.analyze(
        repo_root=repo_root,
        v112aa_payload=load_json_report(repo_root / "reports" / "analysis" / "v112aa_cpo_bounded_cohort_map_v1.json"),
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113o_payload=load_json_report(repo_root / "reports" / "analysis" / "v113o_cpo_time_ordered_market_replay_prototype_v1.json"),
    )
    output_path = write_v113p_cpo_full_board_coverage_and_t1_audit_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v113p_cpo_full_board_coverage_and_t1_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
