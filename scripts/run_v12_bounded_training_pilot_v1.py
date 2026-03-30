from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_bounded_training_pilot_v1 import (
    V12BoundedTrainingPilotAnalyzer,
    load_json_report,
    write_v12_bounded_training_pilot_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bounded report-only training pilot on frozen lane artifacts."
    )
    parser.add_argument(
        "--config",
        default="config/v12_bounded_training_pilot_v1.yaml",
        help="Path to the bounded training pilot YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    opening_payloads = [
        (str(item["sample_id"]), load_json_report(Path(item["report_path"])))
        for item in config["inputs"]["opening_reports"]
    ]
    persistence_payloads = [
        (str(item["sample_id"]), load_json_report(Path(item["report_path"])))
        for item in config["inputs"]["persistence_reports"]
    ]
    carry_payload = load_json_report(Path(config["inputs"]["carry_report"]))
    result = V12BoundedTrainingPilotAnalyzer().analyze(
        opening_payloads=opening_payloads,
        persistence_payloads=persistence_payloads,
        carry_payload=carry_payload,
    )
    output_path = write_v12_bounded_training_pilot_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V12 bounded training pilot report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
