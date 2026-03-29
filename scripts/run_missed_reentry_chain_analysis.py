from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.missed_reentry_chain_analysis import (
    MissedReentryChainAnalyzer,
    load_json_report,
    write_missed_reentry_chain_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a missed re-entry to position-gap chain.")
    parser.add_argument(
        "--config",
        default="config/theme_missed_reentry_chain_300750_v1.yaml",
        help="Path to the missed re-entry chain YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    timeline_payload = load_json_report(Path(config["paths"]["timeline_report"]))
    path_payload = load_json_report(Path(config["paths"]["path_shift_report"]))
    result = MissedReentryChainAnalyzer().analyze(
        timeline_payload=timeline_payload,
        path_payload=path_payload,
        symbol=str(config["analysis"]["symbol"]),
        incumbent_name=str(config["analysis"]["incumbent_candidate"]),
        challenger_name=str(config["analysis"]["challenger_candidate"]),
        missed_buy_date=str(config["analysis"]["missed_buy_date"]),
        position_gap_date=str(config["analysis"]["position_gap_date"]),
    )
    report_path = write_missed_reentry_chain_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Missed re-entry chain report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
