from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    text = str(value).strip()
    if text == "":
        return default
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


@dataclass(slots=True)
class V115MCpoIntradayStrictBandOverlayAuditReport:
    summary: dict[str, Any]
    strict_overlay_hit_rows: list[dict[str, Any]]
    miss_day_uplift_rows: list[dict[str, Any]]
    context_leakage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "strict_overlay_hit_rows": self.strict_overlay_hit_rows,
            "miss_day_uplift_rows": self.miss_day_uplift_rows,
            "context_leakage_rows": self.context_leakage_rows,
            "interpretation": self.interpretation,
        }


class V115MCpoIntradayStrictBandOverlayAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _load_band_rows(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _applicable_floor(
        *,
        board_avg_return: float,
        board_breadth: float,
        strict_symbol_count: int,
        floor_rows: list[dict[str, Any]],
    ) -> float:
        selected_floor = 0.0
        for row in floor_rows:
            trigger = dict(row.get("trigger", {}))
            avg_min = _to_float(trigger.get("board_avg_return_min"))
            breadth_min = _to_float(trigger.get("board_breadth_min"))
            floor_value = _to_float(row.get("minimum_target_gross_exposure"))
            board_state = str(row.get("board_state"))
            if board_avg_return < avg_min or board_breadth < breadth_min:
                continue
            if "two_or_more" in board_state and strict_symbol_count < 2:
                continue
            selected_floor = max(selected_floor, floor_value)
        return selected_floor

    def analyze(
        self,
        *,
        v114w_payload: dict[str, Any],
        v114x_payload: dict[str, Any],
        v115l_payload: dict[str, Any],
        band_rows: list[dict[str, Any]],
    ) -> tuple[V115MCpoIntradayStrictBandOverlayAuditReport, list[dict[str, Any]]]:
        if str(v114w_payload.get("summary", {}).get("acceptance_posture")) != "freeze_v114w_cpo_under_exposure_attribution_repaired_v1":
            raise ValueError("V115M expects repaired under-exposure attribution.")
        if str(v114x_payload.get("summary", {}).get("acceptance_posture")) != "freeze_v114x_cpo_probability_expectancy_sizing_framework_repaired_v1":
            raise ValueError("V115M expects repaired sizing grammar.")
        if str(v115l_payload.get("summary", {}).get("acceptance_posture")) != "freeze_v115l_cpo_intraday_strict_band_refinement_v1":
            raise ValueError("V115M expects V115L strict band refinement.")

        strict_bands = {
            str(row["state_band"])
            for row in list(v115l_payload.get("strict_registry_rows", []))
            if str(row.get("strict_posture")) == "strict_candidate_add_band"
        }
        floor_rows = list(v114x_payload.get("exposure_floor_rows", []))
        top_miss_rows = list(v114w_payload.get("top_opportunity_miss_rows", []))
        miss_by_date = {str(row["trade_date"]): row for row in top_miss_rows}

        annotated_rows: list[dict[str, Any]] = []
        for row in band_rows:
            annotated = dict(row)
            annotated["is_strict_candidate_add_band"] = str(row.get("state_band")) in strict_bands
            annotated_rows.append(annotated)

        top_miss_add_rows = [
            row
            for row in annotated_rows
            if str(row.get("is_top_miss_date")) == "True" and str(row.get("action_context")) == "add_vs_hold"
        ]
        strict_overlay_hit_rows = [
            {
                "signal_trade_date": str(row["signal_trade_date"]),
                "symbol": str(row["symbol"]),
                "state_band": str(row["state_band"]),
                "expectancy_proxy_3d": round(_to_float(row.get("expectancy_proxy_3d")), 6),
                "max_adverse_return_3d": round(_to_float(row.get("max_adverse_return_3d")), 6),
                "forward_close_return_3d": round(_to_float(row.get("forward_close_return_3d")), 6),
                "pc1_score": round(_to_float(row.get("pc1_score")), 6),
                "pc2_score": round(_to_float(row.get("pc2_score")), 6),
            }
            for row in top_miss_add_rows
            if bool(row.get("is_strict_candidate_add_band"))
        ]

        miss_day_uplift_rows: list[dict[str, Any]] = []
        for trade_date in sorted({row["signal_trade_date"] for row in strict_overlay_hit_rows}):
            hit_rows = [row for row in strict_overlay_hit_rows if str(row["signal_trade_date"]) == trade_date]
            miss_row = miss_by_date[trade_date]
            current_exposure = _to_float(miss_row.get("gross_exposure_after_close"))
            board_avg_return = _to_float(miss_row.get("board_avg_return"))
            board_breadth = _to_float(miss_row.get("board_breadth"))
            target_floor = self._applicable_floor(
                board_avg_return=board_avg_return,
                board_breadth=board_breadth,
                strict_symbol_count=len(hit_rows),
                floor_rows=floor_rows,
            )
            miss_day_uplift_rows.append(
                {
                    "trade_date": trade_date,
                    "strict_hit_symbol_count": len(hit_rows),
                    "strict_hit_symbols": ",".join(sorted(str(row["symbol"]) for row in hit_rows)),
                    "board_avg_return": round(board_avg_return, 6),
                    "board_breadth": round(board_breadth, 6),
                    "current_gross_exposure_after_close": round(current_exposure, 6),
                    "target_gross_exposure_floor_from_v114x": round(target_floor, 6),
                    "gross_exposure_gap_to_floor": round(max(target_floor - current_exposure, 0.0), 6),
                    "strict_hit_expectancy_mean": round(_mean([_to_float(row["expectancy_proxy_3d"]) for row in hit_rows]), 6),
                    "strict_hit_adverse_mean": round(_mean([_to_float(row["max_adverse_return_3d"]) for row in hit_rows]), 6),
                }
            )

        context_leakage_rows: list[dict[str, Any]] = []
        for action_context in sorted({str(row["action_context"]) for row in annotated_rows}):
            rows = [row for row in annotated_rows if str(row["action_context"]) == action_context]
            strict_rows = [row for row in rows if bool(row.get("is_strict_candidate_add_band"))]
            context_leakage_rows.append(
                {
                    "action_context": action_context,
                    "row_count": len(rows),
                    "strict_add_band_rate": round(len(strict_rows) / len(rows), 6) if rows else 0.0,
                    "avg_expectancy_proxy_3d_when_strict": round(
                        _mean([_to_float(row.get("expectancy_proxy_3d")) for row in strict_rows]),
                        6,
                    ),
                    "avg_max_adverse_return_3d_when_strict": round(
                        _mean([_to_float(row.get("max_adverse_return_3d")) for row in strict_rows]),
                        6,
                    ),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v115m_cpo_intraday_strict_band_overlay_audit_v1",
            "strict_add_band_count": len(strict_bands),
            "top_miss_day_count": len(top_miss_rows),
            "top_miss_add_row_count": len(top_miss_add_rows),
            "strict_hit_miss_day_count": len(miss_day_uplift_rows),
            "strict_hit_miss_row_count": len(strict_overlay_hit_rows),
            "strict_hit_rate_vs_top_miss_days": round(len(miss_day_uplift_rows) / len(top_miss_rows), 6) if top_miss_rows else 0.0,
            "strict_hit_rate_vs_top_miss_rows": round(len(strict_overlay_hit_rows) / len(top_miss_add_rows), 6) if top_miss_add_rows else 0.0,
            "strict_hit_expectancy_mean": round(_mean([_to_float(row["expectancy_proxy_3d"]) for row in strict_overlay_hit_rows]), 6),
            "strict_hit_adverse_mean": round(_mean([_to_float(row["max_adverse_return_3d"]) for row in strict_overlay_hit_rows]), 6),
            "all_top_miss_expectancy_mean": round(_mean([_to_float(row.get("expectancy_proxy_3d")) for row in top_miss_add_rows]), 6),
            "all_top_miss_adverse_mean": round(_mean([_to_float(row.get("max_adverse_return_3d")) for row in top_miss_add_rows]), 6),
            "strict_add_leakage_into_entry_rate": next(
                row["strict_add_band_rate"] for row in context_leakage_rows if row["action_context"] == "entry_vs_skip"
            ),
            "strict_add_leakage_into_close_rate": next(
                row["strict_add_band_rate"] for row in context_leakage_rows if row["action_context"] == "close_vs_hold"
            ),
            "strict_add_leakage_into_reduce_rate": next(
                row["strict_add_band_rate"] for row in context_leakage_rows if row["action_context"] == "reduce_vs_hold"
            ),
            "recommended_next_posture": "strict_bands_can_only_be_tested_as_held_position_overlay_not_as_new_entry_law",
            "candidate_only_overlay": True,
        }

        interpretation = [
            "V1.15M audits only the strict add bands from V115L against repaired miss days; it does not bind them into replay law.",
            "The strict overlay is cleaner than the permissive V115K add posture, but it only covers a subset of repaired miss days.",
            "Because strict add bands still leak heavily into entry_vs_skip, the next replay-facing test must stay constrained to already-held mature names rather than opening fresh admissions from intraday bands.",
        ]

        report = V115MCpoIntradayStrictBandOverlayAuditReport(
            summary=summary,
            strict_overlay_hit_rows=strict_overlay_hit_rows,
            miss_day_uplift_rows=miss_day_uplift_rows,
            context_leakage_rows=context_leakage_rows,
            interpretation=interpretation,
        )
        return report, annotated_rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115MCpoIntradayStrictBandOverlayAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115MCpoIntradayStrictBandOverlayAuditAnalyzer(repo_root=repo_root)
    report, annotated_rows = analyzer.analyze(
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v114x_payload=json.loads((repo_root / "reports" / "analysis" / "v114x_cpo_probability_expectancy_sizing_framework_repaired_v1.json").read_text(encoding="utf-8")),
        v115l_payload=json.loads((repo_root / "reports" / "analysis" / "v115l_cpo_intraday_strict_band_refinement_v1.json").read_text(encoding="utf-8")),
        band_rows=V115MCpoIntradayStrictBandOverlayAuditAnalyzer._load_band_rows(
            repo_root / "data" / "training" / "cpo_midfreq_band_action_audit_rows_v1.csv"
        ),
    )
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_intraday_strict_band_overlay_audit_rows_v1.csv",
        rows=annotated_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115m_cpo_intraday_strict_band_overlay_audit_v1",
        result=report,
    )
    print(output_path)


if __name__ == "__main__":
    main()
