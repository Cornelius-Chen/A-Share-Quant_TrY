from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127FCommercialAerospaceDEFOrthogonalDownsidePromotionTriageReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "interpretation": self.interpretation}


class V127FCommercialAerospaceDEFOrthogonalDownsidePromotionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v126o_path = repo_root / "reports" / "analysis" / "v126o_commercial_aerospace_phase_geometry_walk_forward_shadow_replay_v1.json"
        self.v126q_path = repo_root / "reports" / "analysis" / "v126q_commercial_aerospace_pruned_phase_geometry_shadow_replay_v1.json"
        self.v127e_path = repo_root / "reports" / "analysis" / "v127e_commercial_aerospace_orthogonal_downside_execution_scan_v1.json"

    def analyze(self) -> V127FCommercialAerospaceDEFOrthogonalDownsidePromotionTriageReport:
        v126o = json.loads(self.v126o_path.read_text(encoding="utf-8"))["summary"]
        v126q = json.loads(self.v126q_path.read_text(encoding="utf-8"))["summary"]
        v127e = json.loads(self.v127e_path.read_text(encoding="utf-8"))
        broad = next(row for row in v127e["variant_rows"] if row["variant"] == "broad_half_reference")
        weak_drift = next(row for row in v127e["variant_rows"] if row["variant"] == "weak_drift_event_neutral_half")
        overdrive = next(row for row in v127e["variant_rows"] if row["variant"] == "overdrive_continuation_half")

        broad_beats_v126o = broad["final_equity"] >= v126o["final_equity"] and broad["max_drawdown"] <= v126o["max_drawdown"]
        broad_beats_v126q = broad["final_equity"] >= v126q["final_equity"] and broad["max_drawdown"] <= v126q["max_drawdown"]

        summary = {
            "acceptance_posture": "freeze_v127f_commercial_aerospace_def_orthogonal_downside_promotion_triage_v1",
            "superseded_reference_variant": "v126o_economic_reference",
            "cleaner_alternative_variant": "v126q_cleaner_reference",
            "new_primary_reference_variant": broad["variant"],
            "new_primary_reference_final_equity": broad["final_equity"],
            "new_primary_reference_max_drawdown": broad["max_drawdown"],
            "new_primary_reference_executed_order_count": broad["executed_order_count"],
            "retained_aggressive_shadow_variant": weak_drift["variant"],
            "retained_aggressive_shadow_final_equity": weak_drift["final_equity"],
            "retained_aggressive_shadow_max_drawdown": weak_drift["max_drawdown"],
            "retained_aggressive_shadow_executed_order_count": weak_drift["executed_order_count"],
            "blocked_variant": overdrive["variant"],
            "blocked_variant_final_equity": overdrive["final_equity"],
            "blocked_variant_max_drawdown": overdrive["max_drawdown"],
            "broad_beats_old_reference": broad_beats_v126o,
            "broad_beats_cleaner_reference": broad_beats_v126q,
            "authoritative_status": "promote_v127e_broad_half_as_primary_reference_and_freeze_new_shadow_stack",
        }
        interpretation = [
            "V1.27F freezes the first commercial-aerospace orthogonal downside family that actually improves the replay frontier.",
            "Broad-half with expanded downside semantics is promoted because it beats both the prior economic reference and the cleaner reference on return and drawdown simultaneously.",
            "Weak-drift-event-neutral remains only the aggressive shadow; overdrive-continuation is blocked.",
        ]
        return V127FCommercialAerospaceDEFOrthogonalDownsidePromotionTriageReport(
            summary=summary,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V127FCommercialAerospaceDEFOrthogonalDownsidePromotionTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127FCommercialAerospaceDEFOrthogonalDownsidePromotionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127f_commercial_aerospace_def_orthogonal_downside_promotion_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
