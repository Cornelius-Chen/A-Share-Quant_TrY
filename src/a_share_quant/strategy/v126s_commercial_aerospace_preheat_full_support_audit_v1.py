from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v126m_commercial_aerospace_phase_geometry_label_table_v1 import (
    V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer,
)


@dataclass(slots=True)
class V126SCommercialAerospacePreheatFullSupportAuditReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "interpretation": self.interpretation}


class V126SCommercialAerospacePreheatFullSupportAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V126SCommercialAerospacePreheatFullSupportAuditReport:
        table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        ordered_dates = sorted({row["trade_date"] for row in rows})

        matured_preheat_full_by_date: dict[str, int] = {}
        matured_any_full_by_date: dict[str, int] = {}
        for idx, trade_date in enumerate(ordered_dates):
            cutoff_idx = idx - 10
            if cutoff_idx < 0:
                matured_preheat_full_by_date[trade_date] = 0
                matured_any_full_by_date[trade_date] = 0
                continue
            matured_dates = set(ordered_dates[: cutoff_idx + 1])
            matured_rows = [row for row in rows if row["trade_date"] in matured_dates]
            matured_preheat_full_by_date[trade_date] = sum(
                1
                for row in matured_rows
                if row["phase_window_semantic"] == "preheat_window" and row["supervised_action_label_pg"] == "full_eligibility_target"
            )
            matured_any_full_by_date[trade_date] = sum(
                1 for row in matured_rows if row["supervised_action_label_pg"] == "full_eligibility_target"
            )

        preheat_dates = [trade_date for trade_date in ordered_dates if "20251114" <= trade_date <= "20251223"]
        preheat_dates_with_matured_support = [trade_date for trade_date in preheat_dates if matured_preheat_full_by_date[trade_date] > 0]
        summary = {
            "acceptance_posture": "freeze_v126s_commercial_aerospace_preheat_full_support_audit_v1",
            "preheat_full_label_count": sum(
                1
                for row in rows
                if row["phase_window_semantic"] == "preheat_window" and row["supervised_action_label_pg"] == "full_eligibility_target"
            ),
            "preheat_dates_with_matured_full_support": len(preheat_dates_with_matured_support),
            "first_preheat_date_with_matured_full_support": preheat_dates_with_matured_support[0] if preheat_dates_with_matured_support else None,
            "matured_preheat_full_on_20251205": matured_preheat_full_by_date.get("20251205", 0),
            "matured_preheat_full_on_20251224": matured_preheat_full_by_date.get("20251224", 0),
            "matured_any_full_on_20251224": matured_any_full_by_date.get("20251224", 0),
            "authoritative_rule": "preheat_full_support_exists_and_should_not_be_collapsed_back_to_probe_only_if_replay_is_attempting_to_capture_the_11_14_to_12_23_segment",
        }
        interpretation = [
            "V1.26S audits whether V1.26M already contains lawful preheat full-support that V1.26O failed to express in replay sizing.",
            "If matured preheat full-support exists before the main impulse dates, replay should test a stronger preheat tier instead of forcing all preheat into probe size.",
        ]
        return V126SCommercialAerospacePreheatFullSupportAuditReport(summary=summary, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V126SCommercialAerospacePreheatFullSupportAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126SCommercialAerospacePreheatFullSupportAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126s_commercial_aerospace_preheat_full_support_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
