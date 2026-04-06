from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127VCommercialAerospaceUVWWindowDeriskTriageReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interpretation": self.interpretation,
        }


class V127VCommercialAerospaceUVWWindowDeriskTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v127u_path = repo_root / "reports" / "analysis" / "v127u_commercial_aerospace_window_specific_derisk_grammar_audit_v1.json"

    def analyze(self) -> V127VCommercialAerospaceUVWWindowDeriskTriageReport:
        payload = json.loads(self.v127u_path.read_text(encoding="utf-8"))
        reference_variant = payload["summary"]["reference_variant"]
        best_variant = payload["summary"]["best_variant"]
        summary = {
            "acceptance_posture": "freeze_v127v_commercial_aerospace_uvw_window_derisk_triage_v1",
            "reference_variant": reference_variant,
            "best_variant": best_variant,
            "best_variant_final_equity": payload["summary"]["best_variant_final_equity"],
            "best_variant_max_drawdown": payload["summary"]["best_variant_max_drawdown"],
            "authoritative_status": (
                "promote_window_specific_derisk_fix"
                if best_variant != reference_variant
                else "blocked_keep_current_primary"
            ),
        }
        interpretation = [
            "V1.27V freezes the first window-specific de-risk grammar branch on the largest new-primary drawdown window.",
        ]
        return V127VCommercialAerospaceUVWWindowDeriskTriageReport(
            summary=summary,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127VCommercialAerospaceUVWWindowDeriskTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127VCommercialAerospaceUVWWindowDeriskTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127v_commercial_aerospace_uvw_window_derisk_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
