from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.v112x_cpo_spillover_factor_candidacy_review_v1 import (
    V112XSpilloverFactorCandidacyReviewAnalyzer,
    load_json_report,
    write_v112x_cpo_spillover_factor_candidacy_review_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.12X CPO spillover factor candidacy review.")
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = V112XSpilloverFactorCandidacyReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path(config["paths"]["v112x_phase_charter_report"])),
        spillover_payload=load_json_report(Path(config["paths"]["v112t_spillover_report"])),
    )
    output_path = write_v112x_cpo_spillover_factor_candidacy_review_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.12X spillover factor candidacy review report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
