from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.feature_pack_b_hierarchy_approval_sweep import (
    FeaturePackBHierarchyApprovalSweepAnalyzer,
    write_feature_pack_b_hierarchy_approval_sweep_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a pocket-local hierarchy/approval sweep for feature-pack-b.")
    parser.add_argument("--config", required=True, help="Path to the hierarchy/approval sweep YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = FeaturePackBHierarchyApprovalSweepAnalyzer()
    result = analyzer.analyze(
        timeline_config_path=Path(config["paths"]["timeline_config_path"]),
        case_report_path=Path(config["paths"]["case_report_path"]),
        candidates_spec=list(config["analysis"]["candidates"]),
        control_candidate_name=str(config["analysis"]["control_candidate_name"]),
    )
    output_path = write_feature_pack_b_hierarchy_approval_sweep_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Feature-pack-b hierarchy/approval sweep report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
