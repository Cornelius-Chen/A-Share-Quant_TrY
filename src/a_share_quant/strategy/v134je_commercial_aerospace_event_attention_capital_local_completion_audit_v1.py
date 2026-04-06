from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JECommercialAerospaceEventAttentionCapitalLocalCompletionAuditV1Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134JECommercialAerospaceEventAttentionCapitalLocalCompletionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.route_path = analysis_dir / "v134hs_commercial_aerospace_training_target_route_audit_v1.json"
        self.env_path = analysis_dir / "v134hu_commercial_aerospace_negative_environment_semantics_registry_v1.json"
        self.event_registry_path = analysis_dir / "v134hw_commercial_aerospace_event_attention_supervision_registry_v1.json"
        self.role_sep_path = analysis_dir / "v134ia_commercial_aerospace_event_attention_role_separation_audit_v1.json"
        self.heat_proxy_path = analysis_dir / "v134iy_commercial_aerospace_event_attention_heat_proxy_audit_v1.json"
        self.readiness_path = analysis_dir / "v134im_commercial_aerospace_capital_true_selection_readiness_audit_v1.json"
        self.source_inventory_path = analysis_dir / "v134jc_commercial_aerospace_symbol_named_heat_source_search_audit_v1.json"
        self.evidence_source_path = analysis_dir / "v134io_commercial_aerospace_true_selection_evidence_source_audit_v1.json"
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_event_attention_capital_local_completion_v1.csv"
        )

    def _load_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def analyze(self) -> V134JECommercialAerospaceEventAttentionCapitalLocalCompletionAuditV1Report:
        route = self._load_json(self.route_path)
        env_registry = self._load_json(self.env_path)
        event_registry = self._load_json(self.event_registry_path)
        role_sep = self._load_json(self.role_sep_path)
        heat_proxy = self._load_json(self.heat_proxy_path)
        readiness = self._load_json(self.readiness_path)
        source_inventory = self._load_json(self.source_inventory_path)
        evidence_source = self._load_json(self.evidence_source_path)

        status_rows = [
            {
                "component": "negative_environment_semantics",
                "status": "frozen_complete_for_local_supervision",
                "detail": f"semantic_count = {env_registry['summary']['semantic_count']}",
            },
            {
                "component": "event_attention_registry",
                "status": "frozen_complete_for_local_supervision",
                "detail": f"registry_row_count = {event_registry['summary']['registry_row_count']}",
            },
            {
                "component": "role_separation_layer",
                "status": "frozen_complete_for_local_supervision",
                "detail": f"soft_candidate_count = {role_sep['summary']['soft_candidate_count']}",
            },
            {
                "component": "heat_proxy_layer",
                "status": "retain_as_local_role_clarity_only",
                "detail": f"strongest_soft_heat_proxy_symbol = {heat_proxy['summary']['strongest_soft_heat_proxy_symbol']}",
            },
            {
                "component": "capital_true_selection",
                "status": "still_blocked",
                "detail": f"remaining_hard_gap_count = {readiness['summary']['remaining_hard_gap_count']}",
            },
            {
                "component": "symbol_named_hard_heat_source_inventory",
                "status": "single_case_stopline",
                "detail": f"retained_symbol_named_heat_source_count = {source_inventory['summary']['retained_symbol_named_heat_source_count']}",
            },
            {
                "component": "local_evidence_source",
                "status": "locally_exhausted",
                "detail": f"current_local_route_exhausted = {evidence_source['summary']['current_local_route_exhausted']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "acceptance_posture": "freeze_v134je_commercial_aerospace_event_attention_capital_local_completion_audit_v1",
            "route_phase_count": route["summary"]["roadmap_phase_count"],
            "negative_environment_ready": True,
            "event_attention_local_stack_ready": True,
            "capital_true_selection_still_blocked": True,
            "single_hard_heat_source_stopline": True,
            "current_local_route_exhausted": evidence_source["summary"]["current_local_route_exhausted"],
            "completion_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_event_attention_capital_local_completion_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34JE asks whether the board-local event-attention-capital branch is still in open exploration or has reached a supervision-level completion stopline.",
            "The answer is that the local branch is complete enough to freeze: local role semantics are rich, but true-selection promotion remains blocked and the event inventory is locally exhausted.",
        ]
        return V134JECommercialAerospaceEventAttentionCapitalLocalCompletionAuditV1Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JECommercialAerospaceEventAttentionCapitalLocalCompletionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JECommercialAerospaceEventAttentionCapitalLocalCompletionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134je_commercial_aerospace_event_attention_capital_local_completion_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
