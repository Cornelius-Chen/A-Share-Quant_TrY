from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112bt_phase_conditioned_veto_and_eligibility_extraction_v1 import (
    V112BTPhaseConditionedVetoAndEligibilityExtractionAnalyzer,
    load_json_report,
    write_v112bt_phase_conditioned_veto_and_eligibility_extraction_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BT phase-conditioned veto and eligibility extraction.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    analyzer = V112BTPhaseConditionedVetoAndEligibilityExtractionAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        bs_refinement_payload=load_json_report(Path(config["paths"]["bs_refinement_report"])),
        bp_fusion_payload=load_json_report(Path(config["paths"]["bp_fusion_report"])),
    )
    output_path = write_v112bt_phase_conditioned_veto_and_eligibility_extraction_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BT extraction report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
