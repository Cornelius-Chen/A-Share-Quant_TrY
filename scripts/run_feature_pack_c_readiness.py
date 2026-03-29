from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.feature_pack_c_readiness import (
    FeaturePackCReadinessAnalyzer,
    load_json_report,
    write_feature_pack_c_readiness_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize why feature-pack-b ended and define feature-pack-c scope.")
    parser.add_argument(
        "--config",
        default="config/feature_pack_c_readiness_v1.yaml",
        help="Path to the feature-pack-c readiness YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = FeaturePackCReadinessAnalyzer().analyze(
        feature_gap_payload=load_json_report(Path(config["paths"]["feature_gap_report"])),
        track_a_payload=load_json_report(Path(config["paths"]["track_a_report"])),
        track_a_sweep_payload=load_json_report(Path(config["paths"]["track_a_sweep_report"])),
        track_b_payload=load_json_report(Path(config["paths"]["track_b_report"])),
        track_b_validation_payload=load_json_report(Path(config["paths"]["track_b_validation_report"])),
    )
    report_path = write_feature_pack_c_readiness_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Feature-pack-c readiness report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
