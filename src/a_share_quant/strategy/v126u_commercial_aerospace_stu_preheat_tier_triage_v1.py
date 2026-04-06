from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V126UCommercialAerospaceSTUPreheatTierTriageReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "interpretation": self.interpretation}


class V126UCommercialAerospaceSTUPreheatTierTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v126o_path = repo_root / "reports" / "analysis" / "v126o_commercial_aerospace_phase_geometry_walk_forward_shadow_replay_v1.json"
        self.v126q_path = repo_root / "reports" / "analysis" / "v126q_commercial_aerospace_pruned_phase_geometry_shadow_replay_v1.json"
        self.v126s_path = repo_root / "reports" / "analysis" / "v126s_commercial_aerospace_preheat_full_support_audit_v1.json"
        self.v126t_path = repo_root / "reports" / "analysis" / "v126t_commercial_aerospace_preheat_tiered_shadow_replay_v1.json"

    def analyze(self) -> V126UCommercialAerospaceSTUPreheatTierTriageReport:
        v126o = json.loads(self.v126o_path.read_text(encoding="utf-8"))["summary"]
        v126q = json.loads(self.v126q_path.read_text(encoding="utf-8"))["summary"]
        v126s = json.loads(self.v126s_path.read_text(encoding="utf-8"))["summary"]
        v126t = json.loads(self.v126t_path.read_text(encoding="utf-8"))["summary"]

        beats_v126o = v126t["final_equity"] >= v126o["final_equity"] and v126t["max_drawdown"] <= v126o["max_drawdown"]
        beats_v126q = v126t["final_equity"] >= v126q["final_equity"] and v126t["max_drawdown"] <= v126q["max_drawdown"]
        authoritative_status = (
            "retained_shadow_preheat_tier_candidate"
            if beats_v126q
            else "keep_existing_shadow_references_and_block_preheat_tier_promotion"
        )

        summary = {
            "acceptance_posture": "freeze_v126u_commercial_aerospace_stu_preheat_tier_triage_v1",
            "matured_preheat_full_on_20251224": v126s["matured_preheat_full_on_20251224"],
            "reference_v126o_final_equity": v126o["final_equity"],
            "reference_v126o_max_drawdown": v126o["max_drawdown"],
            "cleaner_v126q_final_equity": v126q["final_equity"],
            "cleaner_v126q_max_drawdown": v126q["max_drawdown"],
            "preheat_tier_v126t_final_equity": v126t["final_equity"],
            "preheat_tier_v126t_max_drawdown": v126t["max_drawdown"],
            "preheat_tier_v126t_executed_order_count": v126t["executed_order_count"],
            "beats_v126o_on_both_axes": beats_v126o,
            "beats_v126q_on_both_axes": beats_v126q,
            "authoritative_status": authoritative_status,
        }
        interpretation = [
            "V1.26U only promotes preheat-tier replay if lawful preheat full-support translates into replay economics that at least beat the cleaner V1.26Q reference on both return and drawdown.",
            "This prevents us from calling every earlier-entry variant progress just because it participates sooner.",
        ]
        return V126UCommercialAerospaceSTUPreheatTierTriageReport(summary=summary, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V126UCommercialAerospaceSTUPreheatTierTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126UCommercialAerospaceSTUPreheatTierTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126u_commercial_aerospace_stu_preheat_tier_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
