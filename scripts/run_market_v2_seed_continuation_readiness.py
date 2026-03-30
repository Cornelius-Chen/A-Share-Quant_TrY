from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.market_v2_seed_continuation_readiness import (
    MarketV2SeedContinuationReadinessAnalyzer,
    load_json_report,
    write_market_v2_seed_continuation_readiness_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assess whether v2-seed should open another local replay lane.")
    parser.add_argument(
        "--config",
        default="config/market_v2_seed_continuation_readiness_v1.yaml",
        help="Path to the market-v2-seed continuation readiness YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = MarketV2SeedContinuationReadinessAnalyzer().analyze(
        q4_capture_acceptance=load_json_report(Path(config["paths"]["q4_capture_acceptance_report"])),
        q3_drawdown_acceptance=load_json_report(Path(config["paths"]["q3_drawdown_acceptance_report"])),
        audit_payload=load_json_report(Path(config["paths"]["audit_report"])),
        specialist_payload=load_json_report(Path(config["paths"]["specialist_report"])),
    )
    output_path = write_market_v2_seed_continuation_readiness_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Market v2-seed continuation readiness: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
