from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v111a_screened_collection_protocol_v1 import (
    V111AScreenedCollectionProtocolAnalyzer,
    load_json_report,
    write_v111a_screened_collection_protocol_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.11A screened collection protocol.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V111AScreenedCollectionProtocolAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v111a_phase_charter_report"])),
        v111_plan_payload=load_json_report(Path(config["paths"]["v111_acquisition_infrastructure_plan_report"])),
    )
    output_path = write_v111a_screened_collection_protocol_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.11A screened collection protocol report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
