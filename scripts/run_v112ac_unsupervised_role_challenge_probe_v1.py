from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112ac_unsupervised_role_challenge_probe_v1 import (
    V112ACUnsupervisedRoleChallengeProbeAnalyzer,
    load_json_report,
    write_v112ac_unsupervised_role_challenge_probe_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AC unsupervised role-challenge probe.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112ACUnsupervisedRoleChallengeProbeAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112ac_phase_charter_report"])),
        cohort_map_payload=load_json_report(Path(config["paths"]["v112aa_cohort_map_report"])),
        labeling_review_payload=load_json_report(Path(config["paths"]["v112ab_labeling_review_report"])),
    )
    output_path = write_v112ac_unsupervised_role_challenge_probe_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AC unsupervised role-challenge probe report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
