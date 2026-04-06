from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134APCommercialAerospaceAOLocalDeferralDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134APCommercialAerospaceAOLocalDeferralDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ao_local_deferral_direction_triage_v1.csv"
        )

    def analyze(self) -> V134APCommercialAerospaceAOLocalDeferralDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        same_day_delta = float(audit["summary"]["best_same_day_loss_avoided_delta_total"])
        rebound_saved = float(audit["summary"]["best_rebound_cost_saved_5d_total"])
        impacted = int(audit["summary"]["best_impacted_case_count"])
        promotable = same_day_delta > 0 and rebound_saved >= 0 and impacted > 0

        triage_rows = [
            {
                "component": "local_reversal_deferral_expression",
                "status": "promote_inside_phase2_wider_reference" if promotable else "retain_as_supervision_only",
                "detail": (
                    f"same_day_delta = {same_day_delta}, rebound_saved_5d = {rebound_saved}, impacted_cases = {impacted}"
                ),
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "The local deferral expression does not authorize any surface growth.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "The local deferral expression remains phase-2 shadow-only.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134ap_commercial_aerospace_ao_local_deferral_direction_triage_v1",
            "authoritative_status": (
                "promote_local_reversal_deferral_inside_phase2_wider_reference"
                if promotable
                else "retain_local_reversal_deferral_as_supervision_only"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AP decides whether the local reversal-deferral expression is good enough to replace the current wider reference on the same fixed broader-hit surface.",
            "Promotion still remains inside phase 2 and does not change the blocked replay boundary.",
        ]
        return V134APCommercialAerospaceAOLocalDeferralDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134APCommercialAerospaceAOLocalDeferralDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134APCommercialAerospaceAOLocalDeferralDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ap_commercial_aerospace_ao_local_deferral_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
