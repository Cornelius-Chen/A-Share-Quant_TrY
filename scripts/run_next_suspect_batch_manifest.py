from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.next_suspect_batch_manifest import (
    NextSuspectBatchManifestAnalyzer,
    load_manifest_config,
    write_next_suspect_batch_manifest_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit the market_research_v2 seed manifest before bootstrap."
    )
    parser.add_argument("--config", required=True, help="Path to the seed-manifest YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    base_universe, seed_universe, manifest_entries, required_archetypes = load_manifest_config(
        config_path
    )
    config = load_yaml_config(config_path)
    analyzer = NextSuspectBatchManifestAnalyzer()
    result = analyzer.analyze(
        base_universe_symbols=base_universe,
        seed_universe_symbols=seed_universe,
        manifest_entries=manifest_entries,
        required_archetypes=required_archetypes,
    )
    output_path = write_next_suspect_batch_manifest_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Next suspect batch manifest report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
