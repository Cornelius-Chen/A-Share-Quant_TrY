from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112a_price_cycle_inference_v2 import (
    V112APriceCycleInferenceV2Analyzer,
    load_json_report,
    write_v112a_price_cycle_inference_v2_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12A price cycle inference v2.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112APriceCycleInferenceV2Analyzer()
    result = analyzer.analyze(
        pilot_dataset_draft_payload=load_json_report(Path(config["paths"]["v112a_pilot_dataset_draft_v1_report"])),
        inference_symbols=list(config["symbols"]["inference_symbols"]),
    )
    output_path = write_v112a_price_cycle_inference_v2_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12A price cycle inference v2 report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
