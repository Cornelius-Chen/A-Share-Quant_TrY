from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.family_candidate_shortlist import (
    FamilyCandidateShortlistAnalyzer,
    write_family_candidate_shortlist_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rank next replay candidates for specialist family research.")
    parser.add_argument(
        "--config",
        default="config/drawdown_family_candidate_shortlist_v1.yaml",
        help="Path to the candidate shortlist YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = FamilyCandidateShortlistAnalyzer().analyze(
        report_specs=list(config["analysis"]["reports"]),
        excluded_symbols=list(config["analysis"].get("excluded_symbols", [])),
        min_positive_delta=float(config["analysis"].get("min_positive_delta", 0.0)),
    )
    output_path = write_family_candidate_shortlist_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Family candidate shortlist report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
