from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112cg_packaging_refined_action_mapping_pilot_v1 import (
    V112CGPackagingRefinedActionMappingPilotAnalyzer,
    load_json_report,
    write_v112cg_packaging_refined_action_mapping_pilot_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12CG packaging refined action mapping pilot.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    analyzer = V112CGPackagingRefinedActionMappingPilotAnalyzer()
    result = analyzer.analyze(
        cd_payload=load_json_report(Path(config["paths"]["cd_report"])),
        cf_payload=load_json_report(Path(config["paths"]["cf_report"])),
    )
    output_path = write_v112cg_packaging_refined_action_mapping_pilot_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12CG packaging refined pilot report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
