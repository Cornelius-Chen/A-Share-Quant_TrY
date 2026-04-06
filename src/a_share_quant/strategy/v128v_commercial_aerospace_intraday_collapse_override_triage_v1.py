from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v128u_commercial_aerospace_intraday_collapse_override_proxy_audit_v1 import (
    V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditAnalyzer,
)


@dataclass(slots=True)
class V128VCommercialAerospaceIntradayCollapseOverrideTriageReport:
    summary: dict[str, Any]
    retained_rows: list[dict[str, Any]]
    blocked_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_rows": self.retained_rows,
            "blocked_rows": self.blocked_rows,
            "interpretation": self.interpretation,
        }


class V128VCommercialAerospaceIntradayCollapseOverrideTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V128VCommercialAerospaceIntradayCollapseOverrideTriageReport:
        audit = V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditAnalyzer(self.repo_root).analyze()
        retained_rows = [
            {
                "status": "retain_as_supervision_only_override_proto",
                "why": "proxy cleanly isolates retained severe intraday-collapse failures and does not fire on broader watch-only cases",
                "next_use": "future intraday emergency-exit grammar once minute-level lawful support exists",
            }
        ]
        blocked_rows = [
            {
                "status": "blocked_for_current_replay",
                "why": "proxy depends on execution-day path information and therefore cannot be translated into current lawful EOD replay",
            }
        ]
        summary = {
            "acceptance_posture": "freeze_v128v_commercial_aerospace_intraday_collapse_override_triage_v1",
            "proxy_hit_order_count": audit.summary["proxy_hit_order_count"],
            "retained_failure_coverage_rate": audit.summary["retained_failure_coverage_rate"],
            "watch_only_trigger_count": audit.summary["watch_only_trigger_count"],
            "authoritative_status": "retain_supervision_only_not_replay_facing",
            "next_direction": "keep building intraday override supervision objects and delay promotion until lawful minute-level support exists",
        }
        interpretation = [
            "V1.28V freezes the first intraday-collapse-override supervision proto.",
            "It is worth keeping as a future intraday governance object, but it is explicitly blocked from current EOD replay promotion.",
        ]
        return V128VCommercialAerospaceIntradayCollapseOverrideTriageReport(
            summary=summary,
            retained_rows=retained_rows,
            blocked_rows=blocked_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128VCommercialAerospaceIntradayCollapseOverrideTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128VCommercialAerospaceIntradayCollapseOverrideTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128v_commercial_aerospace_intraday_collapse_override_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
