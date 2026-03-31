from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v112k_candidate_substate_draft_v1 import (
    V112KCandidateSubstateDraftAnalyzer,
    load_json_report,
    write_v112k_candidate_substate_draft_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v112k_candidate_substate_draft_v1.yaml").read_text(encoding="utf-8"))
    result = V112KCandidateSubstateDraftAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112k_phase_charter_report"])),
        candidate_review_payload=load_json_report(Path(config["paths"]["v112j_candidate_structure_review_report"])),
        bucketization_payload=load_json_report(Path(config["paths"]["v112h_bucketization_report"])),
    )
    output_path = write_v112k_candidate_substate_draft_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.12K candidate substate draft report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
