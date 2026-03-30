from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.phase_status_snapshot import (
    PhaseStatusSnapshotAnalyzer,
    load_json_report,
    write_phase_status_snapshot_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a one-page phase status snapshot.")
    parser.add_argument(
        "--config",
        default="config/phase_status_snapshot_v1.yaml",
        help="Path to the phase-status snapshot YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = PhaseStatusSnapshotAnalyzer().analyze(
        v11_continuation=load_json_report(Path(config["paths"]["v11_continuation_report"])),
        v2_seed_continuation=load_json_report(Path(config["paths"]["v2_seed_continuation_report"])),
        refresh_readiness=load_json_report(Path(config["paths"]["refresh_readiness_report"])),
        trigger_monitor=load_json_report(Path(config["paths"]["trigger_monitor_report"])),
        action_plan=load_json_report(Path(config["paths"]["action_plan_report"])),
    )
    output_path = write_phase_status_snapshot_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Phase status snapshot: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
