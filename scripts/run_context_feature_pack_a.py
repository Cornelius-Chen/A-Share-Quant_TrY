from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.data.loaders import load_stock_snapshots_from_csv
from a_share_quant.strategy.context_feature_pack_a import (
    ContextFeaturePackAAnalyzer,
    write_context_feature_pack_a_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the first context-conditioned feature branch on closed slices."
    )
    parser.add_argument("--config", required=True, help="Path to the context-feature-pack-a YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    analyzer = ContextFeaturePackAAnalyzer()
    result = analyzer.analyze(
        stock_snapshots=load_stock_snapshots_from_csv(
            Path(config["paths"]["stock_snapshots_csv"])
        ),
        slice_specs=list(config["analysis"]["slices"]),
    )
    output_path = write_context_feature_pack_a_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Context feature-pack-a report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
