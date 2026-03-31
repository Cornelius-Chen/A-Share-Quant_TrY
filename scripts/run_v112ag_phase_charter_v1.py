from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112ag_phase_charter_v1 import (
    V112AGPhaseCharterAnalyzer,
    load_json_report,
    write_v112ag_phase_charter_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AG CPO bounded label-draft assembly phase charter.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112AGPhaseCharterAnalyzer()
    result = analyzer.analyze(
        cohort_map_payload=load_json_report(Path(config["paths"]["v112aa_cohort_map_report"])),
        labeling_review_payload=load_json_report(Path(config["paths"]["v112ab_labeling_review_report"])),
        dynamic_role_payload=load_json_report(Path(config["paths"]["v112ad_dynamic_role_report"])),
        feature_family_payload=load_json_report(Path(config["paths"]["v112af_feature_family_report"])),
    )
    output_path = write_v112ag_phase_charter_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AG phase charter report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
