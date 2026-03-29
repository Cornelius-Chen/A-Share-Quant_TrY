from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.data.free_data_bootstrap import (
    AkshareFreeDataBootstrapper,
    FreeDataBootstrapConfig,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap a minimum free A-share dataset pack with AKShare."
    )
    parser.add_argument(
        "--config",
        default="config/free_data_bootstrap.yaml",
        help="Path to the free-data bootstrap YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    payload = load_yaml_config(config_path)
    config = FreeDataBootstrapConfig.from_config(payload)
    bootstrapper = AkshareFreeDataBootstrapper(config)
    outputs = bootstrapper.run()

    print("Free data bootstrap complete.")
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
