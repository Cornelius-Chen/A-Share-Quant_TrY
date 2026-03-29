from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.damage_transition_analysis import (
    DamageTransitionAnalyzer,
    load_json_report,
    write_damage_transition_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze when repeated symbol path shifts become real trade damage.")
    parser.add_argument(
        "--config",
        default="config/theme_damage_transition_analysis_v1.yaml",
        help="Path to the damage-transition analysis YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    case_payloads = []
    for case in config["analysis"]["cases"]:
        case_payloads.append(
            {
                "symbol": str(case["symbol"]),
                "timeline_payload": load_json_report(Path(case["timeline_report"])),
                "path_payload": load_json_report(Path(case["path_report"])),
            }
        )
    result = DamageTransitionAnalyzer().analyze(case_payloads=case_payloads)
    report_path = write_damage_transition_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Damage transition report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
