from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v113_template_entry_v1 import (
    V113TemplateEntryAnalyzer,
    load_json_report,
    write_v113_template_entry_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v113_template_entry_v1.yaml").read_text(encoding="utf-8"))
    result = V113TemplateEntryAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v113_phase_charter_report"]))
    )
    output_path = write_v113_template_entry_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.13 template entry report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
