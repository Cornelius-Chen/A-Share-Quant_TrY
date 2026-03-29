from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.specialist_pocket_window_analysis import (
    SpecialistPocketWindowAnalyzer,
    load_validation_report,
    write_specialist_pocket_window_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze which windows create a specialist edge inside one validation pocket."
    )
    parser.add_argument(
        "--config",
        default="config/specialist_pocket_window_analysis_v1.yaml",
        help="Path to the specialist-pocket window analysis YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    payload = load_validation_report(Path(config["paths"]["validation_report"]))
    result = SpecialistPocketWindowAnalyzer().analyze(
        payload=payload,
        dataset_name=str(config["analysis"]["dataset_name"]),
        slice_name=str(config["analysis"]["slice_name"]),
        strategy_name=str(config["analysis"]["strategy_name"]),
        specialist_candidate=str(config["analysis"]["specialist_candidate"]),
        anchor_candidates=[str(item) for item in config["analysis"]["anchor_candidates"]],
    )
    report_path = write_specialist_pocket_window_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Specialist pocket window report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
