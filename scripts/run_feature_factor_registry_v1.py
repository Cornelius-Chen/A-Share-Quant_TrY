from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.feature_factor_registry_v1 import (
    FeatureFactorRegistryAnalyzer,
    write_feature_factor_registry_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the first V1.2 feature/factor registry.")
    parser.add_argument(
        "--config",
        default="config/feature_factor_registry_v1.yaml",
        help="Path to the feature/factor registry YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = FeatureFactorRegistryAnalyzer().analyze(
        root_dir=ROOT,
        entries=[dict(item) for item in config["registry"]["entries"]],
    )
    output_path = write_feature_factor_registry_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Feature/factor registry report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
