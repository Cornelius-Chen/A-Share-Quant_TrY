from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127DCommercialAerospaceABCPhaseAwareDownsideTriageReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "interpretation": self.interpretation}


class V127DCommercialAerospaceABCPhaseAwareDownsideTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v126z_path = repo_root / "reports" / "analysis" / "v126z_commercial_aerospace_wxy_shadow_stack_triage_v1.json"
        self.v127a_path = repo_root / "reports" / "analysis" / "v127a_commercial_aerospace_phase_aware_derisk_audit_v1.json"
        self.v127c_path = repo_root / "reports" / "analysis" / "v127c_commercial_aerospace_continuation_exhaustion_derisk_audit_v1.json"

    def analyze(self) -> V127DCommercialAerospaceABCPhaseAwareDownsideTriageReport:
        prior = json.loads(self.v126z_path.read_text(encoding="utf-8"))["summary"]
        v127a = json.loads(self.v127a_path.read_text(encoding="utf-8"))
        v127c = json.loads(self.v127c_path.read_text(encoding="utf-8"))
        a_best = next(row for row in v127a["variant_rows"] if row["variant"] == v127a["summary"]["best_variant"])
        c_best = next(row for row in v127c["variant_rows"] if row["variant"] == v127c["summary"]["best_variant"])

        promotes_aggressive_slot = (
            a_best["final_equity"] >= prior["retained_aggressive_shadow_final_equity"]
            and a_best["max_drawdown"] <= prior["retained_aggressive_shadow_max_drawdown"]
        )
        continuation_branch_blocked = (
            c_best["final_equity"] < a_best["final_equity"]
            and c_best["max_drawdown"] > a_best["max_drawdown"]
        )

        summary = {
            "acceptance_posture": "freeze_v127d_commercial_aerospace_abc_phase_aware_downside_triage_v1",
            "economic_reference_variant": prior["economic_reference_variant"],
            "cleaner_reference_variant": prior["cleaner_reference_variant"],
            "new_aggressive_shadow_variant": a_best["variant"] if promotes_aggressive_slot else prior["retained_aggressive_shadow_variant"],
            "new_aggressive_shadow_final_equity": a_best["final_equity"] if promotes_aggressive_slot else prior["retained_aggressive_shadow_final_equity"],
            "new_aggressive_shadow_max_drawdown": a_best["max_drawdown"] if promotes_aggressive_slot else prior["retained_aggressive_shadow_max_drawdown"],
            "blocked_variant": c_best["variant"],
            "blocked_variant_final_equity": c_best["final_equity"],
            "blocked_variant_max_drawdown": c_best["max_drawdown"],
            "same_family_stopline": continuation_branch_blocked,
            "authoritative_status": "replace_aggressive_shadow_with_v127a_and_block_same_family_narrowing",
        }
        interpretation = [
            "V1.27D freezes the latest commercial-aerospace downside family verdict: V1.27A upgrades the aggressive shadow slot, while V1.27C continuation-exhaustion narrowing is blocked.",
            "This sets a near-stopline on further tuning inside the same phase-aware sell family; next downside work must be orthogonal rather than narrower rewrites of the same grammar.",
        ]
        return V127DCommercialAerospaceABCPhaseAwareDownsideTriageReport(
            summary=summary,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V127DCommercialAerospaceABCPhaseAwareDownsideTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127DCommercialAerospaceABCPhaseAwareDownsideTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127d_commercial_aerospace_abc_phase_aware_downside_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
