from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132QCommercialAerospaceGovernanceStackRefreshV2Report:
    summary: dict[str, Any]
    governance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "governance_rows": self.governance_rows,
            "interpretation": self.interpretation,
        }


class V132QCommercialAerospaceGovernanceStackRefreshV2Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.base_stack_path = (
            repo_root / "reports" / "analysis" / "v129k_commercial_aerospace_governance_stack_packaging_v1.json"
        )
        self.registry_triage_path = (
            repo_root / "reports" / "analysis" / "v131z_commercial_aerospace_yz_intraday_registry_triage_v1.json"
        )
        self.minute_label_triage_path = (
            repo_root / "reports" / "analysis" / "v132b_commercial_aerospace_ab_minute_label_direction_triage_v1.json"
        )
        self.shadow_benefit_triage_path = (
            repo_root / "reports" / "analysis" / "v132p_commercial_aerospace_op_local_1min_shadow_benefit_triage_v1.json"
        )

    def analyze(self) -> V132QCommercialAerospaceGovernanceStackRefreshV2Report:
        base_stack = json.loads(self.base_stack_path.read_text(encoding="utf-8"))
        registry_triage = json.loads(self.registry_triage_path.read_text(encoding="utf-8"))
        minute_label_triage = json.loads(self.minute_label_triage_path.read_text(encoding="utf-8"))
        shadow_benefit_triage = json.loads(self.shadow_benefit_triage_path.read_text(encoding="utf-8"))

        governance_rows = list(base_stack["governance_rows"])
        governance_rows.extend(
            [
                {
                    "layer": "intraday_supervision_registry",
                    "status": registry_triage["summary"]["authoritative_status"],
                    "rule": "retain severe / reversal / mild minute seeds as the canonical intraday supervision source",
                    "source_status": registry_triage["summary"]["authoritative_status"],
                },
                {
                    "layer": "minute_tiered_label_specification",
                    "status": minute_label_triage["summary"]["authoritative_status"],
                    "rule": "commercial-aerospace minute supervision must preserve the severe / reversal / mild tier order before any broader expansion is attempted",
                    "source_status": minute_label_triage["summary"]["authoritative_status"],
                },
                {
                    "layer": "local_1min_shadow_benefit_governance",
                    "status": shadow_benefit_triage["summary"]["authoritative_status"],
                    "rule": "local 1-minute rules gain stronger governance status when a narrow flagged slice of buy executions captures disproportionate later downside notional without touching clean controls",
                    "source_status": shadow_benefit_triage["summary"]["authoritative_status"],
                },
            ]
        )

        summary = {
            "acceptance_posture": "freeze_v132q_commercial_aerospace_governance_stack_refresh_v2",
            "governance_layer_count": len(governance_rows),
            "current_primary_variant": base_stack["summary"]["current_primary_variant"],
            "authoritative_output": "commercial_aerospace_governance_stack_v2_frozen_with_local_minute_branch",
        }
        interpretation = [
            "V1.32Q refreshes the commercial-aerospace governance stack after the local minute branch survived bounded expansion and shadow-benefit auditing.",
            "The output is still governance-first: the lawful EOD primary remains unchanged, but the intraday supervision layers now have explicit authoritative slots in the stack.",
        ]
        return V132QCommercialAerospaceGovernanceStackRefreshV2Report(
            summary=summary,
            governance_rows=governance_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132QCommercialAerospaceGovernanceStackRefreshV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132QCommercialAerospaceGovernanceStackRefreshV2Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132q_commercial_aerospace_governance_stack_refresh_v2",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
