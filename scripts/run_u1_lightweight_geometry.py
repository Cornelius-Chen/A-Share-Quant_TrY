from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.u1_lightweight_geometry import (
    U1LightweightGeometryAnalyzer,
    load_json_report,
    write_u1_lightweight_geometry_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a numpy-only U1 lightweight geometry sidecar.")
    parser.add_argument(
        "--config",
        default="config/u1_lightweight_geometry_v1.yaml",
        help="Path to the U1 lightweight geometry YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = U1LightweightGeometryAnalyzer().analyze(
        recheck_payload=load_json_report(Path(config["paths"]["recheck_report"])),
        feature_names=list(config["features"]["names"]),
    )
    report_path = write_u1_lightweight_geometry_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"U1 lightweight geometry report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
