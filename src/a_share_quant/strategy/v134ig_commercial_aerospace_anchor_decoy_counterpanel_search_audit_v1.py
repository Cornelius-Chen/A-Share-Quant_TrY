from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134IGCommercialAerospaceAnchorDecoyCounterpanelSearchAuditV1Report:
    summary: dict[str, Any]
    search_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "search_rows": self.search_rows,
            "interpretation": self.interpretation,
        }


class V134IGCommercialAerospaceAnchorDecoyCounterpanelSearchAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_anchor_decoy_counterpanel_search_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134IGCommercialAerospaceAnchorDecoyCounterpanelSearchAuditV1Report:
        role_candidates = self._load_json(
            "reports/analysis/v134hy_commercial_aerospace_event_attention_role_candidate_audit_v1.json"
        )
        event_attention = self._load_json(
            "reports/analysis/v134hw_commercial_aerospace_event_attention_supervision_registry_v1.json"
        )

        hard_role_symbols = {
            row["symbol"]
            for row in event_attention["registry_rows"]
            if row["supervision_label"] in {"attention_anchor", "attention_decoy"}
        }

        search_rows: list[dict[str, Any]] = []
        for row in role_candidates["candidate_rows"]:
            symbol = row["symbol"]
            if symbol in hard_role_symbols:
                search_rows.append(
                    {
                        "symbol": symbol,
                        "display_name": row["display_name"],
                        "search_status": "current_hard_counterpanel_case",
                        "hard_anchor_candidate": "yes",
                        "hard_decoy_candidate": "yes",
                        "blocking_reason": "",
                        "next_requirement": "acts_as_existing_counterpanel_reference",
                    }
                )
                continue

            candidate_role = row["candidate_role"]
            if symbol == "603601":
                search_status = "carrier_candidate_not_counterpanel"
                hard_anchor_candidate = "no"
                hard_decoy_candidate = "no"
                blocking_reason = "event_backed_carrier_role_conflicts_with_counterpanel_usage"
                next_requirement = "would need explicit heat-anchor evidence plus later failed board participation"
            elif symbol == "301306":
                search_status = "follow_candidate_not_counterpanel"
                hard_anchor_candidate = "no"
                hard_decoy_candidate = "no"
                blocking_reason = "follow_candidate_lacks_anchor_heat_role"
                next_requirement = "would need clear attention-anchor evidence before any decoy evaluation"
            elif symbol == "002361":
                search_status = "crowding_without_hard_heat_evidence"
                hard_anchor_candidate = "no"
                hard_decoy_candidate = "soft_only"
                blocking_reason = "crowding_and_near_high_repair_exist_but_no explicit hard heat-anchor event"
                next_requirement = "would need decisive attention-anchor evidence before promotion to hard counterpanel"
            elif symbol == "300342":
                search_status = "outlier_breakout_without_hard_heat_evidence"
                hard_anchor_candidate = "no"
                hard_decoy_candidate = "soft_only"
                blocking_reason = "breakout path exists but supporting theme-heat event is not retained as decisive"
                next_requirement = "would need retained heat-anchor evidence plus later failed board restart reading"
            else:
                search_status = "unclassified"
                hard_anchor_candidate = "no"
                hard_decoy_candidate = "no"
                blocking_reason = "unclassified"
                next_requirement = ""

            search_rows.append(
                {
                    "symbol": symbol,
                    "display_name": row["display_name"],
                    "search_status": search_status,
                    "hard_anchor_candidate": hard_anchor_candidate,
                    "hard_decoy_candidate": hard_decoy_candidate,
                    "blocking_reason": blocking_reason,
                    "next_requirement": next_requirement,
                }
            )

        hard_counterpanel_count = sum(1 for row in search_rows if row["search_status"] == "current_hard_counterpanel_case")
        second_hard_counterpanel_found = hard_counterpanel_count >= 2

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(search_rows[0].keys()))
            writer.writeheader()
            writer.writerows(search_rows)

        summary = {
            "acceptance_posture": "freeze_v134ig_commercial_aerospace_anchor_decoy_counterpanel_search_audit_v1",
            "searched_symbol_count": len(search_rows),
            "current_hard_counterpanel_count": hard_counterpanel_count,
            "second_hard_counterpanel_found": second_hard_counterpanel_found,
            "soft_decoy_only_candidate_count": sum(1 for row in search_rows if row["hard_decoy_candidate"] == "soft_only"),
            "search_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the anchor/decoy counterpanel still has only one hard case, 航天发展; 神剑股份 and 天银机电 are at most soft decoy-only candidates, while 再升科技 and 西测测试 remain outside hard counterpanel status for explicit role reasons",
        }
        interpretation = [
            "V1.34IG searches for a second hard anchor/decoy counterpanel case instead of assuming one must already exist.",
            "The result remains conservative: there is still only one hard counterpanel case, with a few softer decoy-only candidates and several explicit non-fits.",
        ]
        return V134IGCommercialAerospaceAnchorDecoyCounterpanelSearchAuditV1Report(
            summary=summary,
            search_rows=search_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IGCommercialAerospaceAnchorDecoyCounterpanelSearchAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IGCommercialAerospaceAnchorDecoyCounterpanelSearchAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ig_commercial_aerospace_anchor_decoy_counterpanel_search_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
