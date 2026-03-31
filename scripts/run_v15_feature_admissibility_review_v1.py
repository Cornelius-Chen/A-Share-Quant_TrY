from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v15_feature_admissibility_review_v1 import (
    V15FeatureAdmissibilityReviewAnalyzer,
    load_json_report,
    write_v15_feature_admissibility_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V1.5 per-feature admissibility review.")
    parser.add_argument(
        "--config",
        default="config/v15_feature_admissibility_review_v1.yaml",
        help="Path to the V1.5 feature admissibility review config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V15FeatureAdmissibilityReviewAnalyzer().analyze(
        candidacy_protocol_payload=load_json_report(Path(config["paths"]["candidacy_protocol_report"])),
        context_feature_schema_payload=load_json_report(Path(config["paths"]["context_feature_schema_report"])),
        bounded_discrimination_payload=load_json_report(Path(config["paths"]["bounded_discrimination_report"])),
    )
    output_path = write_v15_feature_admissibility_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.5 feature admissibility review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
