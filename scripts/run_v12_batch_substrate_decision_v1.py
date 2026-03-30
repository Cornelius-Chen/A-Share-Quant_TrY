from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_batch_substrate_decision_v1 import (
    V12BatchSubstrateDecisionAnalyzer,
    load_json_report,
    write_v12_batch_substrate_decision_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decide the next V1.2 batch/substrate posture.")
    parser.add_argument(
        "--config",
        default="config/v12_batch_substrate_decision_v1.yaml",
        help="Path to the V1.2 batch/substrate decision YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12BatchSubstrateDecisionAnalyzer().analyze(
        phase_readiness_payload=load_json_report(Path(config["paths"]["phase_readiness_report"])),
        v4_reassessment_payload=load_json_report(Path(config["paths"]["v4_reassessment_report"])),
        specialist_analysis_payload=load_json_report(Path(config["paths"]["specialist_analysis_report"])),
    )
    output_path = write_v12_batch_substrate_decision_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.2 batch/substrate decision: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
