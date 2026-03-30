from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v11_continuation_readiness import (
    V11ContinuationReadinessAnalyzer,
    load_json_report,
    write_v11_continuation_readiness_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Decide whether V1.1 specialist refinement should continue or pause for a new suspect batch."
    )
    parser.add_argument("--config", required=True, help="Path to the V1.1 continuation readiness YAML.")
    args = parser.parse_args()

    config = load_yaml_config(Path(args.config))
    report_paths = dict(config["paths"]["reports"])

    analyzer = V11ContinuationReadinessAnalyzer()
    result = analyzer.analyze(
        q2_acceptance=load_json_report(Path(report_paths["q2_acceptance"])),
        q3_acceptance=load_json_report(Path(report_paths["q3_acceptance"])),
        q4_acceptance=load_json_report(Path(report_paths["q4_acceptance"])),
        context_a_acceptance=load_json_report(Path(report_paths["context_a_acceptance"])),
        context_b_report=load_json_report(Path(report_paths["context_b_report"])),
        u2_readiness=load_json_report(Path(report_paths["u2_readiness"])),
        specialist_alpha=load_json_report(Path(report_paths["specialist_alpha"])),
    )
    output_path = write_v11_continuation_readiness_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.1 continuation readiness report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
