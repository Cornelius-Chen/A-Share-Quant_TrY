from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v18a_phase_closure_check_v1 import (
    V18APhaseClosureCheckAnalyzer,
    load_json_report,
    write_v18a_phase_closure_check_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V1.8A phase closure check.")
    parser.add_argument(
        "--config",
        default="config/v18a_phase_closure_check_v1.yaml",
        help="Path to the V1.8A phase closure check config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V18APhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v18a_phase_charter_report"])),
        breadth_entry_design_payload=load_json_report(
            Path(config["paths"]["v18a_breadth_entry_design_report"])
        ),
        phase_check_payload=load_json_report(Path(config["paths"]["v18a_phase_check_report"])),
    )
    output_path = write_v18a_phase_closure_check_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.8A phase closure check report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
