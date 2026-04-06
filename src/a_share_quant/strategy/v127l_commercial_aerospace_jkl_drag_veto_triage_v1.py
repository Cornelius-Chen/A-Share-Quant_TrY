from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127LCommercialAerospaceJKLDragVetoTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V127LCommercialAerospaceJKLDragVetoTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v127k_path = repo_root / "reports" / "analysis" / "v127k_commercial_aerospace_chronic_drag_symbol_veto_audit_v1.json"

    def analyze(self) -> V127LCommercialAerospaceJKLDragVetoTriageReport:
        v127k = json.loads(self.v127k_path.read_text(encoding="utf-8"))
        veto_trio_row = next(
            row for row in v127k["variant_rows"]
            if row["variant"] == "veto_688066_002085_688523"
        )
        summary = {
            "acceptance_posture": "freeze_v127l_commercial_aerospace_jkl_drag_veto_triage_v1",
            "reference_variant": v127k["summary"]["reference_variant"],
            "reference_final_equity": v127k["summary"]["reference_final_equity"],
            "reference_max_drawdown": v127k["summary"]["reference_max_drawdown"],
            "veto_trio_variant": veto_trio_row["variant"],
            "veto_trio_final_equity": veto_trio_row["final_equity"],
            "veto_trio_max_drawdown": veto_trio_row["max_drawdown"],
            "authoritative_status": "blocked_do_not_replace_cleaner_slot",
            "next_step": "phase_conditioned_drag_veto_audit",
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "blocked",
                "reason": "Global chronic-drag veto gives up too much economic participation and does not beat the existing cleaner slot.",
            },
            {
                "subagent": "Tesla",
                "vote": "retain_cleaner_candidate",
                "reason": "The full drag-trio veto offers a real drawdown improvement for a small equity give-back and is at least cleaner-slot worthy.",
            },
            {
                "subagent": "James",
                "vote": "blocked",
                "reason": "The veto is too blunt; it removes symbols that still help in some phases and should not replace the cleaner reference.",
            },
        ]
        interpretation = [
            "V1.27L freezes the global chronic-drag veto as blocked after a 2:1 subagent vote.",
            "The next attribution-driven branch is phase-conditioned drag veto, not full-symbol exclusion.",
        ]
        return V127LCommercialAerospaceJKLDragVetoTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127LCommercialAerospaceJKLDragVetoTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127LCommercialAerospaceJKLDragVetoTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127l_commercial_aerospace_jkl_drag_veto_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
