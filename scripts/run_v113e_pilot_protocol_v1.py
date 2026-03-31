from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v113e_pilot_protocol_v1 import (
    V113EPilotProtocolAnalyzer,
    load_json_report,
    write_v113e_pilot_protocol_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v113e_pilot_protocol_v1.yaml").read_text(encoding="utf-8"))
    result = V113EPilotProtocolAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v113e_phase_charter_report"])),
        archetype_usage_payload=load_json_report(Path(config["paths"]["v113d_archetype_usage_report"])),
    )
    output_path = write_v113e_pilot_protocol_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.13E pilot protocol report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
