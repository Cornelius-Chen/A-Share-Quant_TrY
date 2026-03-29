from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from a_share_quant.data.data_audit import DataAuditConfig, DataPackAuditor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit canonical and derived data-pack completeness.")
    parser.add_argument("--config", required=True, help="Path to the data-audit YAML config.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)

    auditor = DataPackAuditor(DataAuditConfig.from_config(payload))
    report = auditor.build_report()
    output_path = auditor.write_report(report)

    print("Data-pack audit complete.")
    print(f"output: {output_path}")
    print(json.dumps(report["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
