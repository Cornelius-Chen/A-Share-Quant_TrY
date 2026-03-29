from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.specialist_alpha_analysis import (
    SpecialistAlphaAnalyzer,
    load_validation_report,
    write_specialist_alpha_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze slice-level specialist alpha opportunity pockets.")
    parser.add_argument(
        "--config",
        default="config/specialist_alpha_analysis_v1.yaml",
        help="Path to the specialist-alpha analysis YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    payload = load_validation_report(Path(config["paths"]["validation_report"]))
    result = SpecialistAlphaAnalyzer().analyze(
        payload=payload,
        anchors=[str(item) for item in config["analysis"]["anchors"]],
        specialists=[dict(item) for item in config["analysis"]["specialists"]],
    )
    report_path = write_specialist_alpha_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Specialist alpha report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
