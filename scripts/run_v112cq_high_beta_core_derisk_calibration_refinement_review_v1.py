from __future__ import annotations

from pathlib import Path

import yaml

from a_share_quant.strategy.v112cq_high_beta_core_derisk_calibration_refinement_review_v1 import (
    V112CQHighBetaCoreDeriskCalibrationRefinementReviewAnalyzer,
    load_json_report,
    write_v112cq_high_beta_core_derisk_calibration_refinement_review_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "config" / "v112cq_high_beta_core_derisk_calibration_refinement_review_v1.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    analyzer = V112CQHighBetaCoreDeriskCalibrationRefinementReviewAnalyzer()
    result = analyzer.analyze(
        co_payload=load_json_report(repo_root / config["co_report_path"]),
        cp_payload=load_json_report(repo_root / config["cp_report_path"]),
    )
    output_path = write_v112cq_high_beta_core_derisk_calibration_refinement_review_report(
        reports_dir=repo_root / config["reports_dir"],
        report_name=config["report_name"],
        result=result,
    )
    print(f"V1.12CQ high-beta core de-risk calibration refinement review report: {output_path.relative_to(repo_root)}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
