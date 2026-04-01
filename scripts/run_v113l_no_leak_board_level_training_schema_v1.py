from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113l_no_leak_board_level_training_schema_v1 import (
    V113LNoLeakBoardLevelTrainingSchemaAnalyzer,
    load_json_report,
    write_v113l_no_leak_board_level_training_schema_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13L no-leak board-level training schema.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V113LNoLeakBoardLevelTrainingSchemaAnalyzer()
    result = analyzer.analyze(
        v113i_payload=load_json_report(Path(config["paths"]["v113i_report"])),
        v113j_payload=load_json_report(Path(config["paths"]["v113j_report"])),
        v113k_payload=load_json_report(Path(config["paths"]["v113k_report"])),
    )
    output_path = write_v113l_no_leak_board_level_training_schema_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13L no-leak board-level training schema report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
