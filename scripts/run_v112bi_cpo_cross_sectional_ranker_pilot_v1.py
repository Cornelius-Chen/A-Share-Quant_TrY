from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112bi_cpo_cross_sectional_ranker_pilot_v1 import (
    V112BICPOCrossSectionalRankerPilotAnalyzer,
    load_json_report,
    write_v112bi_cpo_cross_sectional_ranker_pilot_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BI CPO cross-sectional ranker pilot.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112BICPOCrossSectionalRankerPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        oracle_benchmark_payload=load_json_report(Path(config["paths"]["oracle_benchmark_report"])),
        aggressive_pilot_payload=load_json_report(Path(config["paths"]["aggressive_pilot_report"])),
        neutral_pilot_payload=load_json_report(Path(config["paths"]["neutral_pilot_report"])),
        training_layer_payload=load_json_report(Path(config["paths"]["training_layer_report"])),
        cycle_reconstruction_payload=load_json_report(Path(config["paths"]["cycle_reconstruction_report"])),
    )
    output_path = write_v112bi_cpo_cross_sectional_ranker_pilot_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BI ranker pilot report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
