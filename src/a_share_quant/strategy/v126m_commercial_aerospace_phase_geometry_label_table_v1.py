from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125t_commercial_aerospace_lawful_supervised_action_training_table_v1 import (
    V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer,
)


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[idx]


@dataclass(slots=True)
class V126MCommercialAerospacePhaseGeometryLabelTableReport:
    summary: dict[str, Any]
    training_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "training_rows": self.training_rows,
            "interpretation": self.interpretation,
        }


class V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer:
    PREHEAT_START = "20251114"
    PREHEAT_END = "20251223"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _in_preheat_window(self, trade_date: str) -> bool:
        return self.PREHEAT_START <= trade_date <= self.PREHEAT_END

    def analyze(self) -> V126MCommercialAerospacePhaseGeometryLabelTableReport:
        base = V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer(self.repo_root).analyze()
        rows = [dict(row) for row in base.training_rows]

        preheat_rows = [row for row in rows if self._in_preheat_window(row["trade_date"])]
        impulse_rows = [
            row
            for row in rows
            if row["regime_proxy_semantic"] == "impulse_expansion_proxy" and row["event_state"] == "continuation_active"
        ]

        preheat_forward = [float(row["forward_return_10"]) for row in preheat_rows]
        preheat_adverse = [float(row["max_adverse_return_10"]) for row in preheat_rows]
        preheat_support_combo = [
            float(row["local_quality_support"]) + float(row["local_heat_support"]) + float(row["board_total_support"])
            for row in preheat_rows
        ]
        impulse_forward = [float(row["forward_return_10"]) for row in impulse_rows]
        impulse_adverse = [float(row["max_adverse_return_10"]) for row in impulse_rows]

        preheat_q60 = _quantile(preheat_forward, 0.60)
        preheat_q80 = _quantile(preheat_forward, 0.80)
        preheat_q20 = _quantile(preheat_forward, 0.20)
        preheat_adverse_q20 = _quantile(preheat_adverse, 0.20)
        preheat_adverse_q50 = _quantile(preheat_adverse, 0.50)
        preheat_support_q60 = _quantile(preheat_support_combo, 0.60)

        impulse_q20 = _quantile(impulse_forward, 0.20)
        impulse_q60 = _quantile(impulse_forward, 0.60)
        impulse_adverse_q20 = _quantile(impulse_adverse, 0.20)
        impulse_adverse_q50 = _quantile(impulse_adverse, 0.50)

        label_counts: dict[str, int] = {}
        full_preheat_count = 0
        full_impulse_count = 0
        for row in rows:
            trade_date = row["trade_date"]
            forward_return = float(row["forward_return_10"])
            adverse_return = float(row["max_adverse_return_10"])
            support_combo = (
                float(row["local_quality_support"]) + float(row["local_heat_support"]) + float(row["board_total_support"])
            )
            regime = row["regime_proxy_semantic"]
            event_state = row["event_state"]

            if self._in_preheat_window(trade_date):
                phase_window = "preheat_window"
                if (
                    forward_return >= preheat_q80
                    and adverse_return > preheat_adverse_q50
                    and support_combo >= preheat_support_q60
                ):
                    label = "full_eligibility_target"
                    full_preheat_count += 1
                elif forward_return >= preheat_q60 and adverse_return > preheat_adverse_q20:
                    label = "probe_eligibility_target"
                elif forward_return <= preheat_q20 and adverse_return <= preheat_adverse_q20:
                    label = "de_risk_target"
                else:
                    label = "neutral_hold"
            elif regime == "impulse_expansion_proxy" and event_state == "continuation_active":
                phase_window = "impulse_window"
                if forward_return >= impulse_q60 and adverse_return > impulse_adverse_q50:
                    label = "full_eligibility_target"
                    full_impulse_count += 1
                elif forward_return >= impulse_q20 and adverse_return > impulse_adverse_q20:
                    label = "probe_eligibility_target"
                elif adverse_return <= impulse_adverse_q20:
                    label = "de_risk_target"
                else:
                    label = "neutral_hold"
            elif regime in {"risk_off_deterioration_proxy", "sentiment_overdrive_transition_proxy"}:
                phase_window = "risk_or_overdrive_window"
                if adverse_return <= _quantile(
                    [float(item["max_adverse_return_10"]) for item in rows if item["regime_proxy_semantic"] == regime], 0.20
                ):
                    label = "de_risk_target"
                else:
                    label = "neutral_hold"
            else:
                phase_window = "other_window"
                if event_state == "continuation_active" and forward_return >= _quantile(
                    [float(item["forward_return_10"]) for item in rows if item["regime_proxy_semantic"] == regime], 0.80
                ):
                    label = "probe_eligibility_target"
                else:
                    label = "neutral_hold"

            row["phase_window_semantic"] = phase_window
            row["supervised_action_label_pg"] = label
            label_counts[label] = label_counts.get(label, 0) + 1

        summary = {
            "acceptance_posture": "freeze_v126m_commercial_aerospace_phase_geometry_label_table_v1",
            "row_count": len(rows),
            "symbol_count": len({row["symbol"] for row in rows}),
            "preheat_start": self.PREHEAT_START,
            "preheat_end": self.PREHEAT_END,
            "preheat_q60": round(preheat_q60, 8),
            "preheat_q80": round(preheat_q80, 8),
            "preheat_support_q60": round(preheat_support_q60, 8),
            "full_preheat_count": full_preheat_count,
            "full_impulse_count": full_impulse_count,
            "label_counts": label_counts,
            "authoritative_rule": "commercial_aerospace_supervision_should_use_phase_geometry_where_preheat_and_impulse_are_distinct_action_windows_not_one_probe_bucket",
        }
        interpretation = [
            "V1.26M rebuilds commercial-aerospace labels around the observed preheat-to-impulse sequence instead of only regime buckets.",
            "This specifically tests whether 2025-11-14 to 2025-12-23 should contribute lawful preheat/full support to later replay learning.",
        ]
        return V126MCommercialAerospacePhaseGeometryLabelTableReport(
            summary=summary,
            training_rows=rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V126MCommercialAerospacePhaseGeometryLabelTableReport) -> Path:
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
    result = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126m_commercial_aerospace_phase_geometry_label_table_v1",
        result=result,
    )
    csv_path = write_csv_file(
        output_path=repo_root / "data" / "training" / "commercial_aerospace_phase_geometry_label_table_v1.csv",
        rows=result.training_rows,
    )
    print(output_path)
    print(csv_path)


if __name__ == "__main__":
    main()
