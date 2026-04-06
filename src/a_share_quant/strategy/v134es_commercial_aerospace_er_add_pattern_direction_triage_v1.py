from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ESCommercialAerospaceERAddPatternDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134ESCommercialAerospaceERAddPatternDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134er_commercial_aerospace_local_add_pattern_envelope_audit_v1.json"
        )

    def analyze(self) -> V134ESCommercialAerospaceERAddPatternDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        status = "freeze_local_add_pattern_envelopes_and_shift_next_to_add_rule_candidate_audit"
        triage_rows = [
            {
                "component": "local_add_pattern_envelopes",
                "status": status,
                "rationale": (
                    "the add frontier now has enough early-session shape separation to move from pattern description into rule-candidate auditing"
                ),
            },
            {
                "component": "intraday_add_execution_authority",
                "status": "still_blocked",
                "rationale": "pattern envelopes remain supervision-only and do not authorize entry execution or replay binding",
            },
            {
                "component": "board_veto_stack",
                "status": "retain_unchanged",
                "rationale": "blocked board-lockout adds remain subordinate to the board-level lockout and local-only rebound guards",
            },
        ]
        interpretation = [
            "V1.34ES freezes the first add pattern envelopes as the canonical next step for the intraday-add frontier.",
            "The branch should next test explicit early-session add rule candidates, not jump to execution.",
        ]
        return V134ESCommercialAerospaceERAddPatternDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134es_commercial_aerospace_er_add_pattern_direction_triage_v1",
                "authoritative_status": status,
                "label_tier_count": audit["summary"]["label_tier_count"],
                "separation_pair_count": audit["summary"]["separation_pair_count"],
                "authoritative_rule": (
                    "the commercial-aerospace intraday-add frontier should next audit explicit early-session add rule candidates under the frozen local pattern envelopes while keeping execution blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ESCommercialAerospaceERAddPatternDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ESCommercialAerospaceERAddPatternDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134es_commercial_aerospace_er_add_pattern_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
