from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_v6_refresh_criteria_v1 import (
    V12V6RefreshCriteriaAnalyzer,
    load_json_report,
    write_v12_v6_refresh_criteria_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Freeze symbol-selection criteria before opening the v6 manifest.")
    parser.add_argument(
        "--config",
        default="config/v12_v6_refresh_criteria_v1.yaml",
        help="Path to the v12 v6 refresh criteria YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12V6RefreshCriteriaAnalyzer().analyze(
        next_refresh_entry_payload=load_json_report(Path(config["paths"]["next_refresh_entry_report"])),
        training_manifest_payload=load_json_report(Path(config["paths"]["training_manifest_report"])),
        carry_schema_payload=load_json_report(Path(config["paths"]["carry_schema_report"])),
        catalyst_phase_check_payload=load_json_report(Path(config["paths"]["catalyst_phase_check_report"])),
    )
    output_path = write_v12_v6_refresh_criteria_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V12 v6 refresh criteria report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
