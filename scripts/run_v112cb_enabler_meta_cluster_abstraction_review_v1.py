from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112cb_enabler_meta_cluster_abstraction_review_v1 import (
    V112CBEnablerMetaClusterAbstractionReviewAnalyzer,
    load_json_report,
    write_v112cb_enabler_meta_cluster_abstraction_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12CB enabler meta-cluster abstraction review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    analyzer = V112CBEnablerMetaClusterAbstractionReviewAnalyzer()
    result = analyzer.analyze(
        by_payload=load_json_report(Path(config["paths"]["by_report"])),
        ca_payload=load_json_report(Path(config["paths"]["ca_report"])),
    )
    output_path = write_v112cb_enabler_meta_cluster_abstraction_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12CB meta-cluster abstraction report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
