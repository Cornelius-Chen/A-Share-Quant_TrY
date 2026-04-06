from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FUCommercialAerospaceFTActiveWaveDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FUCommercialAerospaceFTActiveWaveDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134ft_commercial_aerospace_active_wave_selection_supervision_audit_v1.json"
        )

    def analyze(self) -> V134FUCommercialAerospaceFTActiveWaveDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        authoritative_status = (
            "retain_active_wave_selection_states_as_local_supervision_and_keep_add_execution_blocked"
        )
        triage_rows = [
            {
                "component": "recent_reduce_residue_candidate",
                "status": "retain_as_negative_selection_clue",
                "rationale": "the only displaced active-wave candidate currently sits in this state",
            },
            {
                "component": "same_symbol_continuation_and_clean_reset",
                "status": "retain_as_current_selected_states",
                "rationale": "the currently selected active-wave candidates all fall into these two states",
            },
            {
                "component": "daily_ranker_or_execution",
                "status": "still_blocked",
                "rationale": "the sample is still local and supervision-only; this is enough to structure the problem, not to authorize execution",
            },
        ]
        interpretation = [
            "V1.34FU converts the first active-wave selection audit into a bounded supervision verdict.",
            "The add frontier now has a small but interpretable state split for active-wave selection, while broader promotion and execution remain blocked.",
        ]
        return V134FUCommercialAerospaceFTActiveWaveDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fu_commercial_aerospace_ft_active_wave_direction_triage_v1",
                "authoritative_status": authoritative_status,
                "active_wave_day_count": audit["summary"]["active_wave_day_count"],
                "candidate_count": audit["summary"]["candidate_count"],
                "selected_candidate_count": audit["summary"]["selected_candidate_count"],
                "displaced_candidate_count": audit["summary"]["displaced_candidate_count"],
                "authoritative_rule": (
                    "the add frontier should retain recent-reduce residue as a local negative selection clue inside active waves, while continuing to block broader promotion and execution"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FUCommercialAerospaceFTActiveWaveDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FUCommercialAerospaceFTActiveWaveDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fu_commercial_aerospace_ft_active_wave_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
