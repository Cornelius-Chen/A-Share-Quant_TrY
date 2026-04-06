from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V122KCpoHij1MinProxyLabelTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V122KCpoHij1MinProxyLabelTriageAnalyzer:
    def analyze(self) -> V122KCpoHij1MinProxyLabelTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "supportive_continuation_status": "candidate_family_only",
                "main_issue": "add_reduce_not_separated",
                "recommended_next_step": "add_probe_vs_reduce_probe_separation_audit",
            },
            {
                "reviewer": "Tesla",
                "supportive_continuation_status": "candidate_family_only",
                "main_issue": "active_management_family_not_clean_add_family",
                "recommended_next_step": "add_probe_vs_reduce_probe_separation_audit",
            },
            {
                "reviewer": "James",
                "supportive_continuation_status": "candidate_family_only",
                "main_issue": "add_enrichment_and_reduce_enrichment_coexist",
                "recommended_next_step": "add_probe_vs_reduce_probe_separation_audit",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v122k_cpo_hij_1min_proxy_label_triage_v1",
            "supportive_continuation_status": "candidate_family_only",
            "reviewer_consensus": "unanimous",
            "main_issue": "supportive_family_enriched_for_both_add_and_reduce_probes",
            "forbidden_next_step": "new_1min_family_discovery_or_replay_promotion",
            "recommended_next_posture": "run_supportive_family_add_vs_reduce_separation_audit",
        }
        interpretation = [
            "All three reviewers agree the supportive continuation family survives the proxy label plane but only as candidate_family_only.",
            "The family is no longer unlabeled geometry, but it still mixes add and reduce semantics too much to be a clean candidate.",
            "The next correct step is add-vs-reduce separation, not more family discovery and not replay.",
        ]
        return V122KCpoHij1MinProxyLabelTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122KCpoHij1MinProxyLabelTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122KCpoHij1MinProxyLabelTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122k_cpo_hij_1min_proxy_label_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
