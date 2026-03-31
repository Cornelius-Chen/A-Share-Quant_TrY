from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v113d_bounded_archetype_usage_pass_v1 import (
    V113DBoundedArchetypeUsagePassAnalyzer,
    load_json_report,
    write_v113d_bounded_archetype_usage_pass_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v113d_bounded_archetype_usage_pass_v1.yaml").read_text(encoding="utf-8"))
    result = V113DBoundedArchetypeUsagePassAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v113d_phase_charter_report"])),
        template_entry_payload=load_json_report(Path(config["paths"]["v113_template_entry_report"])),
        state_usage_review_payload=load_json_report(Path(config["paths"]["v113c_state_usage_review_report"])),
    )
    output_path = write_v113d_bounded_archetype_usage_pass_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.13D archetype usage report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
