from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cw_packaging_mainline_extension_status_freeze_v1 import (
    V112CWPackagingMainlineExtensionStatusFreezeAnalyzer,
    load_json_report,
)


def test_v112cw_packaging_mainline_extension_status_freeze() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CWPackagingMainlineExtensionStatusFreezeAnalyzer()
    result = analyzer.analyze(
        ch_payload=load_json_report(repo_root / "reports/analysis/v112ch_packaging_mainline_template_freeze_v1.json"),
        cs_payload=load_json_report(repo_root / "reports/analysis/v112cs_core_residual_stack_status_freeze_v1.json"),
        cv_payload=load_json_report(repo_root / "reports/analysis/v112cv_controlled_packaging_admission_extension_replay_v1.json"),
    )
    summary = result.summary
    assert summary["mainline_template_asset_count"] == 1
    assert summary["mainline_extension_count"] == 1
    packaging_extension = next(row for row in result.stack_rows if row["stack_item"] == "packaging_admission_extension")
    assert packaging_extension["status"] == "controlled_mainline_extension"
