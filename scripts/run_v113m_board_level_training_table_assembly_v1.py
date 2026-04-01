from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113m_board_level_training_table_assembly_v1 import (
    V113MBoardLevelTrainingTableAssemblyAnalyzer,
    load_json_report,
    write_v113m_board_level_training_table_assembly_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13M board-level training table assembly.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V113MBoardLevelTrainingTableAssemblyAnalyzer()
    result = analyzer.analyze(
        v113i_payload=load_json_report(Path(config["paths"]["v113i_report"])),
        v113k_payload=load_json_report(Path(config["paths"]["v113k_report"])),
        v113l_payload=load_json_report(Path(config["paths"]["v113l_report"])),
    )
    output_path = write_v113m_board_level_training_table_assembly_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13M board-level training table assembly report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
