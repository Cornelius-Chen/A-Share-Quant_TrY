from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.feature_pack_b_readiness import (
    FeaturePackBReadinessAnalyzer,
    write_feature_pack_b_readiness_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert feature-pack-a outputs into concrete feature-pack-b tracks.")
    parser.add_argument("--config", required=True, help="Path to the feature-pack-b readiness YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = FeaturePackBReadinessAnalyzer()
    result = analyzer.analyze(
        triage_report_path=Path(config["paths"]["triage_report_path"]),
        recheck_report_path=Path(config["paths"]["recheck_report_path"]),
    )
    output_path = write_feature_pack_b_readiness_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Feature-pack-b readiness report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
