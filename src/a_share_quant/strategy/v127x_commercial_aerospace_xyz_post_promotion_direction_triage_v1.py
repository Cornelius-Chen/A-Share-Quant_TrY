from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127XCommercialAerospaceXYZPostPromotionDirectionTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V127XCommercialAerospaceXYZPostPromotionDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v127w_path = repo_root / "reports" / "analysis" / "v127w_commercial_aerospace_wxy_window_derisk_promotion_triage_v1.json"

    def analyze(self) -> V127XCommercialAerospaceXYZPostPromotionDirectionTriageReport:
        payload = json.loads(self.v127w_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v127x_commercial_aerospace_xyz_post_promotion_direction_triage_v1",
            "current_primary_variant": payload["summary"]["new_primary_variant"],
            "current_primary_final_equity": payload["summary"]["new_primary_final_equity"],
            "current_primary_max_drawdown": payload["summary"]["new_primary_max_drawdown"],
            "authoritative_next_step": "stronger_walk_forward_and_robustness_audit",
            "stop_doing": [
                "do_not_open_new_family_yet",
                "do_not_continue_symbol_micro_tuning",
                "do_not_assume_long_term_freeze_without_robustness",
            ],
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "stronger_walk_forward_and_robustness_audit",
                "reason": "The latest frontier improvement should be tested for chronology robustness before further promotion or freeze.",
            },
            {
                "subagent": "Tesla",
                "vote": "stronger_walk_forward_and_robustness_audit",
                "reason": "The current primary is strong enough that the highest-value next step is to rule out window-specific luck.",
            },
            {
                "subagent": "James",
                "vote": "stronger_walk_forward_and_robustness_audit",
                "reason": "Attribution can wait; what matters now is whether the new primary survives harder robustness checks.",
            },
        ]
        interpretation = [
            "V1.27X freezes the unanimous post-promotion direction after the new primary reference was upgraded.",
            "Commercial aerospace should now move to stronger walk-forward and robustness audits rather than more local tuning.",
        ]
        return V127XCommercialAerospaceXYZPostPromotionDirectionTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127XCommercialAerospaceXYZPostPromotionDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127XCommercialAerospaceXYZPostPromotionDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127x_commercial_aerospace_xyz_post_promotion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
