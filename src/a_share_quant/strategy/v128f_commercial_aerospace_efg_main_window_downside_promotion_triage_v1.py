from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128FCommercialAerospaceEFGMainWindowDownsidePromotionTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V128FCommercialAerospaceEFGMainWindowDownsidePromotionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = repo_root / "reports" / "analysis" / "v128e_commercial_aerospace_main_window_deeper_downside_audit_v1.json"

    def analyze(self) -> V128FCommercialAerospaceEFGMainWindowDownsidePromotionTriageReport:
        payload = json.loads(self.audit_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v128f_commercial_aerospace_efg_main_window_downside_promotion_triage_v1",
            "old_primary_variant": payload["summary"]["reference_variant"],
            "old_primary_final_equity": payload["summary"]["reference_final_equity"],
            "old_primary_max_drawdown": payload["summary"]["reference_max_drawdown"],
            "new_primary_variant": "mainwin_overdrive_075_impulse_075",
            "new_primary_final_equity": 1306704.6132,
            "new_primary_max_drawdown": 0.09309927,
            "authoritative_status": "promote_main_window_downside_variant_to_primary_reference",
            "canonical_name_rationale": "minimal_sufficient_name_that_reflects_the_real_increment",
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "promote_primary_reference",
                "canonical_name": "mainwin_overdrive_075_impulse_075",
                "reason": "This is a clean frontier improvement and the narrower canonical name matches the actual incremental mechanism.",
            },
            {
                "subagent": "Tesla",
                "vote": "promote_primary_reference",
                "canonical_name": "mainwin_overdrive_075_impulse_075",
                "reason": "The real gain comes from deeper impulse-target selling, not from broadening the overdrive layer.",
            },
            {
                "subagent": "James",
                "vote": "promote_primary_reference",
                "canonical_name": "mainwin_overdrive_075_impulse_075",
                "reason": "The promoted name should stay narrow and avoid implying extra semantics that did not earn their way in.",
            },
        ]
        interpretation = [
            "V1.28F promotes the successful main-window deeper downside variant to the new commercial-aerospace primary reference.",
            "The canonical name intentionally stays narrow because the incremental edge came from raising main-window impulse-target de-risk to 0.75, not from any stronger standalone overdrive rule.",
        ]
        return V128FCommercialAerospaceEFGMainWindowDownsidePromotionTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128FCommercialAerospaceEFGMainWindowDownsidePromotionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128FCommercialAerospaceEFGMainWindowDownsidePromotionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128f_commercial_aerospace_efg_main_window_downside_promotion_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
