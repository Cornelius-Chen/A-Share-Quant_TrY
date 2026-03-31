from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113f_pilot_object_pool_v1 import (
    V113FPilotObjectPoolAnalyzer,
    _load_csv_rows,
    load_json_report,
    write_v113f_pilot_object_pool_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13F pilot object pool.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V113FPilotObjectPoolAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v113f_phase_charter_report"])),
        pilot_protocol_payload=load_json_report(Path(config["paths"]["v113e_pilot_protocol_report"])),
        sector_mapping_rows=_load_csv_rows(Path(config["paths"]["sector_mapping_daily_csv"])),
        security_master_rows=_load_csv_rows(Path(config["paths"]["security_master_csv"])),
        mainline_window_rows=_load_csv_rows(Path(config["paths"]["mainline_windows_csv"])),
    )
    output_path = write_v113f_pilot_object_pool_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13F pilot object pool report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
