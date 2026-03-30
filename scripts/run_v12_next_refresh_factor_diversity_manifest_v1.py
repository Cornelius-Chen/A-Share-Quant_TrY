from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.v12_next_refresh_factor_diversity_manifest_v1 import (
    V12NextRefreshFactorDiversityManifestAnalyzer,
    load_manifest_config,
    write_v12_next_refresh_factor_diversity_manifest_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run V1.2 next refresh factor-diversity manifest gate v1."
    )
    parser.add_argument(
        "--config",
        default="config/market_research_v3_factor_diversity_seed_manifest.yaml",
        help="Path to the factor-diversity seed manifest YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = ROOT / args.config
    reference_base, seed_universe, manifest_entries, required_targets = load_manifest_config(
        config_path
    )
    config = load_yaml_config(config_path)
    result = V12NextRefreshFactorDiversityManifestAnalyzer().analyze(
        reference_base_symbols=reference_base,
        seed_universe_symbols=seed_universe,
        manifest_entries=manifest_entries,
        required_targets=required_targets,
    )
    output_path = write_v12_next_refresh_factor_diversity_manifest_report(
        reports_dir=ROOT / config["paths"]["reports_dir"],
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"V1.2 next refresh factor-diversity manifest report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
