from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v114f_multi_board_autonomous_research_orchestrator_protocol_v1 import (
    V114FMultiBoardAutonomousResearchOrchestratorProtocolAnalyzer,
    write_v114f_multi_board_autonomous_research_orchestrator_protocol_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.14F multi-board autonomous research orchestrator protocol.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    analyzer = V114FMultiBoardAutonomousResearchOrchestratorProtocolAnalyzer(repo_root=Path(__file__).resolve().parents[1])
    result = analyzer.analyze(
        default_phase_version=str(config["inputs"]["default_phase_version"]),
        board_queue=list(config["inputs"]["board_queue"]),
    )
    output_path = write_v114f_multi_board_autonomous_research_orchestrator_protocol_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

