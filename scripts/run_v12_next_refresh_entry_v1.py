from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_next_refresh_entry_v1 import (
    V12NextRefreshEntryAnalyzer,
    load_json_report,
    write_v12_next_refresh_entry_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare the next V1.2 refresh entry after the first v3 lane closes."
    )
    parser.add_argument(
        "--config",
        default="config/v12_next_refresh_entry_v1.yaml",
        help="Path to the V1.2 next-refresh entry YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12NextRefreshEntryAnalyzer().analyze(
        bottleneck_payload=load_json_report(Path(config["paths"]["bottleneck_report"])),
        next_refresh_design_payload=load_json_report(Path(config["paths"]["next_refresh_design_report"])),
        v3_audit_payload=load_json_report(Path(config["paths"]["v3_audit_report"])),
        first_lane_acceptance_payload=load_json_report(Path(config["paths"]["first_lane_acceptance_report"])),
    )
    output_path = write_v12_next_refresh_entry_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V12 next-refresh entry report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
