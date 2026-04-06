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
class V126ACommercialAerospaceRegimeConditionedLabelTableReport:
    summary: dict[str, Any]
    training_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "training_rows": self.training_rows,
            "interpretation": self.interpretation,
        }


class V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V126ACommercialAerospaceRegimeConditionedLabelTableReport:
        base = V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer(self.repo_root).analyze()
        rows = [dict(row) for row in base.training_rows]

        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            grouped.setdefault(row["regime_proxy_semantic"], []).append(row)

        label_counts: dict[str, int] = {}
        for regime, members in grouped.items():
            forward_values = [float(row["forward_return_10"]) for row in members]
            adverse_values = [float(row["max_adverse_return_10"]) for row in members]
            q20 = _quantile(forward_values, 0.20)
            q60 = _quantile(forward_values, 0.60)
            q80 = _quantile(forward_values, 0.80)
            adverse_q20 = _quantile(adverse_values, 0.20)
            adverse_q50 = _quantile(adverse_values, 0.50)

            for row in members:
                forward_return = float(row["forward_return_10"])
                adverse_return = float(row["max_adverse_return_10"])
                event_state = row["event_state"]
                if regime == "impulse_expansion_proxy":
                    if forward_return >= q60 and adverse_return > adverse_q50 and event_state == "continuation_active":
                        label = "full_eligibility_target"
                    elif forward_return >= q20 and adverse_return > adverse_q20:
                        label = "probe_eligibility_target"
                    elif adverse_return <= adverse_q20:
                        label = "de_risk_target"
                    else:
                        label = "neutral_hold"
                elif regime == "sentiment_overdrive_transition_proxy":
                    if adverse_return <= adverse_q20:
                        label = "de_risk_target"
                    elif forward_return >= q80 and event_state == "continuation_active":
                        label = "probe_eligibility_target"
                    else:
                        label = "neutral_hold"
                elif regime == "risk_off_deterioration_proxy":
                    if adverse_return <= adverse_q20 or forward_return <= q20:
                        label = "de_risk_target"
                    else:
                        label = "neutral_hold"
                else:
                    if forward_return >= q80 and adverse_return > adverse_q50 and event_state == "continuation_active":
                        label = "probe_eligibility_target"
                    elif adverse_return <= adverse_q20:
                        label = "de_risk_target"
                    else:
                        label = "neutral_hold"

                row["supervised_action_label_rc"] = label
                label_counts[label] = label_counts.get(label, 0) + 1

        summary = {
            "acceptance_posture": "freeze_v126a_commercial_aerospace_regime_conditioned_label_table_v1",
            "row_count": len(rows),
            "symbol_count": len({row["symbol"] for row in rows}),
            "label_counts": label_counts,
            "authoritative_rule": "commercial_aerospace_eod_supervision_should_use_regime_conditioned_labels_not_single_global_quantiles",
        }
        interpretation = [
            "V1.26A rebuilds the lawful EOD label table with regime-conditioned supervision so that impulse, preheat, and risk-off states do not share one global label geometry.",
            "This is the first attempt to make commercial-aerospace action learning economically closer to the board's true structure.",
        ]
        return V126ACommercialAerospaceRegimeConditionedLabelTableReport(
            summary=summary,
            training_rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V126ACommercialAerospaceRegimeConditionedLabelTableReport,
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
    result = V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126a_commercial_aerospace_regime_conditioned_label_table_v1",
        result=result,
    )
    csv_path = write_csv_file(
        output_path=repo_root / "data" / "training" / "commercial_aerospace_regime_conditioned_label_table_v1.csv",
        rows=result.training_rows,
    )
    print(output_path)
    print(csv_path)


if __name__ == "__main__":
    main()
