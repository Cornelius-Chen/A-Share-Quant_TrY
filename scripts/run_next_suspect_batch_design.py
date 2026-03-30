from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.next_suspect_batch_design import (
    NextSuspectBatchDesignAnalyzer,
    load_json_report,
    write_next_suspect_batch_design_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Design the next specialist suspect batch from current closed-slice geography."
    )
    parser.add_argument("--config", required=True, help="Path to the next suspect batch design YAML.")
    args = parser.parse_args()

    config = load_yaml_config(Path(args.config))
    report_paths = dict(config["paths"]["reports"])

    analyzer = NextSuspectBatchDesignAnalyzer()
    result = analyzer.analyze(
        context_audit=load_json_report(Path(report_paths["context_audit"])),
        continuation_readiness=load_json_report(Path(report_paths["continuation_readiness"])),
        specialist_alpha=load_json_report(Path(report_paths["specialist_alpha"])),
    )
    output_path = write_next_suspect_batch_design_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Next suspect batch design report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
