from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from a_share_quant.strategy.cycle_family_inventory import (
    CycleFamilyInventoryAnalyzer,
    write_cycle_family_inventory_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate drawdown cycle families across analyzed pockets.")
    parser.add_argument("--config", required=True, help="Path to the cycle family inventory config YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = CycleFamilyInventoryAnalyzer()
    result = analyzer.analyze(report_specs=list(config["analysis"]["reports"]))
    output_path = write_cycle_family_inventory_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Cycle family inventory report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
