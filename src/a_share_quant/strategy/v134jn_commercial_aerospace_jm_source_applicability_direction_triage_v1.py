from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134jm_commercial_aerospace_broader_attention_source_applicability_audit_v1 import (
    V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Analyzer,
)


@dataclass(slots=True)
class V134JNCommercialAerospaceJMSourceApplicabilityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134JNCommercialAerospaceJMSourceApplicabilityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134JNCommercialAerospaceJMSourceApplicabilityDirectionTriageV1Report:
        audit = V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "decisive_event_registry_v1",
                "direction": "promote_as_first_same_plane_broader_attention_expansion_surface",
            },
            {
                "component": "market_snapshot_inventory_v6",
                "direction": "retain_as_structural_prior_do_not_treat_as_2026_same_plane_evidence",
            },
            {
                "component": "theme_snapshot_inventory_v7",
                "direction": "retain_as_structural_prior_do_not_treat_as_2026_same_plane_evidence",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_while_same_plane_broader_attention_evidence_remains_thin",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134jn_commercial_aerospace_jm_source_applicability_direction_triage_v1",
            "same_plane_ready_source_count": audit.summary["same_plane_ready_source_count"],
            "structural_prior_only_source_count": audit.summary["structural_prior_only_source_count"],
            "authoritative_status": "treat_decisive_event_registry_as_the_first_same_plane_broader_attention_source_and_keep_snapshots_as_structural_priors_only",
        }
        interpretation = [
            "V1.34JN converts source applicability into immediate direction.",
            "The next lawful expansion should start from the 2026-aligned decisive-event surface, while the 2024 snapshots stay as priors and do not receive same-plane evidentiary authority.",
        ]
        return V134JNCommercialAerospaceJMSourceApplicabilityDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JNCommercialAerospaceJMSourceApplicabilityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JNCommercialAerospaceJMSourceApplicabilityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jn_commercial_aerospace_jm_source_applicability_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
