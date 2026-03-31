from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112bo_cpo_internal_maturity_overlay_review_v1 import (
    V112BOCPOInternalMaturityOverlayReviewAnalyzer,
    load_json_report,
    write_v112bo_cpo_internal_maturity_overlay_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12BO internal maturity overlay review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112BOCPOInternalMaturityOverlayReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["phase_charter_report"])),
        cycle_reconstruction_payload=load_json_report(Path(config["paths"]["cycle_reconstruction_report"])),
        market_regime_overlay_payload=load_json_report(Path(config["paths"]["market_regime_overlay_report"])),
        feature_family_payload=load_json_report(Path(config["paths"]["feature_family_report"])),
        regime_gate_pilot_payload=load_json_report(Path(config["paths"]["regime_gate_pilot_report"])),
    )
    output_path = write_v112bo_cpo_internal_maturity_overlay_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12BO internal maturity overlay review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
