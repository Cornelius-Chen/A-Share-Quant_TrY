from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v18a_phase_charter_v1 import (
    V18APhaseCharterAnalyzer,
    load_json_report,
    write_v18a_phase_charter_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V1.8A phase charter.")
    parser.add_argument(
        "--config",
        default="config/v18a_phase_charter_v1.yaml",
        help="Path to the V1.8A phase charter config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V18APhaseCharterAnalyzer().analyze(
        v17_phase_closure_payload=load_json_report(Path(config["paths"]["v17_phase_closure_report"])),
        v17_feature_promotion_gap_review_payload=load_json_report(
            Path(config["paths"]["v17_feature_promotion_gap_review_report"])
        ),
    )
    output_path = write_v18a_phase_charter_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.8A phase charter report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
