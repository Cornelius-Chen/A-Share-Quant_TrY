from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.data.bootstrap_derived import (
    BootstrapDerivedConfig,
    BootstrapDerivedDataBuilder,
)
from a_share_quant.data.loaders import load_daily_bars_from_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate first-pass derived research tables from bootstrap local bars."
    )
    parser.add_argument(
        "--config",
        default="config/bootstrap_derived_data.yaml",
        help="Path to the derived-data bootstrap YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    payload = load_yaml_config(config_path)
    config = BootstrapDerivedConfig.from_config(payload)
    bars = load_daily_bars_from_csv(config.bars_csv)
    builder = BootstrapDerivedDataBuilder(config)
    outputs = builder.build(bars)

    print("Bootstrap derived data generation complete.")
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
