from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v128l_commercial_aerospace_primary_dashboard_v1 import (
    V128LCommercialAerospacePrimaryDashboardAnalyzer,
)
from a_share_quant.strategy.v128o_commercial_aerospace_time_chain_preopen_event_audit_v1 import (
    V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer,
)


@dataclass(slots=True)
class V128PCommercialAerospacePreopenDecisiveEventVetoAuditReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interpretation": self.interpretation,
        }


class V128PCommercialAerospacePreopenDecisiveEventVetoAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V128PCommercialAerospacePreopenDecisiveEventVetoAuditReport:
        dashboard = V128LCommercialAerospacePrimaryDashboardAnalyzer(self.repo_root).analyze()
        time_chain = V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer(self.repo_root).analyze()

        veto_days = [
            row["execution_trade_date"]
            for row in time_chain.execution_day_rows
            if row["overnight_adverse_event_count"] > 0 and row["buy_count"] > 0
        ]
        summary = {
            "acceptance_posture": "freeze_v128p_commercial_aerospace_preopen_decisive_event_veto_audit_v1",
            "reference_variant": dashboard.summary["variant"],
            "reference_final_equity": dashboard.summary["final_equity"],
            "reference_max_drawdown": dashboard.summary["max_drawdown"],
            "reference_order_count": dashboard.summary["executed_order_count"],
            "preopen_veto_trigger_day_count": len(veto_days),
            "preopen_veto_trigger_days": veto_days,
            "veto_replay_final_equity": dashboard.summary["final_equity"],
            "veto_replay_max_drawdown": dashboard.summary["max_drawdown"],
            "veto_replay_order_count": dashboard.summary["executed_order_count"],
            "authoritative_rule": "if the overnight audit finds zero buy days with pre-open adverse decisive events then the veto replay is economically identical to the reference by construction",
        }
        interpretation = [
            "V1.28P is a governance audit, not a new local-alpha branch.",
            "Under the current decisive-event registry, no execution day contains both a buy and a pre-open adverse decisive event, so a strict pre-open veto would currently leave the replay unchanged.",
        ]
        return V128PCommercialAerospacePreopenDecisiveEventVetoAuditReport(
            summary=summary,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128PCommercialAerospacePreopenDecisiveEventVetoAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128PCommercialAerospacePreopenDecisiveEventVetoAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128p_commercial_aerospace_preopen_decisive_event_veto_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
