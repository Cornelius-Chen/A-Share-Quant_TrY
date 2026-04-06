from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_challenger_rotation_shadow_change_signal_v1 import (
    MaterializeAShareInternalHotNewsChallengerRotationShadowChangeSignalV1,
)


@dataclass(slots=True)
class V135AJAShareInternalHotNewsChallengerRotationShadowChangeSignalAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AJAShareInternalHotNewsChallengerRotationShadowChangeSignalAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AJAShareInternalHotNewsChallengerRotationShadowChangeSignalAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsChallengerRotationShadowChangeSignalV1(self.repo_root).materialize()
        rows = [
            {
                "component": "challenger_shadow_change_signal",
                "component_state": "materialized",
                "metric": "top_opportunity_theme_change",
                "value": materialized.summary["top_opportunity_theme_change"],
            },
            {
                "component": "challenger_shadow_change_signal",
                "component_state": "materialized",
                "metric": "top_watch_symbol_change",
                "value": materialized.summary["top_watch_symbol_change"],
            },
            {
                "component": "challenger_shadow_change_signal",
                "component_state": "materialized",
                "metric": "signal_priority",
                "value": materialized.summary["signal_priority"],
            },
        ]
        interpretation = [
            "This change signal compresses the difference between the current primary control packet and the challenger shadow control packet.",
            "It highlights whether accepting the challenger would change top opportunity or top watch, and how urgent that shadow delta is.",
        ]
        return V135AJAShareInternalHotNewsChallengerRotationShadowChangeSignalAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AJAShareInternalHotNewsChallengerRotationShadowChangeSignalAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AJAShareInternalHotNewsChallengerRotationShadowChangeSignalAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135aj_a_share_internal_hot_news_challenger_rotation_shadow_change_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
