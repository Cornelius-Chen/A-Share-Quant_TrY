from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v16_feature_stability_review_v1 import (
    V16FeatureStabilityReviewAnalyzer,
    load_json_report,
    write_v16_feature_stability_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V1.6 per-feature stability review.")
    parser.add_argument(
        "--config",
        default="config/v16_feature_stability_review_v1.yaml",
        help="Path to the V1.6 feature stability review config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V16FeatureStabilityReviewAnalyzer().analyze(
        stability_protocol_payload=load_json_report(Path(config["paths"]["stability_protocol_report"])),
        feature_admissibility_review_payload=load_json_report(
            Path(config["paths"]["feature_admissibility_review_report"])
        ),
        bounded_discrimination_payload=load_json_report(Path(config["paths"]["bounded_discrimination_report"])),
    )
    output_path = write_v16_feature_stability_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.6 feature stability review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
