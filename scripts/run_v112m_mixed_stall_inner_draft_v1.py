from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v112m_mixed_stall_inner_draft_v1 import (
    V112MMixedStallInnerDraftAnalyzer,
    load_json_report,
    write_v112m_mixed_stall_inner_draft_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v112m_mixed_stall_inner_draft_v1.yaml").read_text(encoding="utf-8"))
    result = V112MMixedStallInnerDraftAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112m_phase_charter_report"])),
        pilot_dataset_payload=load_json_report(Path(config["paths"]["v112b_pilot_dataset_freeze_report"])),
        prior_owner_review_payload=load_json_report(Path(config["paths"]["v112l_candidate_substate_owner_review_report"])),
    )
    output_path = write_v112m_mixed_stall_inner_draft_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.12M mixed stall inner draft report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
