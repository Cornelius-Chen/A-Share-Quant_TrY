from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CACommercialAerospaceBZHoldingsLedgerDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CACommercialAerospaceBZHoldingsLedgerDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.ledger_path = (
            repo_root / "reports" / "analysis" / "v134bz_commercial_aerospace_start_of_day_holdings_ledger_v1.json"
        )
        self.precedence_path = (
            repo_root / "reports" / "analysis" / "v134bx_commercial_aerospace_same_day_precedence_policy_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_bz_holdings_ledger_direction_triage_v1.csv"
        )

    def analyze(self) -> V134CACommercialAerospaceBZHoldingsLedgerDirectionTriageV1Report:
        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        precedence = json.loads(self.precedence_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "start_of_day_holdings_ledger",
                "status": "ready_as_binding_input",
                "detail": "The frozen EOD primary now has a concrete carried-inventory ledger with explicit same-day new-lot separation.",
            },
            {
                "component": "same_day_precedence_policy",
                "status": "ready_as_binding_guardrail",
                "detail": "Use the existing precedence families to prevent intraday sells from consuming same-day open/add lots or double-consuming against EOD reduce/close.",
            },
            {
                "component": "next_real_work",
                "status": "build_isolated_sell_side_shadow_lane",
                "detail": "The justified next step is now an isolated sell-side shadow lane wired to the holdings ledger and precedence policy.",
            },
            {
                "component": "scope_guardrail",
                "status": "mandatory",
                "detail": "Keep the lane sell-side only; do not pull reentry execution or full replay binding into this buildout.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134ca_commercial_aerospace_bz_holdings_ledger_direction_triage_v1",
            "authoritative_status": "freeze_holdings_ledger_and_open_isolated_sell_side_shadow_lane_next",
            "ledger_row_count": ledger["summary"]["ledger_row_count"],
            "collision_session_count": precedence["summary"]["collision_session_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CA converts the new holdings ledger plus existing precedence policy into the next binding direction.",
            "With carried inventory now explicit, the next justified build is the isolated sell-side shadow lane and not more semantic research.",
        ]
        return V134CACommercialAerospaceBZHoldingsLedgerDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CACommercialAerospaceBZHoldingsLedgerDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CACommercialAerospaceBZHoldingsLedgerDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ca_commercial_aerospace_bz_holdings_ledger_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
