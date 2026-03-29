from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.feature_pack_c_balanced_turnover_weakness import (
    FeaturePackCBalancedTurnoverWeaknessAnalyzer,
    load_json_report,
    write_feature_pack_c_balanced_turnover_weakness_report,
)


def main() -> None:
    config = load_yaml_config(Path("config/feature_pack_c_balanced_turnover_weakness_v1.yaml"))
    result = FeaturePackCBalancedTurnoverWeaknessAnalyzer().analyze(
        turnover_context_payload=load_json_report(Path(str(config["inputs"]["turnover_context_report"]))),
        stock_snapshots_csv=Path(str(config["inputs"]["stock_snapshots_csv"])),
        case_names=[str(item) for item in config["inputs"]["case_names"]],
    )
    output_path = write_feature_pack_c_balanced_turnover_weakness_report(
        reports_dir=Path(str(config["paths"]["reports_dir"])),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
