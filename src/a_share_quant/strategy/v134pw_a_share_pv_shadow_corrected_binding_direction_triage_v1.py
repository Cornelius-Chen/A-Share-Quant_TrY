from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pv_a_share_shadow_corrected_binding_view_audit_v1 import (
    V134PVAShareShadowCorrectedBindingViewAuditV1Analyzer,
)


@dataclass(slots=True)
class V134PWASharePVShadowCorrectedBindingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PWASharePVShadowCorrectedBindingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134PWASharePVShadowCorrectedBindingDirectionTriageV1Report:
        report = V134PVAShareShadowCorrectedBindingViewAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "corrected_bound_count": report.summary["corrected_bound_count"],
            "corrected_missing_count": report.summary["corrected_missing_count"],
            "corrected_via_effective_trade_date_count": report.summary[
                "corrected_via_effective_trade_date_count"
            ],
            "authoritative_status": "shadow_corrected_binding_view_is_useful_for_replay_only_and_should_not_replace_base_binding",
        }
        triage_rows = [
            {
                "component": "shadow_corrected_binding",
                "direction": "retain_as_shadow_only_overlay_for_replay_rechecks",
            },
            {
                "component": "base_binding_registry",
                "direction": "keep_unchanged_and_do_not_promote_effective_trade_date_logic_into_the_base_tradeable_context_view",
            },
            {
                "component": "next_move",
                "direction": "use_the_shadow_corrected_view_only_for_replay_internal_build_rechecks_before_any_broader_promotion_decision",
            },
        ]
        interpretation = [
            "The corrected binding view is useful because it removes the only internally fixable replay residual without altering PTI timestamps.",
            "That utility is still replay-local. It should remain an overlay until a later explicit promotion decision exists.",
        ]
        return V134PWASharePVShadowCorrectedBindingDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PWASharePVShadowCorrectedBindingDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PWASharePVShadowCorrectedBindingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pw_a_share_pv_shadow_corrected_binding_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
