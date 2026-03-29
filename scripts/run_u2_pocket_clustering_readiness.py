from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.u2_pocket_clustering_readiness import (
    U2PocketClusteringReadinessAnalyzer,
    load_json_report,
    write_u2_pocket_clustering_readiness_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decide whether U2 pocket clustering should start.")
    parser.add_argument(
        "--config",
        default="config/u2_pocket_clustering_readiness_v1.yaml",
        help="Path to the U2 readiness YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    result = U2PocketClusteringReadinessAnalyzer().analyze(
        feature_gap_payload=load_json_report(Path(config["paths"]["feature_gap_report"])),
        feature_pack_c_acceptance_payload=load_json_report(Path(config["paths"]["feature_pack_c_acceptance_report"])),
        u1_payload=load_json_report(Path(config["paths"]["u1_report"])),
    )
    report_path = write_u2_pocket_clustering_readiness_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"U2 pocket clustering readiness report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
