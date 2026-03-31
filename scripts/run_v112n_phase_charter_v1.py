from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v112n_phase_charter_v1 import (
    V112NPhaseCharterAnalyzer,
    load_json_report,
    write_v112n_phase_charter_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v112n_phase_charter_v1.yaml").read_text(encoding="utf-8"))
    result = V112NPhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path(config["paths"]["v112m_phase_closure_check_report"]))
    )
    output_path = write_v112n_phase_charter_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.12N phase charter report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
