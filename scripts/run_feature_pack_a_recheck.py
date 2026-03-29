from __future__ import annotations

import argparse
from pathlib import Path

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.feature_pack_a_recheck import (
    FeaturePackARecheckAnalyzer,
    write_feature_pack_a_recheck_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run feature-pack-a suspect recheck.")
    parser.add_argument("--config", required=True, help="Path to the feature-pack-a recheck YAML config.")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_yaml_config(config_path)

    report_name = str(config["report"]["name"])
    reports_dir = Path(str(config["paths"]["reports_dir"]))
    case_specs = list(config.get("cases", []))

    result = FeaturePackARecheckAnalyzer().analyze(case_specs=case_specs)
    output_path = write_feature_pack_a_recheck_report(
        reports_dir=reports_dir,
        report_name=report_name,
        result=result,
    )
    print(f"Feature-pack-a recheck report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
