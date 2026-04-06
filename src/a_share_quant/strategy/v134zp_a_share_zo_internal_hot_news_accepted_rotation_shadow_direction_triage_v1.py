from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134zo_a_share_internal_hot_news_accepted_rotation_shadow_snapshot_audit_v1 import (
    V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ZPAShareZOInternalHotNewsAcceptedRotationShadowDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ZPAShareZOInternalHotNewsAcceptedRotationShadowDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZPAShareZOInternalHotNewsAcceptedRotationShadowDirectionTriageV1Report:
        report = V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            **report.summary,
            "authoritative_status": "accepted_rotation_shadow_snapshot_ready_without_mutating_the_current_primary_snapshot",
        }
        triage_rows = [
            {
                "component": "shadow_snapshot_visibility",
                "direction": "use the shadow snapshot to compare current and accepted top-level focus side by side",
            },
            {
                "component": "promotion_guard",
                "direction": "keep the primary snapshot unchanged while accepted rotation remains in shadow form only",
            },
            {
                "component": "consumer_review",
                "direction": "review the accepted shadow snapshot before deciding whether to promote the second-source rotation into primary consumers",
            },
        ]
        interpretation = [
            "The accepted state is now visible as a true shadow snapshot instead of only a packet preview.",
            "This keeps promotion disciplined while giving downstream users a realistic post-rotation view.",
        ]
        return V134ZPAShareZOInternalHotNewsAcceptedRotationShadowDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZPAShareZOInternalHotNewsAcceptedRotationShadowDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZPAShareZOInternalHotNewsAcceptedRotationShadowDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zp_a_share_zo_internal_hot_news_accepted_rotation_shadow_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
