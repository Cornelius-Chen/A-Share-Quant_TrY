from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128ICommercialAerospaceHIJTailRepairPromotionTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V128ICommercialAerospaceHIJTailRepairPromotionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = repo_root / "reports" / "analysis" / "v128h_commercial_aerospace_post_window_tail_repair_audit_v1.json"

    def analyze(self) -> V128ICommercialAerospaceHIJTailRepairPromotionTriageReport:
        payload = json.loads(self.audit_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v128i_commercial_aerospace_hij_tail_repair_promotion_triage_v1",
            "old_primary_variant": payload["summary"]["reference_variant"],
            "old_primary_final_equity": payload["summary"]["reference_final_equity"],
            "old_primary_max_drawdown": payload["summary"]["reference_max_drawdown"],
            "new_primary_variant": "tail_weakdrift_full",
            "new_primary_final_equity": 1309426.5555,
            "new_primary_max_drawdown": 0.09309927,
            "authoritative_status": "promote_tail_weakdrift_full_to_primary_reference",
            "canonical_name_rationale": "tail_weakdrift_full_is_the_minimal_and_sufficient_increment",
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "promote_primary_reference",
                "canonical_name": "tail_weakdrift_full",
                "reason": "It raises final equity without increasing drawdown and does so with fewer trades.",
            },
            {
                "subagent": "Tesla",
                "vote": "promote_primary_reference",
                "canonical_name": "tail_weakdrift_full",
                "reason": "The real incremental edge is post-window weak-drift full selling; wider labels would overstate what actually earned its keep.",
            },
            {
                "subagent": "James",
                "vote": "promote_primary_reference",
                "canonical_name": "tail_weakdrift_full",
                "reason": "Sentiment-full and impulse-full extras did not add more economic value, so the canonical name should stay narrow.",
            },
        ]
        interpretation = [
            "V1.28I promotes the successful post-window tail repair to the new commercial-aerospace primary reference.",
            "The new primary is now a two-stage downside grammar: deeper main-window impulse-target selling plus post-window weak-drift full selling.",
        ]
        return V128ICommercialAerospaceHIJTailRepairPromotionTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128ICommercialAerospaceHIJTailRepairPromotionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128ICommercialAerospaceHIJTailRepairPromotionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128i_commercial_aerospace_hij_tail_repair_promotion_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
