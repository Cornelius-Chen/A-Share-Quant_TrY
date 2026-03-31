from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112u_cpo_foundation_readiness_review_v1 import (
    V112UCPOFoundationReadinessReviewAnalyzer,
    load_json_report,
    write_v112u_cpo_foundation_readiness_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12U CPO foundation readiness review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112UCPOFoundationReadinessReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112u_phase_charter_report"])),
        schema_payload=load_json_report(Path(config["paths"]["v112q_schema_report"])),
        adjacent_payload=load_json_report(Path(config["paths"]["v112r_adjacent_validation_report"])),
        chronology_payload=load_json_report(Path(config["paths"]["v112s_chronology_report"])),
        spillover_payload=load_json_report(Path(config["paths"]["v112t_spillover_report"])),
    )
    output_path = write_v112u_cpo_foundation_readiness_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12U readiness review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
