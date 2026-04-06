from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128GCommercialAerospaceFGHPostPromotionDirectionTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V128GCommercialAerospaceFGHPostPromotionDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.portability_path = repo_root / "reports" / "analysis" / "v128c_commercial_aerospace_current_primary_portability_audit_v1.json"
        self.promotion_path = repo_root / "reports" / "analysis" / "v128f_commercial_aerospace_efg_main_window_downside_promotion_triage_v1.json"

    def analyze(self) -> V128GCommercialAerospaceFGHPostPromotionDirectionTriageReport:
        portability = json.loads(self.portability_path.read_text(encoding="utf-8"))
        promotion = json.loads(self.promotion_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v128g_commercial_aerospace_fgh_post_promotion_direction_triage_v1",
            "current_primary_variant": promotion["summary"]["new_primary_variant"],
            "current_primary_final_equity": promotion["summary"]["new_primary_final_equity"],
            "current_primary_max_drawdown": promotion["summary"]["new_primary_max_drawdown"],
            "main_window_delta_new_minus_old": portability["summary"]["main_window_delta_new_minus_old"],
            "post_window_delta_new_minus_old": portability["summary"]["post_window_delta_new_minus_old"],
            "authoritative_next_step": "post_window_tail_repair",
            "secondary_followup": "return_to_main_window_only_if_tail_branch_hits_stopline_fast",
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "B_post_window_tail_repair",
                "reason": "Main-window edge has already been harvested repeatedly; the remaining visible leak is in the post-window tail.",
            },
            {
                "subagent": "Tesla",
                "vote": "A_main_window_downside_grammar",
                "reason": "Main-window economics are still larger in absolute terms, but this is now the minority view.",
            },
            {
                "subagent": "James",
                "vote": "B_post_window_tail_repair",
                "reason": "The post-window giveback is now the cleanest remaining repair target after the main-window promotion succeeded.",
            },
        ]
        interpretation = [
            "V1.28G resolves the first direction split after the main-window deeper downside variant was promoted to current primary.",
            "The majority view is to move to post-window tail repair because the main-window branch has already delivered multiple consecutive frontier improvements.",
        ]
        return V128GCommercialAerospaceFGHPostPromotionDirectionTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128GCommercialAerospaceFGHPostPromotionDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128GCommercialAerospaceFGHPostPromotionDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128g_commercial_aerospace_fgh_post_promotion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
