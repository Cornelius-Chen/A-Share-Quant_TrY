from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114e_cpo_default_sizing_replay_promotion_v1 import (
    V114ECPODefaultSizingReplayPromotionAnalyzer,
    write_v114e_cpo_default_sizing_replay_promotion_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114ECPODefaultSizingReplayPromotionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114d_payload=load_json_report(repo_root / "reports" / "analysis" / "v114d_cpo_stable_zone_replay_injection_v1.json"),
    )
    output_path = write_v114e_cpo_default_sizing_replay_promotion_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114e_cpo_default_sizing_replay_promotion_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

