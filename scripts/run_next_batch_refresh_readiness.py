from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.next_batch_refresh_readiness import (
    NextBatchRefreshReadinessAnalyzer,
    load_json_report,
    write_next_batch_refresh_readiness_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assess whether the repo should open another suspect-batch refresh now.")
    parser.add_argument(
        "--config",
        default="config/next_batch_refresh_readiness_v1.yaml",
        help="Path to the next-batch refresh readiness YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    plan_text = Path(config["paths"]["v2_seed_plan"]).read_text(encoding="utf-8")
    result = NextBatchRefreshReadinessAnalyzer().analyze(
        v11_continuation=load_json_report(Path(config["paths"]["v11_continuation_report"])),
        v2_seed_continuation=load_json_report(Path(config["paths"]["v2_seed_continuation_report"])),
        specialist_payload=load_json_report(Path(config["paths"]["specialist_report"])),
        v2_seed_plan_text=plan_text,
    )
    output_path = write_next_batch_refresh_readiness_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Next batch refresh readiness: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
