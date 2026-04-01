from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113v_cpo_full_board_execution_main_feed_replay_v1 import (
    V113VCPOFullBoardExecutionMainFeedReplayAnalyzer,
    load_json_report,
    write_v113v_cpo_full_board_execution_main_feed_replay_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113VCPOFullBoardExecutionMainFeedReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v112aa_payload=load_json_report(repo_root / "reports" / "analysis" / "v112aa_cpo_bounded_cohort_map_v1.json"),
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113t_payload=load_json_report(repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json"),
        v113u_payload=load_json_report(repo_root / "reports" / "analysis" / "v113u_cpo_execution_main_feed_readiness_audit_v1.json"),
    )
    output_path = write_v113v_cpo_full_board_execution_main_feed_replay_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v113v_cpo_full_board_execution_main_feed_replay_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
