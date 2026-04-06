from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V121YCpoRecent1MinSupportiveContinuationCandidateDiscoveryReport:
    summary: dict[str, Any]
    candidate_band_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_band_rows": self.candidate_band_rows,
            "interpretation": self.interpretation,
        }


class V121YCpoRecent1MinSupportiveContinuationCandidateDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V121YCpoRecent1MinSupportiveContinuationCandidateDiscoveryReport:
        report_path = self.repo_root / "reports" / "analysis" / "v121x_cpo_recent_1min_pca_structure_audit_v1.json"
        with report_path.open("r", encoding="utf-8") as handle:
            structure = json.load(handle)

        candidate_band_rows = []
        for row in structure["band_rows"]:
            if (
                row["mean_push_efficiency"] > 0.5
                and row["mean_late_session_integrity_score"] > 0.08
                and row["mean_close_vs_vwap"] > -0.0095
            ):
                candidate_band_rows.append(row)

        summary = {
            "acceptance_posture": "freeze_v121y_cpo_recent_1min_supportive_continuation_candidate_discovery_v1",
            "candidate_family_name": "supportive_continuation_1min_band_candidate",
            "candidate_band_count": len(candidate_band_rows),
            "candidate_band_names": [row["band"] for row in candidate_band_rows],
            "recommended_next_posture": "keep_as_non_replay_candidate_family_until_label_aligned_audit",
        }
        interpretation = [
            "V1.21Y extracts the positive-support 1-minute bands from the PCA structure instead of inventing a rule first.",
            "These bands look like continuation/repair states: strong push efficiency, acceptable close-vs-VWAP, and better late-session integrity.",
            "This is still a candidate family only and should not be promoted without label-aligned audit.",
        ]
        return V121YCpoRecent1MinSupportiveContinuationCandidateDiscoveryReport(
            summary=summary,
            candidate_band_rows=candidate_band_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121YCpoRecent1MinSupportiveContinuationCandidateDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121YCpoRecent1MinSupportiveContinuationCandidateDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121y_cpo_recent_1min_supportive_continuation_candidate_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
