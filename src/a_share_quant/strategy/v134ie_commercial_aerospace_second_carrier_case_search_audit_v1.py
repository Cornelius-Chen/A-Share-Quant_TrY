from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134IECommercialAerospaceSecondCarrierCaseSearchAuditV1Report:
    summary: dict[str, Any]
    search_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "search_rows": self.search_rows,
            "interpretation": self.interpretation,
        }


class V134IECommercialAerospaceSecondCarrierCaseSearchAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_second_carrier_case_search_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134IECommercialAerospaceSecondCarrierCaseSearchAuditV1Report:
        role_separation = self._load_json(
            "reports/analysis/v134ia_commercial_aerospace_event_attention_role_separation_audit_v1.json"
        )
        event_attention = self._load_json(
            "reports/analysis/v134hw_commercial_aerospace_event_attention_supervision_registry_v1.json"
        )

        separation_by_symbol = {row["symbol"]: row for row in role_separation["separated_rows"]}
        anchor_symbol = next(
            row["symbol"] for row in event_attention["registry_rows"] if row["supervision_label"] == "attention_anchor"
        )

        search_rows = [
            {
                "symbol": "603601",
                "display_name": "再升科技",
                "current_role": separation_by_symbol["603601"]["separated_role"],
                "search_status": "current_primary_carrier_case",
                "carrier_grade": "yes_primary",
                "blocking_reason": "",
                "next_requirement": "needs_peer_case_not_more_self_confirmation",
            },
            {
                "symbol": "301306",
                "display_name": "西测测试",
                "current_role": separation_by_symbol["301306"]["separated_role"],
                "search_status": "event_backed_but_not_carrier",
                "carrier_grade": "no",
                "blocking_reason": "follow_candidate_not_attention_carrier",
                "next_requirement": "would need evidence of attention-carrying role rather than high-beta follow behavior",
            },
            {
                "symbol": "000547",
                "display_name": "航天发展",
                "current_role": "attention_anchor_and_attention_decoy",
                "search_status": "role_conflict_not_carrier",
                "carrier_grade": "no",
                "blocking_reason": "hard_anchor_decoy_case_not_true_selection_candidate",
                "next_requirement": "not a carrier search target; remains counterpanel evidence",
            },
            {
                "symbol": "002361",
                "display_name": "神剑股份",
                "current_role": separation_by_symbol["002361"]["separated_role"],
                "search_status": "crowded_without_event_backing",
                "carrier_grade": "no",
                "blocking_reason": "no_retained_event_backing",
                "next_requirement": "would need retained event backing before carrier consideration",
            },
            {
                "symbol": "300342",
                "display_name": "天银机电",
                "current_role": separation_by_symbol["300342"]["separated_role"],
                "search_status": "breakout_without_decisive_event_backing",
                "carrier_grade": "no",
                "blocking_reason": "supporting_theme_heat_event_not_retained",
                "next_requirement": "would need stronger retained event backing and non-lockout context",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(search_rows[0].keys()))
            writer.writeheader()
            writer.writerows(search_rows)

        summary = {
            "acceptance_posture": "freeze_v134ie_commercial_aerospace_second_carrier_case_search_audit_v1",
            "searched_symbol_count": len(search_rows),
            "current_primary_carrier_case_count": sum(1 for row in search_rows if row["carrier_grade"] == "yes_primary"),
            "second_carrier_case_found": False,
            "hard_anchor_symbol": anchor_symbol,
            "authoritative_rule": "the current event-backed role universe still contains only one carrier-grade case, 再升科技; no second carrier case is yet available, and the remaining candidates fail for explicit role or evidence reasons rather than for vague intuition",
            "search_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34IE turns the next named gap into an explicit search audit.",
            "The result is negative but useful: there is still no second carrier-grade case, and the reasons are now symbol-specific and explicit.",
        ]
        return V134IECommercialAerospaceSecondCarrierCaseSearchAuditV1Report(
            summary=summary,
            search_rows=search_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IECommercialAerospaceSecondCarrierCaseSearchAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IECommercialAerospaceSecondCarrierCaseSearchAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ie_commercial_aerospace_second_carrier_case_search_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
