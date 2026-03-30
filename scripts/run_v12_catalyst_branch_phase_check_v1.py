from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_catalyst_branch_phase_check_v1 import (
    V12CatalystBranchPhaseCheckAnalyzer,
    load_json_report,
    write_v12_catalyst_branch_phase_check_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether the bounded catalyst branch changes the current V1.2 phase posture."
    )
    parser.add_argument(
        "--config",
        default="config/v12_catalyst_branch_phase_check_v1.yaml",
        help="Path to the catalyst branch phase check YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12CatalystBranchPhaseCheckAnalyzer().analyze(
        catalyst_audit_payload=load_json_report(Path(config["paths"]["catalyst_audit_report"])),
        bottleneck_check_payload=load_json_report(Path(config["paths"]["bottleneck_check_report"])),
    )
    output_path = write_v12_catalyst_branch_phase_check_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V12 catalyst branch phase check report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
