from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V123FCpo1MinDownsideSamePlaneStoplineReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interpretation": self.interpretation,
        }


class V123FCpo1MinDownsideSamePlaneStoplineAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123FCpo1MinDownsideSamePlaneStoplineReport:
        report_path = self.repo_root / "reports" / "analysis" / "v123e_cpo_1min_downside_same_plane_integration_audit_v1.json"
        with report_path.open("r", encoding="utf-8") as handle:
            integration_report = json.load(handle)

        summary = {
            "acceptance_posture": "freeze_v123f_cpo_1min_downside_same_plane_stopline_v1",
            "best_variant_name": integration_report["summary"]["best_variant_name"],
            "material_increment_over_downside_failure": integration_report["summary"]["material_increment_over_downside_failure"],
            "same_plane_attachment_allowed": bool(integration_report["summary"]["material_increment_over_downside_failure"]),
            "recommended_next_posture": (
                "triage_same_plane_attachment"
                if integration_report["summary"]["material_increment_over_downside_failure"]
                else "freeze_both_1min_downside_branches_as_separate_soft_components"
            ),
        }
        interpretation = [
            "V1.23F converts the same-plane integration audit into a simple attachment decision.",
            "If there is no material non-replay increment over downside_failure, same-plane attachment is blocked even if one blend looks best locally.",
        ]
        return V123FCpo1MinDownsideSamePlaneStoplineReport(
            summary=summary,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123FCpo1MinDownsideSamePlaneStoplineReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123FCpo1MinDownsideSamePlaneStoplineAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123f_cpo_1min_downside_same_plane_stopline_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

