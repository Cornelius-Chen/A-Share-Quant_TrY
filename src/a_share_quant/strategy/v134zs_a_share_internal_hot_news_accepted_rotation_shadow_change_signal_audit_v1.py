from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_accepted_rotation_shadow_change_signal_v1 import (
    MaterializeAShareInternalHotNewsAcceptedRotationShadowChangeSignalV1,
)


@dataclass(slots=True)
class V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsAcceptedRotationShadowChangeSignalV1(self.repo_root).materialize()
        rows = [
            {
                "component": "shadow_change_signal",
                "component_state": "materialized",
                "metric": "top_opportunity_theme_change",
                "value": materialized.summary["top_opportunity_theme_change"],
            },
            {
                "component": "shadow_change_signal",
                "component_state": "materialized",
                "metric": "top_watch_symbol_change",
                "value": materialized.summary["top_watch_symbol_change"],
            },
            {
                "component": "shadow_change_signal",
                "component_state": "materialized",
                "metric": "signal_priority",
                "value": materialized.summary["signal_priority"],
            },
        ]
        interpretation = [
            "This change signal compresses the difference between the current primary control packet and the accepted shadow control packet.",
            "It highlights whether accepting the rotation would change top opportunity or top watch.",
        ]
        return V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zs_a_share_internal_hot_news_accepted_rotation_shadow_change_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
