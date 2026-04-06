from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134DACommercialAerospaceCZIntradayAddOpeningTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134DACommercialAerospaceCZIntradayAddOpeningTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.checklist_path = (
            repo_root / "reports" / "analysis" / "v134cz_commercial_aerospace_intraday_add_opening_checklist_v1.json"
        )

    def analyze(self) -> V134DACommercialAerospaceCZIntradayAddOpeningTriageV1Report:
        checklist = json.loads(self.checklist_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v134da_commercial_aerospace_cz_intraday_add_opening_triage_v1",
            "authoritative_status": "freeze_intraday_add_opening_checklist_and_keep_frontier_deferred_until_explicit_shift",
            "checklist_gate_count": checklist["summary"]["checklist_gate_count"],
            "authoritative_rule": "a deferred frontier may be prepared, but not opened, when its opening gates are now explicit and reduce remains frozen",
        }
        triage_rows = [
            {
                "component": "intraday_add_opening_checklist",
                "status": "retain_as_prelaunch_protocol",
                "rationale": "the next frontier now has an explicit prelaunch checklist and does not need more speculative preparation",
            },
            {
                "component": "reduce_branch",
                "status": "keep_frozen",
                "rationale": "reduce remains frozen_mainline and must not reopen under the cover of add preparation",
            },
            {
                "component": "frontier_opening_now",
                "status": "blocked",
                "rationale": "the user instruction is still to defer intraday add opening until a later explicit shift",
            },
        ]
        interpretation = [
            "V1.34DA converts the add-opening checklist into a simple governance judgment: the checklist is ready, but the frontier remains deferred.",
            "The point is to make the later shift easy without letting preparation mutate into premature frontier opening.",
        ]
        return V134DACommercialAerospaceCZIntradayAddOpeningTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134DACommercialAerospaceCZIntradayAddOpeningTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134DACommercialAerospaceCZIntradayAddOpeningTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134da_commercial_aerospace_cz_intraday_add_opening_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
