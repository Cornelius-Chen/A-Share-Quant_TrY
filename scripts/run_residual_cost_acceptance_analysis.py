from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.residual_cost_acceptance_analysis import (
    ResidualCostAcceptanceAnalyzer,
    load_json_report,
    write_residual_cost_acceptance_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize whether the remaining blocker is acceptable as residual cost.")
    parser.add_argument(
        "--config",
        default="config/residual_cost_acceptance_v1.yaml",
        help="Path to the residual-cost acceptance YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = ResidualCostAcceptanceAnalyzer().analyze(
        gate_payload=load_json_report(Path(config["paths"]["gate_report"])),
        drawdown_gap_payload=load_json_report(Path(config["paths"]["drawdown_gap_report"])),
        chain_payload=load_json_report(Path(config["paths"]["chain_report"])),
        relief_gate_payload=load_json_report(Path(config["paths"]["relief_gate_report"])),
    )
    report_path = write_residual_cost_acceptance_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Residual-cost acceptance report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
