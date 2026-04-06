from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134zw_a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_audit_v1 import (
    V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ZXAShareZWInternalHotNewsPrimaryConsumerRotationAcceptanceDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ZXAShareZWInternalHotNewsPrimaryConsumerRotationAcceptanceDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZXAShareZWInternalHotNewsPrimaryConsumerRotationAcceptanceDirectionTriageV1Report:
        report = V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            **report.summary,
            "authoritative_status": "primary_consumer_rotation_has_been_explicitly_accepted_and_primary_top_consumer_overrides_may_now_apply",
        }
        triage_rows = [
            {"component": "acceptance_registry", "direction": "treat this accepted registry as the single explicit approval artifact for the p1 focus rotation"},
            {"component": "primary_snapshot_override", "direction": "allow primary snapshot top opportunity and top watch to rotate according to the accepted state"},
            {"component": "control_consumer_override", "direction": "propagate the accepted top focus into primary control consumers after the snapshot override lands"},
        ]
        interpretation = [
            "The process has moved from planning to execution because the manual acceptance artifact now exists.",
            "Subsequent top-consumer changes are now expected behavior rather than shadow-only previews.",
        ]
        return V134ZXAShareZWInternalHotNewsPrimaryConsumerRotationAcceptanceDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V134ZXAShareZWInternalHotNewsPrimaryConsumerRotationAcceptanceDirectionTriageV1Report) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZXAShareZWInternalHotNewsPrimaryConsumerRotationAcceptanceDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zx_a_share_zw_internal_hot_news_primary_consumer_rotation_acceptance_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
