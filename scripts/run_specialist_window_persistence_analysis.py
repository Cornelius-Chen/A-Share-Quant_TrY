from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.specialist_window_persistence_analysis import (
    SpecialistWindowPersistenceAnalyzer,
    load_timeline_report,
    write_specialist_window_persistence_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze when a specialist preserves a target window while anchors churn out."
    )
    parser.add_argument(
        "--config",
        default="config/theme_q1_specialist_window_persistence_000155_v1.yaml",
        help="Path to the specialist-window persistence YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    payload = load_timeline_report(Path(config["paths"]["timeline_report"]))
    result = SpecialistWindowPersistenceAnalyzer().analyze(
        payload=payload,
        strategy_name=str(config["analysis"]["strategy_name"]),
        specialist_candidate=str(config["analysis"]["specialist_candidate"]),
        anchor_candidates=[str(item) for item in config["analysis"]["anchor_candidates"]],
        window_start=str(config["analysis"]["window_start"]),
        window_end=str(config["analysis"]["window_end"]),
    )
    output_path = write_specialist_window_persistence_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Specialist window persistence report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
