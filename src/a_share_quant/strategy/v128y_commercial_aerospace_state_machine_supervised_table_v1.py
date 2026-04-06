from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v126m_commercial_aerospace_phase_geometry_label_table_v1 import (
    V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer,
)


@dataclass(slots=True)
class V128YCommercialAerospaceStateMachineSupervisedTableReport:
    summary: dict[str, Any]
    training_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "training_rows": self.training_rows,
            "interpretation": self.interpretation,
        }


class V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _state_label(row: dict[str, Any]) -> str:
        phase = row["phase_window_semantic"]
        label_pg = row["supervised_action_label_pg"]
        if label_pg == "de_risk_target":
            return "de_risk"
        if label_pg == "probe_eligibility_target":
            return "probe"
        if label_pg == "full_eligibility_target" and phase == "preheat_window":
            return "full_pre"
        if label_pg == "full_eligibility_target" and phase == "impulse_window":
            return "full"
        return "neutral_hold"

    def analyze(self) -> V128YCommercialAerospaceStateMachineSupervisedTableReport:
        phase_table = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(self.repo_root).analyze()
        rows = [dict(row) for row in phase_table.training_rows]

        state_counts: dict[str, int] = {}
        active_counts: dict[str, int] = {}
        for row in rows:
            state_label = self._state_label(row)
            row["supervised_action_state"] = state_label
            state_counts[state_label] = state_counts.get(state_label, 0) + 1
            if state_label != "neutral_hold":
                active_counts[state_label] = active_counts.get(state_label, 0) + 1

        summary = {
            "acceptance_posture": "freeze_v128y_commercial_aerospace_state_machine_supervised_table_v1",
            "row_count": len(rows),
            "symbol_count": len({row["symbol"] for row in rows}),
            "feature_count": 18,
            "state_label_count": len(state_counts),
            "active_state_count": len(active_counts),
            "state_counts": state_counts,
            "active_state_counts": active_counts,
            "authoritative_rule": "commercial_aerospace_lawful_supervision_should_use_probe_full_pre_full_de_risk_state_machine_with_neutral_hold_background",
        }
        interpretation = [
            "V1.28Y translates the commercial-aerospace phase-geometry labels into a state-machine supervised table.",
            "This is a lawful EOD supervision refresh: it formalizes full-pre as a distinct state without reopening replay or intraday execution.",
        ]
        return V128YCommercialAerospaceStateMachineSupervisedTableReport(
            summary=summary,
            training_rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128YCommercialAerospaceStateMachineSupervisedTableReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def write_csv_file(*, output_path: Path, rows: list[dict[str, Any]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128y_commercial_aerospace_state_machine_supervised_table_v1",
        result=result,
    )
    csv_path = write_csv_file(
        output_path=repo_root / "data" / "training" / "commercial_aerospace_state_machine_supervised_table_v1.csv",
        rows=result.training_rows,
    )
    print(output_path)
    print(csv_path)


if __name__ == "__main__":
    main()
