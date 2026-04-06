from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128JCommercialAerospaceIJKPostPrimaryDirectionTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V128JCommercialAerospaceIJKPostPrimaryDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.primary_path = repo_root / "reports" / "analysis" / "v128i_commercial_aerospace_hij_tail_repair_promotion_triage_v1.json"

    def analyze(self) -> V128JCommercialAerospaceIJKPostPrimaryDirectionTriageReport:
        payload = json.loads(self.primary_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v128j_commercial_aerospace_ijk_post_primary_direction_triage_v1",
            "current_primary_variant": payload["summary"]["new_primary_variant"],
            "current_primary_final_equity": payload["summary"]["new_primary_final_equity"],
            "current_primary_max_drawdown": payload["summary"]["new_primary_max_drawdown"],
            "authoritative_next_step": "stop_local_micro_tuning_and_begin_portability_packaging",
            "stop_doing": [
                "do_not_continue_board_local_micro_tuning",
                "do_not_open_new_local_family_before_packaging",
                "do_not_reopen_old_primary_branches_without_cross_board_evidence",
            ],
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "B_portability_packaging",
                "reason": "The local frontier has improved enough that the highest-value next step is transferability, not another local squeeze.",
            },
            {
                "subagent": "Tesla",
                "vote": "B_portability_packaging",
                "reason": "The board-specific grammar is now mature enough to be turned into a migration-ready template.",
            },
            {
                "subagent": "James",
                "vote": "B_portability_packaging",
                "reason": "Further commercial-aerospace-only tuning now has lower marginal value than testing whether the grammar ports.",
            },
        ]
        interpretation = [
            "V1.28J freezes the post-primary direction after commercial aerospace reached a locally mature replay-facing grammar.",
            "The board should now shift from local optimization to portability packaging so the learned execution skeleton can be tested elsewhere without mixing archetypes.",
        ]
        return V128JCommercialAerospaceIJKPostPrimaryDirectionTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128JCommercialAerospaceIJKPostPrimaryDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128JCommercialAerospaceIJKPostPrimaryDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128j_commercial_aerospace_ijk_post_primary_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
