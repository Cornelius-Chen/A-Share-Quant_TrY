from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128WCommercialAerospacePhaseStateMachineAuditReport:
    summary: dict[str, Any]
    state_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "state_rows": self.state_rows,
            "interpretation": self.interpretation,
        }


class V128WCommercialAerospacePhaseStateMachineAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.label_path = repo_root / "data" / "training" / "commercial_aerospace_phase_geometry_label_table_v1.csv"

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _safe_float(value: str | float | int | None) -> float:
        if value in (None, ""):
            return 0.0
        return float(value)

    @staticmethod
    def _summarize_state(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
        forward = [float(row["forward_return_10"]) for row in rows]
        adverse = [float(row["max_adverse_return_10"]) for row in rows]
        favorable = [float(row["max_favorable_return_10"]) for row in rows]
        return {
            "state_name": name,
            "row_count": len(rows),
            "start_trade_date": min((row["trade_date"] for row in rows), default=""),
            "end_trade_date": max((row["trade_date"] for row in rows), default=""),
            "symbol_count": len({row["symbol"] for row in rows}),
            "mean_forward_return_10": round(sum(forward) / len(forward), 8) if forward else 0.0,
            "mean_max_adverse_return_10": round(sum(adverse) / len(adverse), 8) if adverse else 0.0,
            "mean_max_favorable_return_10": round(sum(favorable) / len(favorable), 8) if favorable else 0.0,
        }

    def analyze(self) -> V128WCommercialAerospacePhaseStateMachineAuditReport:
        rows = self._load_csv(self.label_path)

        probe_rows = [
            row
            for row in rows
            if row["supervised_action_label_pg"] == "probe_eligibility_target"
        ]
        full_pre_rows = [
            row
            for row in rows
            if row["phase_window_semantic"] == "preheat_window"
            and row["supervised_action_label_pg"] == "full_eligibility_target"
        ]
        full_rows = [
            row
            for row in rows
            if row["phase_window_semantic"] == "impulse_window"
            and row["supervised_action_label_pg"] == "full_eligibility_target"
        ]
        de_risk_rows = [
            row
            for row in rows
            if row["supervised_action_label_pg"] == "de_risk_target"
        ]

        state_rows = [
            self._summarize_state("probe", probe_rows),
            self._summarize_state("full_pre", full_pre_rows),
            self._summarize_state("full", full_rows),
            self._summarize_state("de_risk", de_risk_rows),
        ]

        full_pre_mean_forward = self._safe_float(state_rows[1]["mean_forward_return_10"])
        full_mean_forward = self._safe_float(state_rows[2]["mean_forward_return_10"])
        full_pre_mean_adverse = self._safe_float(state_rows[1]["mean_max_adverse_return_10"])
        full_mean_adverse = self._safe_float(state_rows[2]["mean_max_adverse_return_10"])

        summary = {
            "acceptance_posture": "freeze_v128w_commercial_aerospace_phase_state_machine_audit_v1",
            "probe_count": len(probe_rows),
            "full_pre_count": len(full_pre_rows),
            "full_count": len(full_rows),
            "de_risk_count": len(de_risk_rows),
            "full_pre_start": min((row["trade_date"] for row in full_pre_rows), default=""),
            "full_pre_end": max((row["trade_date"] for row in full_pre_rows), default=""),
            "full_start": min((row["trade_date"] for row in full_rows), default=""),
            "full_end": max((row["trade_date"] for row in full_rows), default=""),
            "full_pre_to_full_gap_days": 0
            if full_pre_rows and full_rows and max(row["trade_date"] for row in full_pre_rows) < min(row["trade_date"] for row in full_rows)
            else None,
            "full_pre_forward_minus_full_forward": round(full_pre_mean_forward - full_mean_forward, 8),
            "full_pre_adverse_minus_full_adverse": round(full_pre_mean_adverse - full_mean_adverse, 8),
            "authoritative_rule": "commercial aerospace should be represented as probe / full-pre / full / de-risk rather than probe / full only when preheat full-quality support materially overlaps with later impulse full quality",
        }
        interpretation = [
            "V1.28W audits whether commercial aerospace already supports a lawful three-step participation ladder instead of only probe/full.",
            "If preheat-window full-quality rows have similar forward and adverse profiles to later impulse full rows and form a chronology bridge, they should be formalized as full-pre rather than collapsed back into probe.",
        ]
        return V128WCommercialAerospacePhaseStateMachineAuditReport(
            summary=summary,
            state_rows=state_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128WCommercialAerospacePhaseStateMachineAuditReport,
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
    result = V128WCommercialAerospacePhaseStateMachineAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128w_commercial_aerospace_phase_state_machine_audit_v1",
        result=result,
    )
    csv_path = write_csv_file(
        output_path=repo_root / "data" / "training" / "commercial_aerospace_phase_state_machine_rows_v1.csv",
        rows=result.state_rows,
    )
    print(output_path)
    print(csv_path)


if __name__ == "__main__":
    main()
