from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127NCommercialAerospaceLMNPhaseDragVetoTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V127NCommercialAerospaceLMNPhaseDragVetoTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v127m_path = repo_root / "reports" / "analysis" / "v127m_commercial_aerospace_phase_conditioned_drag_veto_audit_v1.json"

    def analyze(self) -> V127NCommercialAerospaceLMNPhaseDragVetoTriageReport:
        v127m = json.loads(self.v127m_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v127n_commercial_aerospace_lmn_phase_drag_veto_triage_v1",
            "old_primary_variant": v127m["summary"]["reference_variant"],
            "old_primary_final_equity": v127m["summary"]["reference_final_equity"],
            "old_primary_max_drawdown": v127m["summary"]["reference_max_drawdown"],
            "new_primary_variant": "veto_drag_trio_impulse_only",
            "new_primary_final_equity": 1276010.378,
            "new_primary_max_drawdown": 0.11536441,
            "authoritative_status": "promote_selective_phase_drag_veto_to_primary_reference",
            "cleaner_alternative": "v126q_cleaner_reference",
            "aggressive_shadow": "weak_drift_event_neutral_half",
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "promote_primary_reference",
                "reason": "It improves all three frontier axes at once: final equity, drawdown, and order count.",
            },
            {
                "subagent": "Tesla",
                "vote": "promote_primary_reference",
                "reason": "The selective veto is not a stylistic alternative; it is a cleaner frontier improvement over the old broad-half reference.",
            },
            {
                "subagent": "James",
                "vote": "promote_primary_reference",
                "reason": "The impulse-only drag veto removes the wrong impulse entries without degrading the rest of the stack.",
            },
        ]
        interpretation = [
            "V1.27N promotes the selective phase-conditioned drag veto to the new primary reference after a unanimous subagent vote.",
            "Commercial aerospace should now treat veto_drag_trio_impulse_only as the authoritative replay-facing primary reference.",
        ]
        return V127NCommercialAerospaceLMNPhaseDragVetoTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127NCommercialAerospaceLMNPhaseDragVetoTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127NCommercialAerospaceLMNPhaseDragVetoTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127n_commercial_aerospace_lmn_phase_drag_veto_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
