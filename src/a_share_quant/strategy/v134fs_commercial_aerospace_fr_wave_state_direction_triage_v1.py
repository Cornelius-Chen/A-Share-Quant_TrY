from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FSCommercialAerospaceFRWaveStateDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FSCommercialAerospaceFRWaveStateDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134fr_commercial_aerospace_add_wave_state_authority_audit_v1.json"
        )

    def analyze(self) -> V134FSCommercialAerospaceFRWaveStateDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        authoritative_status = "retain_post_wave_echo_guard_and_shift_next_to_active_wave_selection_supervision"
        triage_rows = [
            {
                "component": "post_wave_echo_guard",
                "status": "retain",
                "rationale": "late strong local echoes can already be separated from true add-wave days using recent order-flow state",
            },
            {
                "component": "active_wave_selection_problem",
                "status": "still_open",
                "rationale": "after removing post-wave echoes, the residual blocker is deciding which symbol gets selected inside a live add wave",
            },
            {
                "component": "broader_positive_add_promotion",
                "status": "still_blocked",
                "rationale": "the branch still lacks a justified same-wave daily ranking layer, so execution and broader promotion remain blocked",
            },
        ]
        interpretation = [
            "V1.34FS turns the wave-state split into the next governance verdict for the add frontier.",
            "The frontier no longer needs to confuse late echoes with same-wave competition; its remaining blocker is now narrowly the active-wave selection problem.",
        ]
        return V134FSCommercialAerospaceFRWaveStateDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fs_commercial_aerospace_fr_wave_state_direction_triage_v1",
                "authoritative_status": authoritative_status,
                "candidate_day_count": audit["summary"]["candidate_day_count"],
                "active_wave_selection_day_count": audit["summary"]["active_wave_selection_day_count"],
                "post_wave_echo_guard_count": audit["summary"]["post_wave_echo_guard_count"],
                "authoritative_rule": (
                    "the add frontier should keep a post-wave echo guard and shift its next supervision layer to active-wave daily selection rather than continuing generic portability tuning"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FSCommercialAerospaceFRWaveStateDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FSCommercialAerospaceFRWaveStateDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fs_commercial_aerospace_fr_wave_state_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
