from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v110a_cross_family_probe_v1 import (
    V110ACrossFamilyProbeAnalyzer,
    load_json_report,
    write_v110a_cross_family_probe_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.10A cross-family probe.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V110ACrossFamilyProbeAnalyzer()
    result = analyzer.analyze(
        probe_protocol_payload=load_json_report(Path(config["paths"]["v110a_probe_protocol_report"])),
        catalyst_seed_payload=load_json_report(Path(config["paths"]["catalyst_seed_report"])),
        screened_collection_payload=load_json_report(Path(config["paths"]["v18c_screened_collection_report"])),
    )
    output_path = write_v110a_cross_family_probe_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.10A cross-family probe report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
