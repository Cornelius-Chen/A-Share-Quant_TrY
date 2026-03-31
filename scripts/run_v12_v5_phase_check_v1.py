from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_v5_phase_check_v1 import (
    V12V5PhaseCheckAnalyzer,
    load_json_report,
    write_v12_v5_phase_check_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether v5 should open a second bounded lane.")
    parser.add_argument(
        "--config",
        default="config/v12_v5_phase_check_v1.yaml",
        help="Path to the v5 phase-check YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12V5PhaseCheckAnalyzer().analyze(
        manifest_payload=load_json_report(Path(config["paths"]["manifest_report"])),
        training_manifest_payload=load_json_report(Path(config["paths"]["training_manifest_report"])),
        first_lane_payload=load_json_report(Path(config["paths"]["first_lane_report"])),
        divergence_payload=load_json_report(Path(config["paths"]["divergence_report"])),
    )
    output_path = write_v12_v5_phase_check_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V12 v5 phase-check report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
