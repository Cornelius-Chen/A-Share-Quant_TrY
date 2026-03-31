from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112v_cpo_daily_board_chronology_operationalization_v1 import (
    V112VCPODailyBoardChronologyOperationalizationAnalyzer,
    load_json_report,
    write_v112v_cpo_daily_board_chronology_operationalization_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12V CPO daily board chronology operationalization.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112VCPODailyBoardChronologyOperationalizationAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112v_phase_charter_report"])),
        schema_payload=load_json_report(Path(config["paths"]["v112q_schema_report"])),
        chronology_payload=load_json_report(Path(config["paths"]["v112s_chronology_report"])),
        draft_batch_payload=load_json_report(Path(config["paths"]["v112q_parallel_collection_batch_report"])),
    )
    output_path = write_v112v_cpo_daily_board_chronology_operationalization_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12V board chronology operationalization report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
