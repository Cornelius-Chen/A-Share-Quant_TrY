from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.trigger_priority_analysis import (
    TriggerPriorityAnalyzer,
    load_json_report,
    write_trigger_priority_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rank trigger families by unique-cycle damage contribution.")
    parser.add_argument(
        "--config",
        default="config/theme_trigger_priority_300750_v1.yaml",
        help="Path to the trigger-priority YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    timeline_payload = load_json_report(Path(config["paths"]["timeline_report"]))
    taxonomy_payload = load_json_report(Path(config["paths"]["taxonomy_report"]))
    result = TriggerPriorityAnalyzer().analyze(
        timeline_payload=timeline_payload,
        taxonomy_payload=taxonomy_payload,
        symbol=str(config["analysis"]["symbol"]),
        incumbent_name=str(config["analysis"]["incumbent_candidate"]),
        challenger_name=str(config["analysis"]["challenger_candidate"]),
    )
    report_path = write_trigger_priority_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Trigger priority report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
