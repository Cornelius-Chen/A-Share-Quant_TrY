from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(slots=True)
class V134PHASharePGLimitHaltSemanticSourceDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PHASharePGLimitHaltSemanticSourceDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.bootstrap_report_path = (
            repo_root / "reports" / "analysis" / "v134pg_a_share_tushare_limit_halt_semantic_side_inputs_bootstrap_v1.json"
        )

    def analyze(self) -> V134PHASharePGLimitHaltSemanticSourceDirectionTriageV1Report:
        report = _read_json(self.bootstrap_report_path)
        summary = {
            "namechange_row_count": report["summary"]["namechange_row_count"],
            "suspend_row_count": report["summary"]["suspend_row_count"],
            "authoritative_status": "semantic_side_input_sources_bootstrapped_for_limit_halt_replay_closure",
        }
        triage_rows = [
            {
                "component": "namechange_source",
                "direction": "treat_namechange_as_the_first_retained_st_proxy_source_for_limit_halt_side_input_closure",
            },
            {
                "component": "suspend_source",
                "direction": "treat_suspend_d_as_the_first_retained_suspension_source_for_limit_halt_side_input_closure",
            },
            {
                "component": "next_materialization_step",
                "direction": "reframe_the_remaining_replay_gap_as_side_input_materialization_not_source_absence",
            },
        ]
        interpretation = [
            "The replay-side semantic gap is no longer a pure source-absence problem once namechange and suspend_d are retained locally.",
            "The next step shifts to materializing usable ST/suspension side-input surfaces rather than searching for yet another external feed.",
        ]
        return V134PHASharePGLimitHaltSemanticSourceDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PHASharePGLimitHaltSemanticSourceDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PHASharePGLimitHaltSemanticSourceDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ph_a_share_pg_limit_halt_semantic_source_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
