from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.feature_pack_c_acceptance import (
    FeaturePackCAcceptanceAnalyzer,
    load_json_report,
    write_feature_pack_c_acceptance_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize whether feature-pack-c should close as explanatory.")
    parser.add_argument(
        "--config",
        default="config/feature_pack_c_acceptance_v1.yaml",
        help="Path to the feature-pack-c acceptance YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = FeaturePackCAcceptanceAnalyzer().analyze(
        fallback_payload=load_json_report(Path(config["paths"]["fallback_report"])),
        residual_payload=load_json_report(Path(config["paths"]["residual_report"])),
        stability_liquidity_payload=load_json_report(Path(config["paths"]["stability_liquidity_report"])),
        turnover_payload=load_json_report(Path(config["paths"]["turnover_report"])),
        balanced_turnover_payload=load_json_report(Path(config["paths"]["balanced_turnover_report"])),
    )
    report_path = write_feature_pack_c_acceptance_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Feature-pack-c acceptance report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
