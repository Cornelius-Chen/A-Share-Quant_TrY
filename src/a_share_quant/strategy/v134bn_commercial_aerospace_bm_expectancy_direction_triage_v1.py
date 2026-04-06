from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BNCommercialAerospaceBMExpectancyDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BNCommercialAerospaceBMExpectancyDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_bm_expectancy_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BNCommercialAerospaceBMExpectancyDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        summary = audit["summary"]
        triage_rows = [
            {
                "component": "unlock_worthy_expectancy",
                "status": "retained_as_positive_board_state",
                "detail": (
                    f"count = {summary['unlock_worthy_count']}, "
                    f"mean_forward_20d = {summary['unlock_worthy_mean_forward_20d']}, "
                    f"mean_rr20 = {summary['unlock_worthy_mean_rr20']}."
                ),
            },
            {
                "component": "false_bounce_only_expectancy",
                "status": "retained_as_negative_board_state",
                "detail": (
                    f"count = {summary['false_bounce_only_count']}, "
                    f"mean_forward_20d = {summary['false_bounce_only_mean_forward_20d']}, "
                    f"mean_rr20 = {summary['false_bounce_only_mean_rr20']}."
                ),
            },
            {
                "component": "lockout_worthy_expectancy",
                "status": "retained_as_top_level_veto_state",
                "detail": (
                    f"count = {summary['lockout_worthy_count']}, "
                    f"mean_forward_20d = {summary['lockout_worthy_mean_forward_20d']}, "
                    f"mean_rr20 = {summary['lockout_worthy_mean_rr20']}."
                ),
            },
            {
                "component": "shape_only_judgment",
                "status": "demoted",
                "detail": "Board state should now be discussed in expectancy / reward-risk terms first, not only in shape terms.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        out_summary = {
            "acceptance_posture": "freeze_v134bn_commercial_aerospace_bm_expectancy_direction_triage_v1",
            "authoritative_status": "freeze_board_expectancy_supervision_and_use_expectancy_as_board_level_reduce_context",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BN turns board state from a shape debate into an expectancy debate: is the board worth touching at all?",
            "This does not create execution binding. It gives the reduce hierarchy a harder top-level language: lockout-worthy, false-bounce-only, or unlock-worthy expectancy.",
        ]
        return V134BNCommercialAerospaceBMExpectancyDirectionTriageV1Report(
            summary=out_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BNCommercialAerospaceBMExpectancyDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BNCommercialAerospaceBMExpectancyDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bn_commercial_aerospace_bm_expectancy_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
