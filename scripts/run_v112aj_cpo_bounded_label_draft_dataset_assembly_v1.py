from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112aj_cpo_bounded_label_draft_dataset_assembly_v1 import (
    V112AJCPOBoundedLabelDraftDatasetAssemblyAnalyzer,
    load_json_report,
    write_v112aj_cpo_bounded_label_draft_dataset_assembly_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12AJ dataset assembly.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112AJCPOBoundedLabelDraftDatasetAssemblyAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112aj_phase_charter_report"])),
        cohort_map_payload=load_json_report(Path(config["paths"]["v112aa_cohort_map_report"])),
        labeling_review_payload=load_json_report(Path(config["paths"]["v112ab_labeling_review_report"])),
        owner_review_payload=load_json_report(Path(config["paths"]["v112ai_owner_review_report"])),
    )
    output_path = write_v112aj_cpo_bounded_label_draft_dataset_assembly_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12AJ dataset assembly report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
