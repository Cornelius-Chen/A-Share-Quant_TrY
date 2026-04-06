from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134DCCommercialAerospaceDBPrelaunchDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134DCCommercialAerospaceDBPrelaunchDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.prelaunch_status_path = (
            repo_root / "reports" / "analysis" / "v134db_commercial_aerospace_intraday_add_prelaunch_status_card_v1.json"
        )

    def analyze(self) -> V134DCCommercialAerospaceDBPrelaunchDirectionTriageV1Report:
        prelaunch = json.loads(self.prelaunch_status_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v134dc_commercial_aerospace_db_prelaunch_direction_triage_v1",
            "authoritative_status": "freeze_intraday_add_prelaunch_status_and_keep_frontier_deferred",
            "opening_gate_count": prelaunch["summary"]["opening_gate_count"],
            "authoritative_rule": "when the next frontier is deferred and its opening checklist exists, the correct action is to retain prelaunch readiness without opening the frontier",
        }
        triage_rows = [
            {
                "component": "prelaunch_status_card",
                "status": "retain",
                "rationale": "the board now has a clean single-card summary for later explicit frontier opening",
            },
            {
                "component": "reduce_branch",
                "status": "keep_frozen",
                "rationale": "reduce remains complete enough and should not be reopened through deferred-frontier preparation",
            },
            {
                "component": "intraday_add_opening_now",
                "status": "blocked",
                "rationale": "prelaunch readiness is not equivalent to permission to start the next frontier",
            },
        ]
        interpretation = [
            "V1.34DC turns the prelaunch card into a final governance judgment: the next frontier is ready to be named, not ready to be silently opened.",
            "This preserves a clean handoff boundary between reduce completion and the later explicit start of intraday add.",
        ]
        return V134DCCommercialAerospaceDBPrelaunchDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134DCCommercialAerospaceDBPrelaunchDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134DCCommercialAerospaceDBPrelaunchDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134dc_commercial_aerospace_db_prelaunch_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
