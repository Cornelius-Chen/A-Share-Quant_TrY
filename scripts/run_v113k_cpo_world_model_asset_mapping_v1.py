from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113k_cpo_world_model_asset_mapping_v1 import (
    V113KCPOWorldModelAssetMappingAnalyzer,
    load_json_report,
    write_v113k_cpo_world_model_asset_mapping_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13K CPO world-model asset mapping.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V113KCPOWorldModelAssetMappingAnalyzer()
    result = analyzer.analyze(
        v113j_payload=load_json_report(Path(config["paths"]["v113j_report"])),
        v112cw_payload=load_json_report(Path(config["paths"]["v112cw_report"])),
        v112cx_payload=load_json_report(Path(config["paths"]["v112cx_report"])),
        v112cs_payload=load_json_report(Path(config["paths"]["v112cs_report"])),
    )
    output_path = write_v113k_cpo_world_model_asset_mapping_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13K CPO world-model asset mapping report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
