from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112af_cpo_feature_family_design_review_v1 import (
    V112AFCPOFeatureFamilyDesignReviewAnalyzer,
    load_json_report,
    write_v112af_cpo_feature_family_design_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AF CPO feature-family design review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112AFCPOFeatureFamilyDesignReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112af_phase_charter_report"])),
        registry_schema_payload=load_json_report(Path(config["paths"]["v112q_registry_schema_report"])),
        labeling_review_payload=load_json_report(Path(config["paths"]["v112ab_labeling_review_report"])),
        dynamic_role_payload=load_json_report(Path(config["paths"]["v112ad_dynamic_role_report"])),
        brainstorm_payload=load_json_report(Path(config["paths"]["v112ae_brainstorm_report"])),
    )
    output_path = write_v112af_cpo_feature_family_design_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AF feature-family design review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
