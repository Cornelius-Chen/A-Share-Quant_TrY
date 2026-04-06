from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hm_commercial_aerospace_crowded_local_rebound_supervision_audit_v1 import (
    V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134HQCommercialAerospaceBoardWeakSymbolStrongConcentrationAuditV1Report:
    summary: dict[str, Any]
    module_rows: list[dict[str, Any]]
    contrast_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "module_rows": self.module_rows,
            "contrast_rows": self.contrast_rows,
            "interpretation": self.interpretation,
        }


class V134HQCommercialAerospaceBoardWeakSymbolStrongConcentrationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_board_weak_symbol_strong_concentration_v1.csv"
        )

    @staticmethod
    def _mean(rows: list[dict[str, Any]], key: str) -> float | None:
        values = [float(row[key]) for row in rows if row.get(key) not in {"", None}]
        if not values:
            return None
        return round(sum(values) / len(values), 8)

    def analyze(self) -> V134HQCommercialAerospaceBoardWeakSymbolStrongConcentrationAuditV1Report:
        base = V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Analyzer(self.repo_root).analyze()

        module_rows: list[dict[str, Any]] = []
        non_module_rows: list[dict[str, Any]] = []
        for row in base.symbol_rows:
            family = row["crowded_rebound_family"]
            peak_gap = row["post_lockout_max_vs_pre_lockout_peak"]
            peak_gap_float = float(peak_gap) if peak_gap not in {"", None} else None

            in_module = (
                family in {"crowding_like_shelter_rebound", "lockout_outlier_breakout"}
                and peak_gap_float is not None
                and peak_gap_float >= -0.05
            )
            enriched = {
                **row,
                "module_label": (
                    "board_weak_symbol_strong_concentration"
                    if in_module
                    else "outside_board_weak_symbol_strong_concentration"
                ),
                "module_reading": (
                    "symbol_can run near or through prior highs while the board remains non-restarted"
                    if in_module
                    else "symbol_strength_is_not_strong_or_concentrated_enough_to_define_the_higher_level_module"
                ),
            }
            if in_module:
                module_rows.append(enriched)
            else:
                non_module_rows.append(enriched)

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list((module_rows or non_module_rows)[0].keys()))
            writer.writeheader()
            writer.writerows(module_rows + non_module_rows)

        module_peak_gap = self._mean(module_rows, "post_lockout_max_vs_pre_lockout_peak")
        other_peak_gap = self._mean(non_module_rows, "post_lockout_max_vs_pre_lockout_peak")
        module_avg_turnover = self._mean(module_rows, "avg_turnover_rate_f")
        other_avg_turnover = self._mean(non_module_rows, "avg_turnover_rate_f")
        module_max_turnover = self._mean(module_rows, "max_turnover_rate_f")
        other_max_turnover = self._mean(non_module_rows, "max_turnover_rate_f")

        contrast_rows = [
            {
                "contrast_name": "peak_proximity_vs_other_negative_labels",
                "module_mean": module_peak_gap,
                "outside_mean": other_peak_gap,
                "mean_gap": round(module_peak_gap - other_peak_gap, 8)
                if module_peak_gap is not None and other_peak_gap is not None
                else "",
                "reading": "module members stay materially closer to prior highs than the rest of the negative-label set",
            },
            {
                "contrast_name": "avg_turnover_vs_other_negative_labels",
                "module_mean": module_avg_turnover,
                "outside_mean": other_avg_turnover,
                "mean_gap": round(module_avg_turnover - other_avg_turnover, 8)
                if module_avg_turnover is not None and other_avg_turnover is not None
                else "",
                "reading": "module members sustain heavier turnover than the rest of the negative-label set",
            },
            {
                "contrast_name": "max_turnover_vs_other_negative_labels",
                "module_mean": module_max_turnover,
                "outside_mean": other_max_turnover,
                "mean_gap": round(module_max_turnover - other_max_turnover, 8)
                if module_max_turnover is not None and other_max_turnover is not None
                else "",
                "reading": "module members produce stronger peak turnover concentration than the rest of the negative-label set",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134hq_commercial_aerospace_board_weak_symbol_strong_concentration_audit_v1",
            "analysis_symbol_count": len(base.symbol_rows),
            "module_member_count": len(module_rows),
            "outside_member_count": len(non_module_rows),
            "module_member_symbols": [row["symbol"] for row in module_rows],
            "module_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_board_weak_symbol_strong_concentration_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34HQ asks whether crowded shelter rebounds and lockout outlier breakouts are really separate families or members of one higher-level board-weak / symbol-strong concentration module.",
            "The module is intentionally negative: strong symbol-level concentration near prior highs still does not authorize board restart when breadth and board context remain absent.",
        ]
        return V134HQCommercialAerospaceBoardWeakSymbolStrongConcentrationAuditV1Report(
            summary=summary,
            module_rows=module_rows,
            contrast_rows=contrast_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HQCommercialAerospaceBoardWeakSymbolStrongConcentrationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HQCommercialAerospaceBoardWeakSymbolStrongConcentrationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hq_commercial_aerospace_board_weak_symbol_strong_concentration_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
