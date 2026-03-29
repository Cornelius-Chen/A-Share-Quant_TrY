from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.feature_pack_b_concept_late_validation import (
    FeaturePackBConceptLateValidationAnalyzer,
    load_json_report,
    write_feature_pack_b_concept_late_validation_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate whether track B still merits more concept-to-late refinement.")
    parser.add_argument(
        "--config",
        default="config/feature_pack_b_concept_late_validation_v1.yaml",
        help="Path to the feature-pack-b concept-late validation YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    variant_payloads = [
        (
            str(item["variant_name"]),
            load_json_report(Path(item["timeline_report_path"])),
            str(item["challenger_candidate_name"]),
        )
        for item in config["variants"]
    ]
    result = FeaturePackBConceptLateValidationAnalyzer().analyze(
        bridge_payload=load_json_report(Path(config["paths"]["bridge_report_path"])),
        baseline_payload=load_json_report(Path(config["baseline"]["timeline_report_path"])),
        baseline_challenger_name=str(config["baseline"]["challenger_candidate_name"]),
        variant_payloads=variant_payloads,
    )
    report_path = write_feature_pack_b_concept_late_validation_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Feature-pack-b concept-late validation report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
