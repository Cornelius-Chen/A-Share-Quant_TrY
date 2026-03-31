from __future__ import annotations

import json
from pathlib import Path

import yaml

from a_share_quant.strategy.v113a_theme_diffusion_state_schema_v1 import (
    V113AThemeDiffusionStateSchemaAnalyzer,
    load_json_report,
    write_v113a_theme_diffusion_state_schema_report,
)


def main() -> None:
    config = yaml.safe_load(Path("config/v113a_theme_diffusion_state_schema_v1.yaml").read_text(encoding="utf-8"))
    result = V113AThemeDiffusionStateSchemaAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v113a_phase_charter_report"]))
    )
    output_path = write_v113a_theme_diffusion_state_schema_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=config["paths"]["report_name"],
        result=result,
    )
    print(f"V1.13A state schema report: {output_path}")
    print(f"Summary: {json.dumps(result.summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
