from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JGCommercialAerospaceEventAttentionCapitalLocalHandoffPackageV1Report:
    summary: dict[str, Any]
    package_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "package_rows": self.package_rows,
            "interpretation": self.interpretation,
        }


class V134JGCommercialAerospaceEventAttentionCapitalLocalHandoffPackageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.completion_path = analysis_dir / "v134jf_commercial_aerospace_je_local_completion_direction_triage_v1.json"
        self.env_path = analysis_dir / "v134hu_commercial_aerospace_negative_environment_semantics_registry_v1.json"
        self.event_registry_path = analysis_dir / "v134hw_commercial_aerospace_event_attention_supervision_registry_v1.json"
        self.role_sep_path = analysis_dir / "v134ia_commercial_aerospace_event_attention_role_separation_audit_v1.json"
        self.heat_proxy_path = analysis_dir / "v134iy_commercial_aerospace_event_attention_heat_proxy_audit_v1.json"
        self.readiness_path = analysis_dir / "v134im_commercial_aerospace_capital_true_selection_readiness_audit_v1.json"
        self.source_inventory_path = analysis_dir / "v134jc_commercial_aerospace_symbol_named_heat_source_search_audit_v1.json"
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_event_attention_capital_local_handoff_package_v1.csv"
        )

    def _load_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def analyze(self) -> V134JGCommercialAerospaceEventAttentionCapitalLocalHandoffPackageV1Report:
        completion = self._load_json(self.completion_path)
        env_registry = self._load_json(self.env_path)
        event_registry = self._load_json(self.event_registry_path)
        role_sep = self._load_json(self.role_sep_path)
        heat_proxy = self._load_json(self.heat_proxy_path)
        readiness = self._load_json(self.readiness_path)
        source_inventory = self._load_json(self.source_inventory_path)

        package_rows = [
            {
                "component": "local_route_completion",
                "status": "frozen_for_handoff",
                "detail": completion["summary"]["authoritative_status"],
            },
            {
                "component": "negative_environment_semantics",
                "status": "retained",
                "detail": f"semantic_count = {env_registry['summary']['semantic_count']}",
            },
            {
                "component": "event_attention_registry",
                "status": "retained",
                "detail": f"registry_row_count = {event_registry['summary']['registry_row_count']}",
            },
            {
                "component": "role_separation_and_heat_proxy_layers",
                "status": "retained_as_local_only",
                "detail": f"soft_candidate_count = {role_sep['summary']['soft_candidate_count']}; strongest_soft_heat_proxy_symbol = {heat_proxy['summary']['strongest_soft_heat_proxy_symbol']}",
            },
            {
                "component": "capital_true_selection",
                "status": "still_blocked",
                "detail": f"remaining_hard_gap_count = {readiness['summary']['remaining_hard_gap_count']}",
            },
            {
                "component": "hard_heat_source_inventory",
                "status": "single_case_stopline",
                "detail": f"retained_symbol_named_heat_source_count = {source_inventory['summary']['retained_symbol_named_heat_source_count']}",
            },
            {
                "component": "future_progress_gate",
                "status": "future_evidence_expansion_only",
                "detail": "Do not reopen the local route without broader attention evidence or a new retained symbol-named hard heat source.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(package_rows[0].keys()))
            writer.writeheader()
            writer.writerows(package_rows)

        summary = {
            "acceptance_posture": "freeze_v134jg_commercial_aerospace_event_attention_capital_local_handoff_package_v1",
            "local_route_mainline_frozen": True,
            "capital_true_selection_blocked": True,
            "hard_heat_source_inventory_single_case": True,
            "future_handoff_ready": True,
            "handoff_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_event_attention_capital_local_handoff_package_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34JG packages the board-local event-attention-capital route for handoff without pretending that true-selection authority is solved.",
            "The point is to freeze the local semantics that are already real, keep promotion blocked, and make the next frontier explicitly evidence-driven rather than repetitive.",
        ]
        return V134JGCommercialAerospaceEventAttentionCapitalLocalHandoffPackageV1Report(
            summary=summary,
            package_rows=package_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JGCommercialAerospaceEventAttentionCapitalLocalHandoffPackageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JGCommercialAerospaceEventAttentionCapitalLocalHandoffPackageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jg_commercial_aerospace_event_attention_capital_local_handoff_package_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
