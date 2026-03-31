from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112bg_cpo_oracle_vs_no_leak_gap_review_v1 import (
    V112BGCPOOracleVsNoLeakGapReviewAnalyzer,
    load_json_report,
    write_v112bg_cpo_oracle_vs_no_leak_gap_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BG oracle-vs-no-leak gap review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112BGCPOOracleVsNoLeakGapReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        oracle_benchmark_payload=load_json_report(Path(config["paths"]["oracle_benchmark_report"])),
        aggressive_pilot_payload=load_json_report(Path(config["paths"]["aggressive_pilot_report"])),
        v112bc_protocol_payload=load_json_report(Path(config["paths"]["v112bc_protocol_report"])),
    )
    output_path = write_v112bg_cpo_oracle_vs_no_leak_gap_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BG gap review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
