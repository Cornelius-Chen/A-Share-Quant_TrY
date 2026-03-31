from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v14_context_consumption_protocol_v1 import (
    V14ContextConsumptionProtocolAnalyzer,
    load_json_report,
    write_v14_context_consumption_protocol_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V1.4 context consumption protocol freeze.")
    parser.add_argument(
        "--config",
        default="config/v14_context_consumption_protocol_v1.yaml",
        help="Path to the V1.4 context consumption protocol config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V14ContextConsumptionProtocolAnalyzer().analyze(
        v14_phase_charter_payload=load_json_report(Path(config["paths"]["v14_phase_charter_report"])),
        concept_usage_rules_payload=load_json_report(Path(config["paths"]["concept_usage_rules_report"])),
        catalyst_context_audit_payload=load_json_report(Path(config["paths"]["catalyst_context_audit_report"])),
    )
    output_path = write_v14_context_consumption_protocol_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.4 context consumption protocol report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
