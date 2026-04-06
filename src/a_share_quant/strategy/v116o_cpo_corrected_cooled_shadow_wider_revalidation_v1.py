from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


@dataclass(slots=True)
class V116OCpoCorrectedCooledShadowWiderRevalidationReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    hit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "hit_rows": self.hit_rows,
            "interpretation": self.interpretation,
        }


class V116OCpoCorrectedCooledShadowWiderRevalidationAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v114w_payload: dict[str, Any],
        v116j_payload: dict[str, Any],
        v116n_payload: dict[str, Any],
    ) -> V116OCpoCorrectedCooledShadowWiderRevalidationReport:
        repaired_rows = list(v114w_payload.get("top_opportunity_miss_rows", []))
        repaired_days = {str(row["trade_date"]) for row in repaired_rows}
        gap_map = {str(row["trade_date"]): _to_float(row.get("under_exposure_gap")) for row in repaired_rows}
        breadth_map = {str(row["trade_date"]): _to_float(row.get("board_breadth")) for row in repaired_rows}
        board_ret_map = {str(row["trade_date"]): _to_float(row.get("board_avg_return")) for row in repaired_rows}

        timing_rows = [
            row for row in list(v116j_payload.get("timing_rows", []))
            if str(row.get("signal_trade_date")) in repaired_days
        ]
        checkpoint_rows = [
            row for row in list(v116j_payload.get("checkpoint_rows", []))
            if str(row.get("signal_trade_date")) in repaired_days
        ]
        checkpoint_map: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in checkpoint_rows:
            checkpoint_map.setdefault((str(row["signal_trade_date"]), str(row["symbol"])), []).append(row)
        for rows in checkpoint_map.values():
            rows.sort(key=lambda row: str(row["checkpoint"]))

        def has_pass(row_key: tuple[str, str], checkpoint: str) -> bool:
            for row in checkpoint_map.get(row_key, []):
                if str(row["checkpoint"]) == checkpoint:
                    return _to_bool(row.get("passes_pc1_or_pc2_q_0p25"))
            return False

        def earliest_late_checkpoint(row_key: tuple[str, str]) -> str | None:
            for checkpoint in ("14:00", "14:30"):
                if has_pass(row_key, checkpoint):
                    return checkpoint
            return None

        retained_name = str(v116n_payload.get("summary", {}).get("retained_variant_name"))
        if retained_name != "double_confirm_late_quarter":
            raise ValueError(f"unexpected_retained_variant:{retained_name}")

        def corrected_candidate(row: dict[str, Any]) -> bool:
            row_key = (str(row["signal_trade_date"]), str(row["symbol"]))
            return (
                str(row.get("timing_bucket")) == "intraday_same_session"
                and has_pass(row_key, "10:30")
                and has_pass(row_key, "11:00")
                and earliest_late_checkpoint(row_key) is not None
            )

        def hot_upper_bound(row: dict[str, Any]) -> bool:
            return str(row.get("timing_bucket")) == "intraday_same_session"

        variants = {
            "corrected_cooled_shadow_candidate": corrected_candidate,
            "hot_upper_bound_reference": hot_upper_bound,
        }

        variant_rows: list[dict[str, Any]] = []
        hit_rows: list[dict[str, Any]] = []
        for variant_name, predicate in variants.items():
            hits = [row for row in timing_rows if predicate(row)]
            hit_count = len(hits)
            hit_day_count = len({str(row["signal_trade_date"]) for row in hits})
            positive_rate = (
                sum(1 for row in hits if _to_float(row.get("expectancy_proxy_3d")) > 0) / hit_count if hit_count > 0 else 0.0
            )
            avg_expectancy = (
                sum(_to_float(row.get("expectancy_proxy_3d")) for row in hits) / hit_count if hit_count > 0 else 0.0
            )
            avg_adverse = (
                sum(_to_float(row.get("max_adverse_return_3d")) for row in hits) / hit_count if hit_count > 0 else 0.0
            )
            variant_rows.append(
                {
                    "variant_name": variant_name,
                    "wider_window_day_count": len(repaired_days),
                    "candidate_base_row_count": len(timing_rows),
                    "hit_row_count": hit_count,
                    "hit_day_count": hit_day_count,
                    "hit_day_rate": round(hit_day_count / len(repaired_days), 6) if repaired_days else 0.0,
                    "positive_expectancy_hit_rate": round(positive_rate, 6),
                    "avg_expectancy_proxy_3d": round(avg_expectancy, 6),
                    "avg_max_adverse_return_3d": round(avg_adverse, 6),
                }
            )
            for row in hits:
                signal_trade_date = str(row["signal_trade_date"])
                row_key = (signal_trade_date, str(row["symbol"]))
                hit_rows.append(
                    {
                        "variant_name": variant_name,
                        "signal_trade_date": signal_trade_date,
                        "symbol": str(row["symbol"]),
                        "timing_bucket": str(row.get("timing_bucket")),
                        "earliest_visible_checkpoint": str(row.get("earliest_visible_checkpoint")),
                        "late_confirmation_checkpoint": earliest_late_checkpoint(row_key),
                        "board_avg_return": board_ret_map.get(signal_trade_date, 0.0),
                        "board_breadth": breadth_map.get(signal_trade_date, 0.0),
                        "under_exposure_gap": gap_map.get(signal_trade_date, 0.0),
                        "visible_pc1_score": round(_to_float(row.get("visible_pc1_score")), 6),
                        "visible_pc2_score": round(_to_float(row.get("visible_pc2_score")), 6),
                        "expectancy_proxy_3d": round(_to_float(row.get("expectancy_proxy_3d")), 6),
                        "max_adverse_return_3d": round(_to_float(row.get("max_adverse_return_3d")), 6),
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v116o_cpo_corrected_cooled_shadow_wider_revalidation_v1",
            "retained_variant_name": retained_name,
            "wider_window_day_count": len(repaired_days),
            "candidate_base_row_count": len(timing_rows),
            "recommended_next_posture": "use_corrected_cooled_shadow_candidate_as_the_only_visible_only_retained_object_but_keep_candidate_only",
        }
        interpretation = [
            "V1.16O revalidates the corrected cooled-shadow retained object from V116N against the wider repaired under-exposure window rather than the original narrow strict sample.",
            "This is still candidate-only and audit-facing: the goal is to measure whether the corrected retained object keeps enough repaired-window explanatory power after the V116M/V116N correction.",
            "The hot upper bound is kept only as a reference line so the project can compare cleaner retained coverage against the wider expressive ceiling without confusing the two objects.",
        ]
        return V116OCpoCorrectedCooledShadowWiderRevalidationReport(
            summary=summary,
            variant_rows=variant_rows,
            hit_rows=hit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116OCpoCorrectedCooledShadowWiderRevalidationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116OCpoCorrectedCooledShadowWiderRevalidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v116j_payload=json.loads((repo_root / "reports" / "analysis" / "v116j_cpo_visible_only_broader_shadow_replay_v1.json").read_text(encoding="utf-8")),
        v116n_payload=json.loads((repo_root / "reports" / "analysis" / "v116n_cpo_corrected_cooled_shadow_retention_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116o_cpo_corrected_cooled_shadow_wider_revalidation_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
