from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_phase_readiness_v1 import (
    V12PhaseReadinessAnalyzer,
    load_json_report,
    write_v12_phase_readiness_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.2 phase readiness review v1.")
    parser.add_argument(
        "--config",
        default="config/v12_phase_readiness_v1.yaml",
        help="Path to the V1.2 phase readiness YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12PhaseReadinessAnalyzer().analyze(
        data_audit_payload=load_json_report(ROOT / config["inputs"]["data_audit_report"]),
        registry_payload=load_json_report(ROOT / config["inputs"]["registry_report"]),
        factorization_review_payload=load_json_report(ROOT / config["inputs"]["factorization_review_report"]),
        carry_pilot_payload=load_json_report(ROOT / config["inputs"]["carry_pilot_report"]),
    )
    output_path = write_v12_phase_readiness_report(
        reports_dir=ROOT / config["paths"]["reports_dir"],
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.2 phase readiness report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
