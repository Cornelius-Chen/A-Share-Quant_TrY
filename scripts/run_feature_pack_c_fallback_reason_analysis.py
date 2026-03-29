from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.feature_pack_c_fallback_reason_analysis import (
    FeaturePackCFallbackReasonAnalyzer,
    load_json_report,
    write_feature_pack_c_fallback_reason_analysis_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decompose feature-pack-c fallback rows into local causal deficit types.")
    parser.add_argument(
        "--config",
        default="config/feature_pack_c_fallback_reason_analysis_v1.yaml",
        help="Path to the feature-pack-c fallback-reason analysis YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = FeaturePackCFallbackReasonAnalyzer().analyze(
        recheck_payload=load_json_report(Path(config["paths"]["recheck_report"])),
        case_names=[str(item) for item in config["analysis"]["case_names"]],
    )
    report_path = write_feature_pack_c_fallback_reason_analysis_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Feature-pack-c fallback-reason report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
