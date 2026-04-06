from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134px_a_share_replay_shadow_corrected_recheck_audit_v1 import (
    V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer,
)


@dataclass(slots=True)
class V134PYASharePXShadowCorrectedRecheckDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PYASharePXShadowCorrectedRecheckDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134PYASharePXShadowCorrectedRecheckDirectionTriageV1Report:
        report = V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "base_missing_count": report.summary["base_missing_count"],
            "corrected_missing_count": report.summary["corrected_missing_count"],
            "boundary_only_residual_count": report.summary["boundary_only_residual_count"],
            "authoritative_status": "shadow_corrected_recheck_shows_only_external_boundary_residuals_remain_for_replay_internal_build",
        }
        triage_rows = [
            {
                "component": "shadow_corrected_recheck",
                "direction": "retain_as_replay_internal_evidence_that_the_calendar_alignment_residual_has_been_removed_in_shadow_overlay_space",
            },
            {
                "component": "remaining_residuals",
                "direction": "treat_remaining_rows_as_external_boundary_residuals_and_do_not_reopen_broad_market_context_rebuild_for_them",
            },
            {
                "component": "promotion_boundary",
                "direction": "keep_the_corrected_recheck_shadow_only_and_do_not_let_it_replace_base_binding_or_execution_state",
            },
        ]
        interpretation = [
            "The recheck confirms that the shadow overlay solves the only internally fixable replay residual on this branch.",
            "The remaining two rows sit outside the current market-context coverage window, so they should stay boundary-scoped rather than trigger broad internal rebuild work.",
        ]
        return V134PYASharePXShadowCorrectedRecheckDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PYASharePXShadowCorrectedRecheckDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PYASharePXShadowCorrectedRecheckDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134py_a_share_px_shadow_corrected_recheck_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
