from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112cd_packaging_role_specific_action_mapping_pilot_v1 import (
    V112CDPackagingRoleSpecificActionMappingPilotAnalyzer,
    load_json_report,
    write_v112cd_packaging_role_specific_action_mapping_pilot_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12CD packaging role-specific action mapping pilot.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    analyzer = V112CDPackagingRoleSpecificActionMappingPilotAnalyzer()
    result = analyzer.analyze(
        bp_payload=load_json_report(Path(config["paths"]["bp_report"])),
        bz_payload=load_json_report(Path(config["paths"]["bz_report"])),
        bw_payload=load_json_report(Path(config["paths"]["bw_report"])),
        neutral_payload=load_json_report(Path(config["paths"]["neutral_report"])),
    )
    output_path = write_v112cd_packaging_role_specific_action_mapping_pilot_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12CD packaging action mapping pilot report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
