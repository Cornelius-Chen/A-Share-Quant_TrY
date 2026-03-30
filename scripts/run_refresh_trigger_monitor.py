from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.refresh_trigger_monitor import (
    RefreshTriggerMonitorAnalyzer,
    load_json_report,
    write_refresh_trigger_monitor_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor explicit triggers for the next post-v2 refresh.")
    parser.add_argument(
        "--config",
        default="config/refresh_trigger_monitor_v1.yaml",
        help="Path to the refresh trigger monitor YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = RefreshTriggerMonitorAnalyzer().analyze(
        next_batch_refresh_readiness=load_json_report(Path(config["paths"]["next_batch_refresh_readiness_report"])),
        v2_seed_continuation=load_json_report(Path(config["paths"]["v2_seed_continuation_report"])),
        q4_capture_acceptance=load_json_report(Path(config["paths"]["q4_capture_acceptance_report"])),
        q3_drawdown_acceptance=load_json_report(Path(config["paths"]["q3_drawdown_acceptance_report"])),
        specialist_payload=load_json_report(Path(config["paths"]["specialist_report"])),
    )
    output_path = write_refresh_trigger_monitor_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Refresh trigger monitor: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
