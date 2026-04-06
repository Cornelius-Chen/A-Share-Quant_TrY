from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134zs_a_share_internal_hot_news_accepted_rotation_shadow_change_signal_audit_v1 import (
    V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ZTAShareZSInternalHotNewsAcceptedRotationShadowChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ZTAShareZSInternalHotNewsAcceptedRotationShadowChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZTAShareZSInternalHotNewsAcceptedRotationShadowChangeDirectionTriageV1Report:
        report = V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            **report.summary,
            "authoritative_status": "accepted_rotation_shadow_delta_explicitly_measured_against_the_current_primary_control_packet",
        }
        triage_rows = [
            {
                "component": "opportunity_shadow_delta",
                "direction": "treat top opportunity theme change as an explicit shadow rotation delta rather than a silent merge consequence",
            },
            {
                "component": "symbol_shadow_delta",
                "direction": "treat top watch symbol change as an explicit shadow rotation delta requiring deliberate review",
            },
            {
                "component": "promotion_discipline",
                "direction": "use the shadow delta signal as the final check before deciding whether to promote the accepted rotation",
            },
        ]
        interpretation = [
            "The accepted rotation now has a dedicated delta signal against the current primary control state.",
            "This makes the promotion consequence explicit in one row.",
        ]
        return V134ZTAShareZSInternalHotNewsAcceptedRotationShadowChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZTAShareZSInternalHotNewsAcceptedRotationShadowChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZTAShareZSInternalHotNewsAcceptedRotationShadowChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zt_a_share_zs_internal_hot_news_accepted_rotation_shadow_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
