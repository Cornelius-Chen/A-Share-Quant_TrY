from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_training_sample_manifest_v1 import (
    V12TrainingSampleManifestAnalyzer,
    load_json_report,
    write_v12_training_sample_manifest_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze the next bounded training-sample manifest before any further model step."
    )
    parser.add_argument(
        "--config",
        default="config/v12_training_sample_manifest_v1.yaml",
        help="Path to the training sample manifest YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V12TrainingSampleManifestAnalyzer().analyze(
        expansion_design_payload=load_json_report(Path(config["paths"]["expansion_design_report"])),
        readiness_payload=load_json_report(Path(config["paths"]["readiness_report"])),
    )
    output_path = write_v12_training_sample_manifest_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V12 training sample manifest report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
