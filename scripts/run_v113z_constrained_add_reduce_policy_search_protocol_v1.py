from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113z_constrained_add_reduce_policy_search_protocol_v1 import (
    V113ZConstrainedAddReducePolicySearchProtocolAnalyzer,
    load_json_report,
    write_v113z_constrained_add_reduce_policy_search_protocol_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113ZConstrainedAddReducePolicySearchProtocolAnalyzer()
    result = analyzer.analyze(
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v113x_payload=load_json_report(repo_root / "reports" / "analysis" / "v113x_probability_expectancy_sizing_framework_review_v1.json"),
        v113y_payload=load_json_report(repo_root / "reports" / "analysis" / "v113y_soft_gate_add_reduce_learning_framework_review_v1.json"),
    )
    output_path = write_v113z_constrained_add_reduce_policy_search_protocol_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v113z_constrained_add_reduce_policy_search_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
