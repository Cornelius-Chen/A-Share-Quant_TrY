from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113i_board_level_owner_labeling_protocol_v1 import (
    V113IBoardLevelOwnerLabelingProtocolAnalyzer,
    load_json_report,
    write_v113i_board_level_owner_labeling_protocol_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13I board-level owner labeling protocol.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V113IBoardLevelOwnerLabelingProtocolAnalyzer()
    result = analyzer.analyze(
        v113h_payload=load_json_report(Path(config["paths"]["v113h_phase_charter_report"])),
        owner_board_level_only=bool(config["inputs"]["owner_board_level_only"]),
    )
    output_path = write_v113i_board_level_owner_labeling_protocol_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13I board-level owner labeling protocol report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
