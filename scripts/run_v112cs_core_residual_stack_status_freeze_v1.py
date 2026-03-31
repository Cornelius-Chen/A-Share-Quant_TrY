from __future__ import annotations

from pathlib import Path

import yaml

from a_share_quant.strategy.v112cs_core_residual_stack_status_freeze_v1 import (
    V112CSCoreResidualStackStatusFreezeAnalyzer,
    load_json_report,
    write_v112cs_core_residual_stack_status_freeze_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "config" / "v112cs_core_residual_stack_status_freeze_v1.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    analyzer = V112CSCoreResidualStackStatusFreezeAnalyzer()
    result = analyzer.analyze(
        ch_payload=load_json_report(repo_root / config["ch_report_path"]),
        ci_payload=load_json_report(repo_root / config["ci_report_path"]),
        cn_payload=load_json_report(repo_root / config["cn_report_path"]),
        cq_payload=load_json_report(repo_root / config["cq_report_path"]),
        cr_payload=load_json_report(repo_root / config["cr_report_path"]),
    )
    output_path = write_v112cs_core_residual_stack_status_freeze_report(
        reports_dir=repo_root / config["reports_dir"],
        report_name=config["report_name"],
        result=result,
    )
    print(f"V1.12CS core residual stack status freeze report: {output_path.relative_to(repo_root)}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
