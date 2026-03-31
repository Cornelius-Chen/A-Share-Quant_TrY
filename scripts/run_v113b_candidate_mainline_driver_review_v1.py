from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v113b_candidate_mainline_driver_review_v1 import (
    V113BCandidateMainlineDriverReviewAnalyzer,
    load_json_report,
    write_v113b_candidate_mainline_driver_review_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v113b_candidate_mainline_driver_review_v1.yaml").read_text(encoding="utf-8"))
    result = V113BCandidateMainlineDriverReviewAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v113b_phase_charter_report"])),
        state_schema_payload=load_json_report(Path(config["paths"]["v113a_state_schema_report"])),
    )
    output_path = write_v113b_candidate_mainline_driver_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.13B driver review report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
