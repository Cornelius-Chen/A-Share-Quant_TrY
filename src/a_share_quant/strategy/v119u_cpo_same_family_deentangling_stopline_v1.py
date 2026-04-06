from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V119UCpoSameFamilyDeentanglingStoplineReport:
    summary: dict[str, Any]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "comparison_rows": self.comparison_rows, "interpretation": self.interpretation}


class V119UCpoSameFamilyDeentanglingStoplineAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v119t_payload: dict[str, Any]) -> V119UCpoSameFamilyDeentanglingStoplineReport:
        comparison_rows = v119t_payload["variant_rows"]
        summary = {
            "acceptance_posture": "freeze_v119u_cpo_same_family_deentangling_stopline_v1",
            "authoritative_conclusion": "no_narrow_same_family_variant_improves_holdout_and_leakage_together",
            "same_family_micro_tuning_allowed": False,
            "recommended_next_posture": "stop_same_family_deentangling_micro_tuning_and_reopen_only_if_a_new_orthogonal_fix_idea_exists",
        }
        interpretation = [
            "V1.19U freezes the decision boundary after the narrow same-family de-entangling scan.",
            "The scan found no single residualization variant that simultaneously improves chronology/holdouts and reduces context leakage.",
            "That means same-family de-entangling has reached its stopline; further progress requires a new orthogonal fix idea rather than more micro-tuning.",
        ]
        return V119UCpoSameFamilyDeentanglingStoplineReport(summary=summary, comparison_rows=comparison_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V119UCpoSameFamilyDeentanglingStoplineReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119UCpoSameFamilyDeentanglingStoplineAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119t_payload=json.loads((repo_root / "reports" / "analysis" / "v119t_cpo_same_family_deentangling_scan_v1.json").read_text(encoding="utf-8"))
    )
    output_path = write_report(reports_dir=repo_root / "reports" / "analysis", report_name="v119u_cpo_same_family_deentangling_stopline_v1", result=result)
    print(output_path)


if __name__ == "__main__":
    main()
