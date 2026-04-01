from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113j_board_research_world_model_protocol_v1 import (
    V113JBoardResearchWorldModelProtocolAnalyzer,
    load_json_report,
    write_v113j_board_research_world_model_protocol_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13J board research world-model protocol.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V113JBoardResearchWorldModelProtocolAnalyzer()
    result = analyzer.analyze(
        v113i_payload=load_json_report(Path(config["paths"]["v113i_report"])),
        world_model_teaching_approved=bool(config["inputs"]["world_model_teaching_approved"]),
    )
    output_path = write_v113j_board_research_world_model_protocol_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13J board research world-model protocol report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
