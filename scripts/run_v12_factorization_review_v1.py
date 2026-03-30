from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_factorization_review_v1 import (
    V12FactorizationReviewAnalyzer,
    load_json_report,
    write_v12_factorization_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.2 factorization review v1.")
    parser.add_argument(
        "--config",
        default="config/v12_factorization_review_v1.yaml",
        help="Path to the V1.2 factorization review YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12FactorizationReviewAnalyzer().analyze(
        registry_payload=load_json_report(ROOT / config["inputs"]["registry_report"]),
        protocol_payload=load_json_report(ROOT / config["inputs"]["protocol_report"]),
        carry_first_pass_payload=load_json_report(ROOT / config["inputs"]["carry_first_pass_report"]),
        carry_pilot_payload=load_json_report(ROOT / config["inputs"]["carry_pilot_report"]),
    )
    output_path = write_v12_factorization_review_report(
        reports_dir=ROOT / config["paths"]["reports_dir"],
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.2 factorization review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
