from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.catalyst_event_registry_schema_v1 import (
    CatalystEventRegistrySchemaAnalyzer,
    write_catalyst_event_registry_schema_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze the first bounded catalyst-event registry schema."
    )
    parser.add_argument(
        "--config",
        default="config/catalyst_event_registry_schema_v1.yaml",
        help="Path to the catalyst-event registry schema YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = CatalystEventRegistrySchemaAnalyzer().analyze()
    output_path = write_catalyst_event_registry_schema_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Catalyst event registry schema report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
