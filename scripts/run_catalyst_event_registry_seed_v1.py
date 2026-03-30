from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.catalyst_event_registry_seed_v1 import (
    CatalystEventRegistrySeedAnalyzer,
    load_catalyst_event_registry_seed_config,
    write_catalyst_event_registry_seed_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the first bounded catalyst event registry seed from already-closed lanes."
    )
    parser.add_argument(
        "--config",
        default="config/catalyst_event_registry_seed_v1.yaml",
        help="Path to the catalyst event registry seed YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    opening_reports, persistence_reports, carry_schema_payload, reports_dir, report_name = (
        load_catalyst_event_registry_seed_config(Path(args.config))
    )
    result = CatalystEventRegistrySeedAnalyzer().analyze(
        opening_reports=opening_reports,
        persistence_reports=persistence_reports,
        carry_schema_payload=carry_schema_payload,
    )
    output_path = write_catalyst_event_registry_seed_report(
        reports_dir=reports_dir,
        report_name=report_name,
        result=result,
    )
    print(f"Catalyst event registry seed report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
