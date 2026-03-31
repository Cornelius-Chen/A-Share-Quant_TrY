from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v112i_label_refinement_review_protocol_v1 import (
    V112ILabelRefinementReviewProtocolAnalyzer,
    load_json_report,
    write_v112i_label_refinement_review_protocol_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v112i_label_refinement_review_protocol_v1.yaml").read_text(encoding="utf-8"))
    result = V112ILabelRefinementReviewProtocolAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112i_phase_charter_report"])),
        refinement_design_payload=load_json_report(Path(config["paths"]["v112f_refinement_design_report"])),
        semantic_rerun_payload=load_json_report(Path(config["paths"]["v112g_phase_closure_check_report"])),
    )
    output_path = write_v112i_label_refinement_review_protocol_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.12I label refinement review protocol report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
