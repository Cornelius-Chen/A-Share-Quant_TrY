from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.feature_pack_b_concept_supported_hierarchy import (
    FeaturePackBConceptSupportedHierarchyAnalyzer,
    write_feature_pack_b_concept_supported_hierarchy_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the concept-supported hierarchy track for feature-pack-b.")
    parser.add_argument("--config", required=True, help="Path to the feature-pack-b concept-supported hierarchy YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = FeaturePackBConceptSupportedHierarchyAnalyzer()
    result = analyzer.analyze(
        recheck_report_path=Path(config["paths"]["recheck_report_path"]),
        case_name=str(config["analysis"]["case_name"]),
    )
    output_path = write_feature_pack_b_concept_supported_hierarchy_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Feature-pack-b concept-supported hierarchy report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
