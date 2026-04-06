from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JCommercialAerospacePhase2BroaderHitWideningProtocolReport:
    summary: dict[str, Any]
    protocol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "protocol_rows": self.protocol_rows,
            "interpretation": self.interpretation,
        }


class V134JCommercialAerospacePhase2BroaderHitWideningProtocolAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.review_path = analysis_dir / "v134i_commercial_aerospace_phase2_seed_supervision_review_v1.json"
        self.det_path = analysis_dir / "v134g_commercial_aerospace_intraday_seed_simulator_deterministic_audit_v1.json"
        self.expand_path = analysis_dir / "v132k_commercial_aerospace_local_1min_session_expansion_audit_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_phase2_broader_hit_widening_protocol_v1.csv"
        )

    def analyze(self) -> V134JCommercialAerospacePhase2BroaderHitWideningProtocolReport:
        review = json.loads(self.review_path.read_text(encoding="utf-8"))
        det = json.loads(self.det_path.read_text(encoding="utf-8"))
        expand = json.loads(self.expand_path.read_text(encoding="utf-8"))

        protocol_rows = [
            {
                "protocol_component": "widening_scope",
                "status": "approved_with_guardrails",
                "detail": (
                    f"Expand from canonical seeds to broader-hit sessions only: "
                    f"{expand['summary']['expanded_hit_count']} hit sessions, not {expand['summary']['expanded_session_count']} all sessions."
                ),
            },
            {
                "protocol_component": "allowed_execution_tiers",
                "status": "approved_with_guardrails",
                "detail": "Only reversal_watch and severe_override_positive may enter broader phase-2 simulation.",
            },
            {
                "protocol_component": "mild_tier_handling",
                "status": "blocked_from_execution",
                "detail": "mild_override_watch stays governance-only and may only feed do-not-readd logic.",
            },
            {
                "protocol_component": "clock_and_cost_model",
                "status": "mandatory",
                "detail": "Keep minute-close trigger, next-bar-open fill, and the same frozen EOD cost model with no local modifications.",
            },
            {
                "protocol_component": "determinism_gate",
                "status": "mandatory",
                "detail": f"double_run_exact_match = {det['summary']['double_run_exact_match']} must remain true before and after widening.",
            },
            {
                "protocol_component": "replay_boundary",
                "status": "still_blocked",
                "detail": "Broader-hit widening remains inside phase 2 and does not authorize phase-3 replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(protocol_rows[0].keys()))
            writer.writeheader()
            writer.writerows(protocol_rows)

        summary = {
            "acceptance_posture": "freeze_v134j_commercial_aerospace_phase2_broader_hit_widening_protocol_v1",
            "canonical_seed_count": review["summary"]["seed_session_count"],
            "broader_hit_session_count": expand["summary"]["expanded_hit_count"],
            "all_session_count": expand["summary"]["expanded_session_count"],
            "allowed_widening_surface": "broader_hit_sessions_only",
            "allowed_execution_tiers": ["reversal_watch", "severe_override_positive"],
            "blocked_execution_tiers": ["mild_override_watch"],
            "phase2_widening_status": "approved_with_guardrails",
            "protocol_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_phase2_broader_hit_widening_protocol_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34J turns the seed supervision review into an explicit widening protocol.",
            "The protocol does not open replay. It only says that, if phase 2 continues, the next lawful expansion is to broader-hit sessions under the same clock, cost, and governance constraints.",
        ]
        return V134JCommercialAerospacePhase2BroaderHitWideningProtocolReport(
            summary=summary,
            protocol_rows=protocol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JCommercialAerospacePhase2BroaderHitWideningProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JCommercialAerospacePhase2BroaderHitWideningProtocolAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134j_commercial_aerospace_phase2_broader_hit_widening_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
