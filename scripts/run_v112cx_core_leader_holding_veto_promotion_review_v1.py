from __future__ import annotations

from pathlib import Path

import yaml

from a_share_quant.strategy.v112cx_core_leader_holding_veto_promotion_review_v1 import (
    V112CXCoreLeaderHoldingVetoPromotionReviewAnalyzer,
    load_json_report,
    write_v112cx_core_leader_holding_veto_promotion_review_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "config" / "v112cx_core_leader_holding_veto_promotion_review_v1.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    analyzer = V112CXCoreLeaderHoldingVetoPromotionReviewAnalyzer()
    result = analyzer.analyze(
        cn_payload=load_json_report(repo_root / config["cn_report_path"]),
        cw_payload=load_json_report(repo_root / config["cw_report_path"]),
        cs_payload=load_json_report(repo_root / config["cs_report_path"]),
    )
    output_path = write_v112cx_core_leader_holding_veto_promotion_review_report(
        reports_dir=repo_root / config["reports_dir"],
        report_name=config["report_name"],
        result=result,
    )
    print(f"V1.12CX core leader holding veto promotion review report: {output_path.relative_to(repo_root)}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
