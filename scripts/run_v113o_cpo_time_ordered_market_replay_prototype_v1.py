from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v113o_cpo_time_ordered_market_replay_prototype_v1 import (
    V113OCPOTimeOrderedMarketReplayPrototypeAnalyzer,
    load_json_report,
    write_v113o_cpo_time_ordered_market_replay_prototype_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.13O CPO time-ordered market replay prototype.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    repo_root = Path(config["paths"]["repo_root"])
    analyzer = V113OCPOTimeOrderedMarketReplayPrototypeAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / config["paths"]["v113n_report"]),
    )
    output_path = write_v113o_cpo_time_ordered_market_replay_prototype_report(
        reports_dir=repo_root / config["paths"]["reports_dir"],
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.13O CPO time-ordered market replay prototype report: {output_path.relative_to(repo_root)}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
