from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HCommercialAerospaceGHSeedDeterministicDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HCommercialAerospaceGHSeedDeterministicDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134g_commercial_aerospace_intraday_seed_simulator_deterministic_audit_v1.json"
        )
        self.attr_path = (
            repo_root / "reports" / "analysis" / "v134e_commercial_aerospace_intraday_seed_simulator_attribution_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_gh_seed_deterministic_direction_triage_v1.csv"
        )

    def analyze(self) -> V134HCommercialAerospaceGHSeedDeterministicDirectionTriageReport:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        attr = json.loads(self.attr_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "seed_simulator_determinism",
                "status": "accepted",
                "detail": f"double_run_exact_match = {audit['summary']['double_run_exact_match']}",
            },
            {
                "component": "seed_clock_monotonicity",
                "status": "accepted",
                "detail": (
                    f"monotonic_fill_violation_count = {audit['summary']['monotonic_fill_violation_count']}, "
                    f"post_flat_action_violation_count = {audit['summary']['post_flat_action_violation_count']}"
                ),
            },
            {
                "component": "seed_benefit_concentration",
                "status": "retain_for_phase_2_understanding",
                "detail": (
                    f"same_day_loss_avoided_total = {attr['summary']['same_day_loss_avoided_total']}, "
                    f"top_symbol = {attr['summary']['top_symbol_by_same_day_loss_avoided']}"
                ),
            },
            {
                "component": "broader_session_phase_2_expansion",
                "status": "still_blocked",
                "detail": "deterministic seeds improve trust, but broader session simulation still requires an explicit widening protocol",
            },
            {
                "component": "phase_3_replay_lane",
                "status": "still_blocked",
                "detail": "deterministic seed simulation is a phase-2 maturity signal only, not a replay-binding authorization",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134h_commercial_aerospace_gh_seed_deterministic_direction_triage_v1",
            "authoritative_status": "retain_deterministic_seed_simulation_inside_phase_2_but_keep_expansion_and_replay_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34H converts the deterministic seed audit into the next phase-2 direction judgment.",
            "The seed simulator is now stable enough to be trusted as a narrow infrastructure object, but not yet broad enough to justify wider simulation or replay binding.",
        ]
        return V134HCommercialAerospaceGHSeedDeterministicDirectionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HCommercialAerospaceGHSeedDeterministicDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HCommercialAerospaceGHSeedDeterministicDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134h_commercial_aerospace_gh_seed_deterministic_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
