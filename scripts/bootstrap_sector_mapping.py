from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.data.loaders import load_daily_bars_from_csv
from a_share_quant.data.sector_mapper import AkshareCninfoSectorMapper, SectorMapperConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap daily sector mapping from CNInfo industry-change history via AKShare."
    )
    parser.add_argument(
        "--config",
        default="config/bootstrap_sector_mapping.yaml",
        help="Path to the sector-mapping bootstrap YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    payload = load_yaml_config(config_path)
    bars = load_daily_bars_from_csv(Path(payload["bars_csv"]))
    mapper = AkshareCninfoSectorMapper(SectorMapperConfig.from_config(payload))
    records = mapper.build_daily_mapping(bars)
    output_path = mapper.write_daily_mapping(records)

    print("Bootstrap sector mapping complete.")
    print(f"rows: {len(records)}")
    print(f"output: {output_path}")


if __name__ == "__main__":
    main()
