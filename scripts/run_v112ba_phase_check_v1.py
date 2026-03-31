from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112ba_phase_check_v1 import (
    V112BAPhaseCheckAnalyzer,
    load_json_report,
    write_v112ba_phase_check_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BA phase check.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112BAPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        replacement_review_payload=load_json_report(Path(config["paths"]["replacement_review_report"])),
    )
    output_path = write_v112ba_phase_check_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BA phase check report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
