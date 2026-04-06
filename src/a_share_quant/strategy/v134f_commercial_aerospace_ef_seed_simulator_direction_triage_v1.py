from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FCommercialAerospaceEFSeedSimulatorDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FCommercialAerospaceEFSeedSimulatorDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.seed_sim_path = (
            repo_root / "reports" / "analysis" / "v134c_commercial_aerospace_intraday_seed_simulator_v1.json"
        )
        self.attr_path = (
            repo_root / "reports" / "analysis" / "v134e_commercial_aerospace_intraday_seed_simulator_attribution_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ef_seed_simulator_direction_triage_v1.csv"
        )

    def analyze(self) -> V134FCommercialAerospaceEFSeedSimulatorDirectionTriageReport:
        seed_sim = json.loads(self.seed_sim_path.read_text(encoding="utf-8"))
        attr = json.loads(self.attr_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "canonical_seed_simulator",
                "status": "retain_and_continue_inside_phase_2",
                "detail": f"simulated_order_count = {seed_sim['summary']['simulated_order_count']}",
            },
            {
                "component": "chronology_boundary",
                "status": "accepted_after_correction",
                "detail": "seed actions now execute in trigger-minute order rather than tier-name order",
            },
            {
                "component": "seed_attribution_signal",
                "status": "retain_for_direction",
                "detail": (
                    f"top_tier = {attr['summary']['top_tier_by_same_day_loss_avoided']}, "
                    f"top_symbol = {attr['summary']['top_symbol_by_same_day_loss_avoided']}"
                ),
            },
            {
                "component": "broader_session_expansion",
                "status": "still_blocked",
                "detail": "the branch should first finish deterministic/attribution understanding on canonical seeds before widening phase 2",
            },
            {
                "component": "phase_3_replay_lane",
                "status": "still_blocked",
                "detail": "seed simulator plus attribution does not authorize opening an intraday replay lane",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134f_commercial_aerospace_ef_seed_simulator_direction_triage_v1",
            "authoritative_status": "retain_seed_simulator_and_attribution_inside_phase_2_but_keep_broader_expansion_and_replay_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34F turns the corrected seed simulator plus attribution into the next phase-2 direction triage.",
            "The result is constructive but still narrow: canonical seed understanding improves, while broader expansion and replay binding remain blocked.",
        ]
        return V134FCommercialAerospaceEFSeedSimulatorDirectionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FCommercialAerospaceEFSeedSimulatorDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FCommercialAerospaceEFSeedSimulatorDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134f_commercial_aerospace_ef_seed_simulator_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
