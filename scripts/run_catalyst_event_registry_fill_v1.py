from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.catalyst_event_registry_fill_v1 import (
    CatalystEventRegistryFillAnalyzer,
    load_catalyst_event_registry_fill_config,
    write_catalyst_event_registry_fill_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fill the first bounded catalyst registry rows using local market context mappings."
    )
    parser.add_argument(
        "--config",
        default="config/catalyst_event_registry_fill_v1.yaml",
        help="Path to the catalyst event registry fill YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_payload, concept_mapping_rows, sector_mapping_rows, reports_dir, report_name = (
        load_catalyst_event_registry_fill_config(Path(args.config))
    )
    result = CatalystEventRegistryFillAnalyzer().analyze(
        seed_payload=seed_payload,
        concept_mapping_rows=concept_mapping_rows,
        sector_mapping_rows=sector_mapping_rows,
    )
    output_path = write_catalyst_event_registry_fill_report(
        reports_dir=reports_dir,
        report_name=report_name,
        result=result,
    )
    print(f"Catalyst event registry fill report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
