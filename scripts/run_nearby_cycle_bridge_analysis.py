from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.nearby_cycle_bridge_analysis import (
    NearbyCycleBridgeAnalyzer,
    load_cycle_delta_report,
    load_timeline_report,
    write_nearby_cycle_bridge_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bridge incumbent-only cycles to nearby challenger cycles.")
    parser.add_argument(
        "--config",
        default="config/baseline_q3_nearby_cycle_bridge_600519_v1.yaml",
        help="Path to the nearby-cycle bridge YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    cycle_delta_payload = load_cycle_delta_report(Path(config["paths"]["cycle_delta_report"]))
    timeline_payload = load_timeline_report(Path(config["paths"]["timeline_report"]))
    result = NearbyCycleBridgeAnalyzer().analyze(
        cycle_delta_payload=cycle_delta_payload,
        timeline_payload=timeline_payload,
        strategy_name=str(config["analysis"]["strategy_name"]),
        incumbent_name=str(config["analysis"]["incumbent_candidate"]),
        challenger_name=str(config["analysis"]["challenger_candidate"]),
        bridge_days=int(config["analysis"].get("bridge_days", 1)),
    )
    output_path = write_nearby_cycle_bridge_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Nearby cycle bridge report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
