from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112h_candidate_substate_clustering_v1 import (
    V112HCandidateSubstateClusteringAnalyzer,
    load_json_report,
    write_v112h_candidate_substate_clustering_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12H candidate substate clustering draft.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112HCandidateSubstateClusteringAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112h_phase_charter_report"])),
        pilot_dataset_payload=load_json_report(Path(config["paths"]["v112b_pilot_dataset_freeze_report"])),
        training_protocol_payload=load_json_report(Path(config["paths"]["v112_training_protocol_report"])),
        baseline_v2_payload=load_json_report(Path(config["paths"]["v112g_baseline_readout_v2_report"])),
        gbdt_v2_payload=load_json_report(Path(config["paths"]["v112g_gbdt_pilot_v2_report"])),
    )
    output_path = write_v112h_candidate_substate_clustering_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12H candidate substate clustering report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
