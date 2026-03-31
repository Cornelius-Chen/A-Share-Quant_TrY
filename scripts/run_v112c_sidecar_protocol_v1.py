from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112c_sidecar_protocol_v1 import (
    V112CSidecarProtocolAnalyzer,
    load_json_report,
    write_v112c_sidecar_protocol_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12C sidecar protocol.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112CSidecarProtocolAnalyzer()
    result = analyzer.analyze(
        hotspot_review_payload=load_json_report(Path(config["paths"]["v112c_hotspot_review_report"])),
        training_protocol_payload=load_json_report(Path(config["paths"]["v112_training_protocol_report"])),
    )
    output_path = write_v112c_sidecar_protocol_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12C sidecar protocol report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
