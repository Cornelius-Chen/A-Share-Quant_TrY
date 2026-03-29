from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.concept_to_late_bridge_analysis import (
    ConceptToLateBridgeAnalyzer,
    write_concept_to_late_bridge_analysis_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze how much concept support is needed to bridge a late-mover threshold.")
    parser.add_argument("--config", required=True, help="Path to the concept-to-late bridge YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = ConceptToLateBridgeAnalyzer()
    result = analyzer.analyze(
        recheck_report_path=Path(config["paths"]["recheck_report_path"]),
        case_name=str(config["analysis"]["case_name"]),
        timeline_config_path=Path(config["paths"]["timeline_config_path"]),
        derived_config_path=Path(config["paths"]["derived_config_path"]),
    )
    output_path = write_concept_to_late_bridge_analysis_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Concept-to-late bridge report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
