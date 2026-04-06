from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134EWCommercialAerospaceEVAddFalsePositiveTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134EWCommercialAerospaceEVAddFalsePositiveTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134ev_commercial_aerospace_broader_add_false_positive_audit_v1.json"
        )

    def analyze(self) -> V134EWCommercialAerospaceEVAddFalsePositiveTriageV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        status = "keep_add_positive_rules_seed_only_and_shift_next_to_context_gating_audit"
        triage_rows = [
            {
                "component": "positive_add_rule_expansion",
                "status": status,
                "rationale": (
                    "shape-only positive add rules are too dense on the broader session surface and cannot yet be promoted beyond seed-only governed rules"
                ),
            },
            {
                "component": "negative_governance_families",
                "status": "retain_as_useful_bounded_signals",
                "rationale": "failed and blocked add families remain much sparser and can be retained as bounded governance references",
            },
            {
                "component": "intraday_add_execution_authority",
                "status": "still_blocked",
                "rationale": "broader false-positive density blocks any move toward add execution or replay binding",
            },
        ]
        interpretation = [
            "V1.34EW converts the broader add false-positive audit into a governance verdict.",
            "The next correct move is not broader rule promotion but context-gating work that can distinguish real add permission from generic early-session rebounds.",
        ]
        return V134EWCommercialAerospaceEVAddFalsePositiveTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134ew_commercial_aerospace_ev_add_false_positive_triage_v1",
                "authoritative_status": status,
                "total_session_count": audit["summary"]["total_session_count"],
                "non_seed_positive_hit_count": audit["summary"]["non_seed_positive_hit_count"],
                "non_seed_positive_hit_rate": audit["summary"]["non_seed_positive_hit_rate"],
                "authoritative_rule": (
                    "the intraday-add frontier must keep positive add rules as seed-only until additional context gating is strong enough to suppress broader shape-only false positives"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EWCommercialAerospaceEVAddFalsePositiveTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EWCommercialAerospaceEVAddFalsePositiveTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ew_commercial_aerospace_ev_add_false_positive_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
