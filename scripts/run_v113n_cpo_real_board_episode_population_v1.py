from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113n_cpo_real_board_episode_population_v1 import (
    V113NCPORealBoardEpisodePopulationAnalyzer,
    load_json_report,
    write_v113n_cpo_real_board_episode_population_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13N real CPO board episode population.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V113NCPORealBoardEpisodePopulationAnalyzer()
    result = analyzer.analyze(
        v113m_payload=load_json_report(Path(config["paths"]["v113m_report"])),
        v112ct_payload=load_json_report(Path(config["paths"]["v112ct_report"])),
        v112cn_payload=load_json_report(Path(config["paths"]["v112cn_report"])),
        v112co_payload=load_json_report(Path(config["paths"]["v112co_report"])),
        v112ci_payload=load_json_report(Path(config["paths"]["v112ci_report"])),
    )
    output_path = write_v113n_cpo_real_board_episode_population_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13N real CPO board episode population report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
