from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JICommercialAerospaceBroaderAttentionEvidenceFrontierOpeningV1Report:
    summary: dict[str, Any]
    frontier_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "frontier_rows": self.frontier_rows,
            "interpretation": self.interpretation,
        }


class V134JICommercialAerospaceBroaderAttentionEvidenceFrontierOpeningV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.local_completion_path = (
            analysis_dir / "v134je_commercial_aerospace_event_attention_capital_local_completion_audit_v1.json"
        )
        self.local_handoff_path = (
            analysis_dir / "v134jh_commercial_aerospace_jg_local_handoff_direction_triage_v1.json"
        )
        self.evidence_source_path = (
            analysis_dir / "v134io_commercial_aerospace_true_selection_evidence_source_audit_v1.json"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_broader_attention_evidence_frontier_opening_v1.csv"
        )

    def _load_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def analyze(self) -> V134JICommercialAerospaceBroaderAttentionEvidenceFrontierOpeningV1Report:
        local_completion = self._load_json(self.local_completion_path)
        local_handoff = self._load_json(self.local_handoff_path)
        evidence_source = self._load_json(self.evidence_source_path)

        frontier_rows = [
            {
                "component": "board_local_event_attention_capital_route",
                "status": "frozen_input",
                "detail": local_handoff["summary"]["authoritative_status"],
            },
            {
                "component": "symbol_named_heat_source_expansion",
                "status": "protocol_open",
                "detail": "search for a second retained symbol-named hard heat source outside the exhausted local inventory",
            },
            {
                "component": "broader_attention_heat_evidence_expansion",
                "status": "protocol_open",
                "detail": "expand beyond board-local proxy evidence into thicker attention and heat evidence while staying supervision-only",
            },
            {
                "component": "expanded_symbol_attention_carrier_search",
                "status": "protocol_open",
                "detail": "expand candidate search beyond the current named local inventory without reopening execution or true selection",
            },
            {
                "component": "concept_purity_business_reference_layer",
                "status": "deferred_until_future_full_a_share_info",
                "detail": "user explicitly deferred broader fundamentals and concept-purity integration until fuller A-share information exists",
            },
            {
                "component": "capital_true_selection",
                "status": "still_blocked",
                "detail": "broader evidence frontier may support it later, but no promotion is allowed at opening",
            },
            {
                "component": "execution_authority",
                "status": "blocked",
                "detail": "the new frontier is supervision-only and does not inherit any execution permission",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(frontier_rows[0].keys()))
            writer.writeheader()
            writer.writerows(frontier_rows)

        summary = {
            "acceptance_posture": "freeze_v134ji_commercial_aerospace_broader_attention_evidence_frontier_opening_v1",
            "frontier_name": "broader_attention_evidence",
            "frontier_state": "opened_protocol_only",
            "frozen_input_route_count": 1,
            "protocol_open_count": 3,
            "deferred_component_count": 1,
            "execution_blocked": True,
            "opening_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the next lawful frontier after the frozen board-local route is broader attention evidence expansion: it opens as protocol-only, keeps the local route read-only, keeps capital_true_selection blocked, and defers concept-purity or full-A-share business-reference work until later coverage exists",
        }
        interpretation = [
            "V1.34JI does not reopen the exhausted local route. It opens the next evidence frontier in protocol form only.",
            "The core discipline is preserved: new evidence may expand the stack, but nothing here reactivates true-selection promotion or execution authority.",
        ]
        return V134JICommercialAerospaceBroaderAttentionEvidenceFrontierOpeningV1Report(
            summary=summary,
            frontier_rows=frontier_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JICommercialAerospaceBroaderAttentionEvidenceFrontierOpeningV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JICommercialAerospaceBroaderAttentionEvidenceFrontierOpeningV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ji_commercial_aerospace_broader_attention_evidence_frontier_opening_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
