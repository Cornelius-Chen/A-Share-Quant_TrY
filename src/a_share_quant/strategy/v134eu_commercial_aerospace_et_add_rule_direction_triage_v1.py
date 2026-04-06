from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134EUCommercialAerospaceETAddRuleDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134EUCommercialAerospaceETAddRuleDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134et_commercial_aerospace_local_add_rule_candidate_audit_v1.json"
        )

    def analyze(self) -> V134EUCommercialAerospaceETAddRuleDirectionTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        if audit["summary"]["matched_count"] == audit["summary"]["registry_row_count"]:
            status = "retain_local_add_rule_candidates_as_governed_seed_rules_and_shift_next_to_broader_add_false_positive_audit"
        else:
            status = "keep_local_add_rule_candidates_as_draft_only"

        triage_rows = [
            {
                "component": "local_add_rule_candidates",
                "status": status,
                "rationale": "add seed rules are worth keeping only if they preserve the frozen four-tier add ordering before any broader minute-surface expansion",
            },
            {
                "component": "intraday_add_execution_authority",
                "status": "still_blocked",
                "rationale": "seed-rule coherence does not authorize add execution or replay binding",
            },
            {
                "component": "reduce_mainline",
                "status": "retain_frozen",
                "rationale": "advancing add seed rules does not reopen reduce or inherit reduce execution authority",
            },
        ]
        interpretation = [
            "V1.34EU turns the first add rule-candidate audit into a governance verdict.",
            "The next correct move is a broader add false-positive audit over local minute sessions, not execution binding.",
        ]
        return V134EUCommercialAerospaceETAddRuleDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134eu_commercial_aerospace_et_add_rule_direction_triage_v1",
                "authoritative_status": status,
                "matched_count": audit["summary"]["matched_count"],
                "registry_row_count": audit["summary"]["registry_row_count"],
                "authoritative_rule": (
                    "the intraday-add frontier may keep local add rule candidates as governed seed rules once they preserve the frozen add-tier ordering, "
                    "but broader false-positive auditing must come before any stronger claims"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EUCommercialAerospaceETAddRuleDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EUCommercialAerospaceETAddRuleDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134eu_commercial_aerospace_et_add_rule_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
