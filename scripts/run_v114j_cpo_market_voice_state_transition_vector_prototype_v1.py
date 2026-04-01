from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114j_cpo_market_voice_state_transition_vector_prototype_v1 import (
    V114JCpoMarketVoiceStateTransitionVectorPrototypeAnalyzer,
    write_v114j_cpo_market_voice_state_transition_vector_prototype_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114JCpoMarketVoiceStateTransitionVectorPrototypeAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114h_payload=load_json_report(repo_root / "reports" / "analysis" / "v114h_cpo_promoted_sizing_behavior_audit_v1.json"),
        v114i_payload=load_json_report(repo_root / "reports" / "analysis" / "v114i_cpo_existing_info_vector_excavation_review_v1.json"),
    )
    output_path = write_v114j_cpo_market_voice_state_transition_vector_prototype_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114j_cpo_market_voice_state_transition_vector_prototype_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

