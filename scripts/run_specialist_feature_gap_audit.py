from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.specialist_feature_gap_audit import (
    SpecialistFeatureGapAuditAnalyzer,
    write_specialist_feature_gap_audit_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit whether specialist replay work is entering a feature-limited thinning phase.")
    parser.add_argument("--config", required=True, help="Path to the specialist feature-gap audit YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = SpecialistFeatureGapAuditAnalyzer()
    result = analyzer.analyze(report_specs=list(config["analysis"]["reports"]))
    output_path = write_specialist_feature_gap_audit_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Specialist feature-gap audit report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
