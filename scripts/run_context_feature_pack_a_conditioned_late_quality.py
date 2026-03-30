from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.data.loaders import load_stock_snapshots_from_csv
from a_share_quant.strategy.context_feature_pack_a_conditioned_late_quality import (
    ContextConditionedLateQualityAnalyzer,
    write_context_conditioned_late_quality_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze whether late-quality misses should be conditioned on theme-turnover context."
    )
    parser.add_argument("--config", required=True, help="Path to the conditioned late-quality YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_yaml_config(config_path)
    suite_config = load_yaml_config(Path(config["paths"]["strategy_suite_config"]))

    hierarchy_config = dict(suite_config.get("trend", {}).get("hierarchy", {}))
    thresholds = dict(config.get("analysis", {}).get("thresholds", {}))

    analyzer = ContextConditionedLateQualityAnalyzer()
    result = analyzer.analyze(
        stock_snapshots=load_stock_snapshots_from_csv(
            Path(config["paths"]["stock_snapshots_csv"])
        ),
        slice_specs=list(config["analysis"]["slices"]),
        late_quality_threshold=float(hierarchy_config.get("min_quality_for_late_mover", 0.55)),
        non_junk_threshold=float(hierarchy_config.get("min_composite_for_non_junk", 0.55)),
        resonance_floor=float(thresholds.get("resonance_floor", 0.40)),
        high_interaction_threshold=float(thresholds.get("high_interaction_threshold", 0.25)),
        medium_interaction_threshold=float(thresholds.get("medium_interaction_threshold", 0.18)),
        near_threshold_gap=float(thresholds.get("near_threshold_gap", 0.05)),
    )
    output_path = write_context_conditioned_late_quality_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Conditioned late-quality report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
