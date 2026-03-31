from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v17_promotion_evidence_protocol_v1 import (
    V17PromotionEvidenceProtocolAnalyzer,
    load_json_report,
    write_v17_promotion_evidence_protocol_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V1.7 promotion evidence protocol freeze.")
    parser.add_argument(
        "--config",
        default="config/v17_promotion_evidence_protocol_v1.yaml",
        help="Path to the V1.7 promotion evidence protocol config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = V17PromotionEvidenceProtocolAnalyzer().analyze(
        v17_phase_charter_payload=load_json_report(Path(config["paths"]["v17_phase_charter_report"])),
        v16_feature_stability_review_payload=load_json_report(
            Path(config["paths"]["v16_feature_stability_review_report"])
        ),
    )
    output_path = write_v17_promotion_evidence_protocol_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.7 promotion evidence protocol report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
