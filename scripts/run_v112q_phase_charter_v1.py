from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112q_phase_charter_v1 import (
    V112QPhaseCharterAnalyzer,
    load_json_report,
    write_v112q_phase_charter_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12Q phase charter.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112QPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112p_phase_closure_payload=load_json_report(Path(config["paths"]["v112p_phase_closure_report"])),
        owner_requires_schema_hardening=bool(config["inputs"]["owner_requires_schema_hardening"]),
        owner_requires_pre_rise_window=bool(config["inputs"]["owner_requires_pre_rise_window"]),
        owner_allows_parallel_collection_drafts=bool(config["inputs"]["owner_allows_parallel_collection_drafts"]),
    )
    output_path = write_v112q_phase_charter_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12Q phase charter report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
