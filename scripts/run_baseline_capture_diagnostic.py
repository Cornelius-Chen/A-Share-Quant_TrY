from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.common.config import load_yaml_config
from a_share_quant.strategy.baseline_capture_diagnostic import (
    BaselineCaptureDiagnostic,
    load_json_report,
    write_baseline_capture_diagnostic,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnose where a challenger gives back baseline-pack capture."
    )
    parser.add_argument(
        "--config",
        default="config/baseline_capture_diagnostic_v1.yaml",
        help="Path to the baseline-capture diagnostic YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_yaml_config(Path(args.config))
    comparison_payload = load_json_report(Path(payload["paths"]["comparison_report"]))
    slice_payload = None
    if payload["paths"].get("slice_report"):
        slice_payload = load_json_report(Path(payload["paths"]["slice_report"]))

    diagnostic = BaselineCaptureDiagnostic().analyze(
        comparison_payload=comparison_payload,
        slice_payload=slice_payload,
        incumbent_name=str(payload["diagnostic"]["incumbent_name"]),
        challenger_name=str(payload["diagnostic"]["challenger_name"]),
        dataset_name=str(payload["diagnostic"]["dataset_name"]),
    )
    output_path = write_baseline_capture_diagnostic(
        reports_dir=Path(payload["paths"]["reports_dir"]),
        report_name=str(payload["report"]["name"]),
        result=diagnostic,
        extras={
            "config_path": str(Path(args.config)),
            "protocol_version": str(payload["project"]["protocol_version"]),
        },
    )
    print(f"Baseline capture diagnostic report: {output_path}")
    print(f"Summary: {diagnostic.summary}")


if __name__ == "__main__":
    main()
