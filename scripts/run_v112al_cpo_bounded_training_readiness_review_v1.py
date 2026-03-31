from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112al_cpo_bounded_training_readiness_review_v1 import (
    V112ALCPOBoundedTrainingReadinessReviewAnalyzer,
    load_json_report,
    write_v112al_cpo_bounded_training_readiness_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AL bounded training readiness review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112ALCPOBoundedTrainingReadinessReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112al_phase_charter_report"])),
        dataset_assembly_payload=load_json_report(Path(config["paths"]["v112aj_dataset_report"])),
        feature_binding_payload=load_json_report(Path(config["paths"]["v112ak_feature_binding_report"])),
        feature_family_payload=load_json_report(Path(config["paths"]["v112af_feature_family_report"])),
        daily_board_payload=load_json_report(Path(config["paths"]["v112v_daily_board_report"])),
        future_calendar_payload=load_json_report(Path(config["paths"]["v112w_future_calendar_report"])),
    )
    output_path = write_v112al_cpo_bounded_training_readiness_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AL training readiness review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
