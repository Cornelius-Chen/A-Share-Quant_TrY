from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.v12_v6_refresh_manifest_v1 import (
    V12V6RefreshManifestAnalyzer,
    load_manifest_config,
    write_v12_v6_refresh_manifest_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit whether the v6 refresh manifest is ready to bootstrap.")
    parser.add_argument(
        "--config",
        default="config/market_research_v6_catalyst_supported_carry_persistence_refresh_manifest.yaml",
        help="Path to the v6 refresh manifest YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reference_base, seed_universe, manifest_entries, required_targets = load_manifest_config(Path(args.config))
    result = V12V6RefreshManifestAnalyzer().analyze(
        reference_base_symbols=reference_base,
        seed_universe_symbols=seed_universe,
        manifest_entries=manifest_entries,
        required_targets=required_targets,
    )
    output_path = write_v12_v6_refresh_manifest_report(
        reports_dir=Path("reports/analysis"),
        report_name="market_research_v6_catalyst_supported_carry_persistence_refresh_manifest_v1",
        result=result,
    )
    print(f"V12 v6 refresh manifest report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
