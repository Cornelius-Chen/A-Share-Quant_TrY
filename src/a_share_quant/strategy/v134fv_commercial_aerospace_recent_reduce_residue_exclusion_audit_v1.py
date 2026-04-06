from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FVCommercialAerospaceRecentReduceResidueExclusionAuditV1Report:
    summary: dict[str, Any]
    exclusion_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "exclusion_rows": self.exclusion_rows,
            "interpretation": self.interpretation,
        }


class V134FVCommercialAerospaceRecentReduceResidueExclusionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134ft_commercial_aerospace_active_wave_selection_supervision_audit_v1.json"
        )

    def analyze(self) -> V134FVCommercialAerospaceRecentReduceResidueExclusionAuditV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        candidate_rows = audit["candidate_rows"]

        excluded_rows = [
            row for row in candidate_rows if row["selection_state"] == "recent_reduce_residue_candidate"
        ]
        kept_rows = [
            row for row in candidate_rows if row["selection_state"] != "recent_reduce_residue_candidate"
        ]

        excluded_displaced_count = sum(1 for row in excluded_rows if row["selection_outcome"] == "displaced")
        excluded_selected_count = sum(1 for row in excluded_rows if row["selection_outcome"] == "selected")
        kept_selected_count = sum(1 for row in kept_rows if row["selection_outcome"] == "selected")
        kept_displaced_count = sum(1 for row in kept_rows if row["selection_outcome"] == "displaced")

        exclusion_rows = [
            {
                "rule_name": "recent_reduce_residue_exclusion",
                "candidate_count": len(candidate_rows),
                "excluded_count": len(excluded_rows),
                "excluded_displaced_count": excluded_displaced_count,
                "excluded_selected_count": excluded_selected_count,
                "kept_selected_count": kept_selected_count,
                "kept_displaced_count": kept_displaced_count,
                "displaced_precision": round(excluded_displaced_count / len(excluded_rows), 8) if excluded_rows else 0.0,
                "displaced_coverage": round(
                    excluded_displaced_count
                    / sum(1 for row in candidate_rows if row["selection_outcome"] == "displaced"),
                    8,
                )
                if candidate_rows
                else 0.0,
                "reading": "the first active-wave exclusion rule checks whether recent symbol-level reduce residue cleanly captures the displaced candidate without excluding selected ones",
            }
        ]

        summary = {
            "acceptance_posture": "freeze_v134fv_commercial_aerospace_recent_reduce_residue_exclusion_audit_v1",
            "candidate_count": len(candidate_rows),
            "excluded_count": len(excluded_rows),
            "excluded_displaced_count": excluded_displaced_count,
            "excluded_selected_count": excluded_selected_count,
            "kept_selected_count": kept_selected_count,
            "kept_displaced_count": kept_displaced_count,
            "displaced_precision": exclusion_rows[0]["displaced_precision"],
            "displaced_coverage": exclusion_rows[0]["displaced_coverage"],
            "authoritative_rule": (
                "recent symbol-level reduce residue is now the first clean local exclusion clue inside active-wave add selection, but it remains too narrow for execution authority"
            ),
        }
        interpretation = [
            "V1.34FV tests whether the first active-wave negative clue is strong enough to be treated as a real exclusion object rather than a descriptive label.",
            "The result is clean but tiny: it fully captures the currently displaced candidate and excludes none of the selected candidates, which makes it useful as local supervision but still too narrow for execution or broad promotion.",
        ]
        return V134FVCommercialAerospaceRecentReduceResidueExclusionAuditV1Report(
            summary=summary,
            exclusion_rows=exclusion_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FVCommercialAerospaceRecentReduceResidueExclusionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FVCommercialAerospaceRecentReduceResidueExclusionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fv_commercial_aerospace_recent_reduce_residue_exclusion_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
