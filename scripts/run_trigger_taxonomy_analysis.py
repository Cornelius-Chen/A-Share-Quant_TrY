from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.trigger_taxonomy_analysis import (
    TriggerTaxonomyAnalyzer,
    load_json_report,
    write_trigger_taxonomy_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify action-state trigger rows into trigger types.")
    parser.add_argument(
        "--config",
        default="config/theme_trigger_taxonomy_300750_v1.yaml",
        help="Path to the trigger-taxonomy YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    payload = load_json_report(Path(config["paths"]["source_report"]))
    result = TriggerTaxonomyAnalyzer().analyze(
        payload=payload,
        symbol=str(config["analysis"]["symbol"]),
    )
    report_path = write_trigger_taxonomy_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Trigger taxonomy report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
