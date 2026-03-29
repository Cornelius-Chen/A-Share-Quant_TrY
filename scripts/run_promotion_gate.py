from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.promotion_gate import (
    PromotionGateEvaluator,
    load_comparison_report,
    write_promotion_gate_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a promotion gate on a comparison report.")
    parser.add_argument(
        "--config",
        default="config/balanced_compromise_promotion_gate.yaml",
        help="Path to the promotion-gate YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)
    comparison_report_path = Path(config["paths"]["comparison_report"])
    payload = load_comparison_report(comparison_report_path)
    evaluator = PromotionGateEvaluator()
    result = evaluator.evaluate(
        payload=payload,
        incumbent_name=str(config["gate"]["incumbent_candidate"]),
        challenger_name=str(config["gate"]["challenger_candidate"]),
        gate_config=dict(config["gate"]),
    )
    report_path = write_promotion_gate_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
        extras={
            "comparison_report": str(comparison_report_path),
            "config_path": str(config_path),
            "protocol_version": config["project"]["protocol_version"],
        },
    )
    print(f"Promotion gate report: {report_path}")
    print(f"Gate passed: {result.passed}")
    print(f"Summary: {result.summary}")
    print("Checks:")
    for check in result.checks:
        print(check)


if __name__ == "__main__":
    main()
