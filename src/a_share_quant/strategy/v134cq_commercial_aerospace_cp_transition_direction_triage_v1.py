from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CQCommercialAerospaceCPTransitionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CQCommercialAerospaceCPTransitionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.protocol_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134cp_commercial_aerospace_reduce_to_intraday_add_transition_protocol_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_cp_transition_direction_triage_v1.csv"
        )

    def analyze(self) -> V134CQCommercialAerospaceCPTransitionDirectionTriageV1Report:
        protocol = json.loads(self.protocol_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "reduce_branch",
                "status": "keep_frozen",
                "detail": "Reduce remains frozen as handoff package and may only accept local residue maintenance.",
            },
            {
                "component": "intraday_add_frontier",
                "status": "approved_but_not_opened_now",
                "detail": "The later frontier should be intraday add, but this step preserves the user’s instruction not to start it immediately.",
            },
            {
                "component": "scope_guardrail",
                "status": "mandatory",
                "detail": "When add later opens, it must inherit board-level vetoes but must not inherit reduce execution authority.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134cq_commercial_aerospace_cp_transition_direction_triage_v1",
            "authoritative_status": "freeze_reduce_handoff_and_defer_intraday_add_frontier_opening_until_later_explicit_shift",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CQ converts the transition protocol into a direction judgment that respects the current deferred-handoff instruction.",
            "The branch should now stop inside reduce, keep the handoff package frozen, and wait for the later intentional opening of intraday add.",
        ]
        return V134CQCommercialAerospaceCPTransitionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CQCommercialAerospaceCPTransitionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CQCommercialAerospaceCPTransitionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cq_commercial_aerospace_cp_transition_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
