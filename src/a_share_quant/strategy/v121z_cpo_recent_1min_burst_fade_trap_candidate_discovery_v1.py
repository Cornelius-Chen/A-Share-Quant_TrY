from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V121ZCpoRecent1MinBurstFadeTrapCandidateDiscoveryReport:
    summary: dict[str, Any]
    candidate_band_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_band_rows": self.candidate_band_rows,
            "interpretation": self.interpretation,
        }


class V121ZCpoRecent1MinBurstFadeTrapCandidateDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V121ZCpoRecent1MinBurstFadeTrapCandidateDiscoveryReport:
        report_path = self.repo_root / "reports" / "analysis" / "v121x_cpo_recent_1min_pca_structure_audit_v1.json"
        with report_path.open("r", encoding="utf-8") as handle:
            structure = json.load(handle)

        candidate_band_rows = []
        for row in structure["band_rows"]:
            if (
                row["mean_push_efficiency"] < -0.35
                and row["mean_late_session_integrity_score"] < -0.01
                and row["mean_burst_then_fade_score"] > 0.001
            ):
                candidate_band_rows.append(row)

        summary = {
            "acceptance_posture": "freeze_v121z_cpo_recent_1min_burst_fade_trap_candidate_discovery_v1",
            "candidate_family_name": "burst_fade_trap_1min_band_candidate",
            "candidate_band_count": len(candidate_band_rows),
            "candidate_band_names": [row["band"] for row in candidate_band_rows],
            "recommended_next_posture": "keep_as_non_replay_candidate_family_until_label_aligned_audit",
        }
        interpretation = [
            "V1.21Z extracts the negative/trap 1-minute bands from the PCA structure instead of pretending they are already rules.",
            "These bands look like burst-then-fade or upper-shadow-heavy trap states: weak push efficiency and poor late-session integrity with elevated fade score.",
            "This is a candidate family only and should be treated as non-replay until label-aligned audit exists.",
        ]
        return V121ZCpoRecent1MinBurstFadeTrapCandidateDiscoveryReport(
            summary=summary,
            candidate_band_rows=candidate_band_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121ZCpoRecent1MinBurstFadeTrapCandidateDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121ZCpoRecent1MinBurstFadeTrapCandidateDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121z_cpo_recent_1min_burst_fade_trap_candidate_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
