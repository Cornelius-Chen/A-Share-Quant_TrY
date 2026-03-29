from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.data.theme_data_quality import (
    ThemeDataQualityAnalyzer,
    load_theme_quality_inputs,
    write_theme_data_quality_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze theme-pack data quality.")
    parser.add_argument(
        "--config",
        default="config/theme_data_quality.yaml",
        help="Path to the theme-data-quality YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)
    inputs = load_theme_quality_inputs(
        security_master_csv=Path(config["paths"]["security_master_csv"]),
        concept_mapping_csv=Path(config["paths"]["concept_mapping_csv"]),
        sector_mapping_csv=Path(config["paths"]["sector_mapping_csv"])
        if config["paths"].get("sector_mapping_csv")
        else None,
    )
    result = ThemeDataQualityAnalyzer().analyze(**inputs)
    report_path = write_theme_data_quality_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
        extras={
            "config_path": str(config_path),
            "protocol_version": config["project"]["protocol_version"],
        },
    )
    print(f"Theme data quality report: {report_path}")
    print(f"Summary: {result.summary}")
    print(f"Warnings: {result.warnings}")


if __name__ == "__main__":
    main()
