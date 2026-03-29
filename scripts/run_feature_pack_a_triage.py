from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.feature_pack_a_triage import (
    FeaturePackATriageAnalyzer,
    write_feature_pack_a_triage_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Split feature-pack-a suspects into narrow next-step tracks.")
    parser.add_argument("--config", required=True, help="Path to the feature-pack-a triage YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = FeaturePackATriageAnalyzer()
    result = analyzer.analyze(
        recheck_report_path=Path(config["paths"]["recheck_report_path"]),
    )
    output_path = write_feature_pack_a_triage_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Feature-pack-a triage report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
