from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.data.loaders import load_stock_snapshots_from_csv
from a_share_quant.strategy.context_feature_pack_b_sector_heat_breadth import (
    ContextFeaturePackBSectorHeatBreadthAnalyzer,
    write_context_feature_pack_b_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit whether sector heat/breadth should become the second conditioned context branch."
    )
    parser.add_argument("--config", required=True, help="Path to the context-feature-pack-b YAML.")
    args = parser.parse_args()

    config = load_yaml_config(Path(args.config))
    suite_config = load_yaml_config(Path(config["paths"]["strategy_suite_config"]))
    hierarchy_config = dict(suite_config.get("trend", {}).get("hierarchy", {}))
    thresholds = dict(config.get("analysis", {}).get("thresholds", {}))

    analyzer = ContextFeaturePackBSectorHeatBreadthAnalyzer()
    result = analyzer.analyze(
        stock_snapshots=load_stock_snapshots_from_csv(Path(config["paths"]["stock_snapshots_csv"])),
        slice_specs=list(config["analysis"]["slices"]),
        non_junk_threshold=float(hierarchy_config.get("min_composite_for_non_junk", 0.55)),
        late_quality_floor=float(thresholds.get("late_quality_floor", 0.55)),
        resonance_floor=float(thresholds.get("resonance_floor", 0.40)),
        high_sector_heat_threshold=float(thresholds.get("high_sector_heat_threshold", 0.65)),
        high_sector_breadth_threshold=float(thresholds.get("high_sector_breadth_threshold", 0.55)),
        near_threshold_gap=float(thresholds.get("near_threshold_gap", 0.05)),
    )
    output_path = write_context_feature_pack_b_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Context feature-pack-b report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
