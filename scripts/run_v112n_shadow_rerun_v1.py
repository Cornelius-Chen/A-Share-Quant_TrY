from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v112n_shadow_rerun_v1 import (
    V112NShadowRerunAnalyzer,
    load_json_report,
    write_v112n_shadow_rerun_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v112n_shadow_rerun_v1.yaml").read_text(encoding="utf-8"))
    result = V112NShadowRerunAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112n_phase_charter_report"])),
        pilot_dataset_payload=load_json_report(Path(config["paths"]["v112b_pilot_dataset_freeze_report"])),
        baseline_v2_payload=load_json_report(Path(config["paths"]["v112g_baseline_readout_v2_report"])),
        gbdt_v2_payload=load_json_report(Path(config["paths"]["v112g_gbdt_pilot_v2_report"])),
    )
    output_path = write_v112n_shadow_rerun_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.12N shadow rerun report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
