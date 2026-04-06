from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ISCommercialAerospaceOutsideNamedSecondCarrierSupervisionAuditV1Report:
    summary: dict[str, Any]
    supervision_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "supervision_rows": self.supervision_rows,
            "interpretation": self.interpretation,
        }


class V134ISCommercialAerospaceOutsideNamedSecondCarrierSupervisionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_outside_named_second_carrier_supervision_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134ISCommercialAerospaceOutsideNamedSecondCarrierSupervisionAuditV1Report:
        primary_search = self._load_json(
            "reports/analysis/v134ie_commercial_aerospace_second_carrier_case_search_audit_v1.json"
        )
        expanded_search = self._load_json(
            "reports/analysis/v134iq_commercial_aerospace_expanded_symbol_universe_carrier_search_audit_v1.json"
        )
        local_rebound = self._load_json(
            "reports/analysis/v134bk_commercial_aerospace_local_only_rebound_audit_v1.json"
        )
        event_attention = self._load_json(
            "reports/analysis/v134hw_commercial_aerospace_event_attention_supervision_registry_v1.json"
        )

        primary_row = next(row for row in primary_search["search_rows"] if row["symbol"] == "603601")
        outside_row = next(row for row in expanded_search["symbol_rows"] if row["symbol"] == "000738")
        local_rows_000738 = [row for row in local_rebound["seed_rows"] if row["top_symbol"] == "000738"]
        event_rows_000738 = [
            row for row in event_attention["registry_rows"] if row["symbol"] == "000738"
        ]

        supervision_rows = [
            {
                "symbol": "603601",
                "display_name": "再升科技",
                "supervision_role": "current_primary_event_backed_carrier_case",
                "local_top_day_count": 0,
                "post_lockout_max_vs_pre_lockout_peak": 0.05806011,
                "post_lockout_max_return_from_start": 0.45173383,
                "event_backing_present": True,
                "board_local_rebound_leadership_present": False,
                "remaining_blockers": "needs_peer_case_not_more_self_confirmation",
                "learning_reading": primary_row["next_requirement"],
            },
            {
                "symbol": "000738",
                "display_name": "航发控制",
                "supervision_role": "outside_named_local_leadership_second_carrier_watch",
                "local_top_day_count": len(local_rows_000738),
                "post_lockout_max_vs_pre_lockout_peak": outside_row["post_lockout_max_vs_pre_lockout_peak"],
                "post_lockout_max_return_from_start": outside_row["post_lockout_max_return_from_start"],
                "event_backing_present": bool(event_rows_000738),
                "board_local_rebound_leadership_present": True,
                "remaining_blockers": "no_retained_event_seed|no_event_attention_role_label|followthrough_not_extended_to_outside_named_watch",
                "learning_reading": "outside-named formal/core symbol has repeated locked-board leadership and breakout strength, but it still lacks retained event backing and downstream role labeling required for second-carrier promotion",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(supervision_rows[0].keys()))
            writer.writeheader()
            writer.writerows(supervision_rows)

        summary = {
            "acceptance_posture": "freeze_v134is_commercial_aerospace_outside_named_second_carrier_supervision_audit_v1",
            "current_primary_case_count": 1,
            "outside_named_watch_count": 1,
            "outside_named_watch_has_event_backing": False,
            "outside_named_watch_local_top_day_count": len(local_rows_000738),
            "supervision_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "000738 is now a lawful outside-named second-carrier watch because it shows repeated board-local rebound leadership and breakout strength, but it remains blocked from promotion until retained event backing and downstream role/followthrough labeling exist",
        }
        interpretation = [
            "V1.34IS promotes 000738 into the supervision stack without pretending it already satisfies the same evidence standard as the current primary carrier case.",
            "The point is to separate 'worth searching next' from 'already ready for second-carrier promotion'.",
        ]
        return V134ISCommercialAerospaceOutsideNamedSecondCarrierSupervisionAuditV1Report(
            summary=summary,
            supervision_rows=supervision_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ISCommercialAerospaceOutsideNamedSecondCarrierSupervisionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ISCommercialAerospaceOutsideNamedSecondCarrierSupervisionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134is_commercial_aerospace_outside_named_second_carrier_supervision_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
