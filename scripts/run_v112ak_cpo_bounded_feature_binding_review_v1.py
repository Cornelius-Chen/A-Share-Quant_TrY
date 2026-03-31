from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112ak_cpo_bounded_feature_binding_review_v1 import (
    V112AKCPOBoundedFeatureBindingReviewAnalyzer,
    load_json_report,
    write_v112ak_cpo_bounded_feature_binding_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AK feature binding review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112AKCPOBoundedFeatureBindingReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112ak_phase_charter_report"])),
        dataset_assembly_payload=load_json_report(Path(config["paths"]["v112aj_dataset_report"])),
        label_draft_payload=load_json_report(Path(config["paths"]["v112ag_label_draft_report"])),
    )
    output_path = write_v112ak_cpo_bounded_feature_binding_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AK feature binding review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
