from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer,
    load_json_report,
    write_v114a_cpo_constrained_add_reduce_policy_search_pilot_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v113z_payload=load_json_report(repo_root / "reports" / "analysis" / "v113z_constrained_add_reduce_policy_search_protocol_v1.json"),
    )
    output_path = write_v114a_cpo_constrained_add_reduce_policy_search_pilot_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114a_cpo_constrained_add_reduce_policy_search_pilot_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
