from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.action_state_divergence_analysis import (
    ActionStateDivergenceAnalyzer,
    load_json_report,
    write_action_state_divergence_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze action-state divergence across symbol path-shift cases.")
    parser.add_argument(
        "--config",
        default="config/theme_action_state_divergence_v1.yaml",
        help="Path to the action-state divergence YAML config.",
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
                "path_payload": load_json_report(Path(case["path_report"])),
            }
        )
    result = ActionStateDivergenceAnalyzer().analyze(case_payloads=case_payloads)
    report_path = write_action_state_divergence_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Action-state divergence report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
