from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112q_parallel_collection_draft_batch_v1 import (
    V112QParallelCollectionDraftBatchAnalyzer,
    load_json_report,
    write_v112q_parallel_collection_draft_batch_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12Q parallel collection draft batch.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112QParallelCollectionDraftBatchAnalyzer()
    result = analyzer.analyze(
        schema_payload=load_json_report(Path(config["paths"]["v112q_schema_report"]))
    )
    output_path = write_v112q_parallel_collection_draft_batch_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12Q parallel collection draft batch report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
