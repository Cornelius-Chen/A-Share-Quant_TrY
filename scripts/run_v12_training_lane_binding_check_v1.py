from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.v12_training_lane_binding_check_v1 import (
    V12TrainingLaneBindingCheckAnalyzer,
    load_candidate_binding_check_config,
    write_v12_training_lane_binding_check_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether closed lane artifacts may bind into the bounded training sample."
    )
    parser.add_argument(
        "--config",
        default="config/v12_training_lane_binding_check_v1.yaml",
        help="Path to the lane binding check YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_payload, candidate_payloads, reports_dir, report_name = load_candidate_binding_check_config(
        Path(args.config)
    )
    result = V12TrainingLaneBindingCheckAnalyzer().analyze(
        manifest_payload=manifest_payload,
        candidate_payloads=candidate_payloads,
    )
    output_path = write_v12_training_lane_binding_check_report(
        reports_dir=reports_dir,
        report_name=report_name,
        result=result,
    )
    print(f"V12 training lane binding check report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
