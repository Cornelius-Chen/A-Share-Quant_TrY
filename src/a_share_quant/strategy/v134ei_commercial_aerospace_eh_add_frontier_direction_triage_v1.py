from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134EICommercialAerospaceEHAddFrontierDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134EICommercialAerospaceEHAddFrontierDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.opening_path = (
            repo_root / "reports" / "analysis" / "v134eh_commercial_aerospace_intraday_add_frontier_opening_v1.json"
        )

    def analyze(self) -> V134EICommercialAerospaceEHAddFrontierDirectionTriageV1Report:
        opening = json.loads(self.opening_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "open_v134ei_commercial_aerospace_eh_add_frontier_direction_triage_v1",
            "authoritative_status": "open_intraday_add_as_supervision_frontier_and_start_registry_bootstrap",
            "frontier_state": opening["summary"]["frontier_state"],
            "first_build_step": opening["summary"]["first_build_step"],
            "authoritative_rule": "the correct first move after explicit frontier shift is to build seed supervision, not execution authority",
        }
        triage_rows = [
            {
                "component": "intraday_add_frontier",
                "status": "opened_as_supervision_only",
                "rationale": "the branch is now active, but only at the supervision layer",
            },
            {
                "component": "first_artifact",
                "status": "intraday_add_supervision_registry_v1",
                "rationale": "registry bootstrap is the narrowest artifact that creates canonical add cases without leaking execution authority",
            },
            {
                "component": "reduce_branch",
                "status": "keep_frozen",
                "rationale": "reduce remains complete enough and must not reopen during add startup",
            },
        ]
        interpretation = [
            "V1.34EI converts the explicit frontier shift into a practical direction judgment.",
            "The add branch is now active, but its first job is to build a supervision registry rather than pretend it already owns execution.",
        ]
        return V134EICommercialAerospaceEHAddFrontierDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EICommercialAerospaceEHAddFrontierDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EICommercialAerospaceEHAddFrontierDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ei_commercial_aerospace_eh_add_frontier_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
