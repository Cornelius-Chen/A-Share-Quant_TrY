from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_next_refresh_entry_v3 import (
    V12NextRefreshEntryV3Analyzer,
    load_json_report,
    write_v12_next_refresh_entry_v3_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare the next V1.2 refresh entry after v5 exhausts.")
    parser.add_argument(
        "--config",
        default="config/v12_next_refresh_entry_v3.yaml",
        help="Path to the v12 next-refresh entry v3 YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12NextRefreshEntryV3Analyzer().analyze(
        v5_exhaustion_phase_check_payload=load_json_report(Path(config["paths"]["v5_exhaustion_phase_check_report"])),
        training_manifest_payload=load_json_report(Path(config["paths"]["training_manifest_report"])),
        catalyst_phase_check_payload=load_json_report(Path(config["paths"]["catalyst_phase_check_report"])),
    )
    output_path = write_v12_next_refresh_entry_v3_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.2 next refresh entry v3: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
