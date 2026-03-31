from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v113c_bounded_state_usage_review_v1 import (
    V113CBoundedStateUsageReviewAnalyzer,
    load_json_report,
    write_v113c_bounded_state_usage_review_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v113c_bounded_state_usage_review_v1.yaml").read_text(encoding="utf-8"))
    result = V113CBoundedStateUsageReviewAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v113c_phase_charter_report"])),
        driver_review_payload=load_json_report(Path(config["paths"]["v113b_driver_review_report"])),
    )
    output_path = write_v113c_bounded_state_usage_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.13C state usage review report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
