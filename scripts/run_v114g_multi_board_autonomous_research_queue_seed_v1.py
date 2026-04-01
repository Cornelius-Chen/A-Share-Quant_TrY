from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114g_multi_board_autonomous_research_queue_seed_v1 import (
    V114GMultiBoardAutonomousResearchQueueSeedAnalyzer,
    write_v114g_multi_board_autonomous_research_queue_seed_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.14G autonomous research queue seed.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    analyzer = V114GMultiBoardAutonomousResearchQueueSeedAnalyzer(repo_root=Path(__file__).resolve().parents[1])
    result = analyzer.analyze(
        v114f_payload=load_json_report(Path(config["paths"]["v114f_report"])),
        board_queue=list(config["inputs"]["board_queue"]),
    )
    output_path = write_v114g_multi_board_autonomous_research_queue_seed_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

