from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.context_feature_pack_a_conditioned_late_quality_acceptance import (
    ContextConditionedLateQualityAcceptanceAnalyzer,
    load_json_report,
    write_context_conditioned_late_quality_acceptance_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Accept or close the conditioned late-quality context branch."
    )
    parser.add_argument("--config", required=True, help="Path to the conditioned branch acceptance YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = ContextConditionedLateQualityAcceptanceAnalyzer()
    result = analyzer.analyze(
        control_payload=load_json_report(Path(config["paths"]["control_comparison_report"])),
        conditioned_payload=load_json_report(Path(config["paths"]["conditioned_comparison_report"])),
        min_material_return_improvement=float(
            config["analysis"].get("min_material_return_improvement", 0.0005)
        ),
        max_capture_regression=float(
            config["analysis"].get("max_capture_regression", 0.001)
        ),
    )
    output_path = write_context_conditioned_late_quality_acceptance_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Conditioned late-quality acceptance report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
