from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V116ICpoVisibleOnlyWiderRepairedWindowRevalidationReport:
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


class V116ICpoVisibleOnlyWiderRepairedWindowRevalidationAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v114h_payload: dict[str, Any],
        v116d_payload: dict[str, Any],
        pca_rows_path: Path,
    ) -> V116ICpoVisibleOnlyWiderRepairedWindowRevalidationReport:
        remaining_rows = list(v114h_payload.get("remaining_under_exposed_rows", []))
        remaining_days = {str(row["trade_date"]) for row in remaining_rows}
        under_gap_map = {str(row["trade_date"]): _to_float(row.get("under_exposure_gap")) for row in remaining_rows}
        breadth_map = {str(row["trade_date"]): _to_float(row.get("board_breadth")) for row in remaining_rows}
        board_ret_map = {str(row["trade_date"]): _to_float(row.get("board_avg_return")) for row in remaining_rows}

        candidate_base_rows: list[dict[str, Any]] = []
        with pca_rows_path.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                signal_trade_date = str(row["signal_trade_date"])
                if signal_trade_date not in remaining_days:
                    continue
                if str(row["action_context"]) != "add_vs_hold":
                    continue
                candidate_base_rows.append(row)

        threshold_rows = list(v116d_payload.get("threshold_rows", []))
        threshold_map = {str(row["quantile"]).replace(".", "p"): row for row in threshold_rows}
        pc1_q25 = _to_float(threshold_map["0p25"]["pc1_low_threshold"])
        pc2_q25 = _to_float(threshold_map["0p25"]["pc2_low_threshold"])

        variants = {
            "pc2_only_q_0p25": lambda row: _to_float(row["pc2_score"]) <= pc2_q25,
            "pc1_or_pc2_q_0p25": lambda row: _to_float(row["pc1_score"]) <= pc1_q25 or _to_float(row["pc2_score"]) <= pc2_q25,
        }

        variant_rows: list[dict[str, Any]] = []
        hit_rows: list[dict[str, Any]] = []
        for variant_name, predicate in variants.items():
            hits = [row for row in candidate_base_rows if predicate(row)]
            hit_count = len(hits)
            positive_rate = (
                sum(1 for row in hits if _to_float(row.get("expectancy_proxy_3d")) > 0) / hit_count if hit_count > 0 else 0.0
            )
            avg_expectancy = (
                sum(_to_float(row.get("expectancy_proxy_3d")) for row in hits) / hit_count if hit_count > 0 else 0.0
            )
            avg_adverse = (
                sum(_to_float(row.get("max_adverse_return_3d")) for row in hits) / hit_count if hit_count > 0 else 0.0
            )
            hit_day_count = len({str(row["signal_trade_date"]) for row in hits})
            variant_rows.append(
                {
                    "variant_name": variant_name,
                    "candidate_base_row_count": len(candidate_base_rows),
                    "wider_window_day_count": len(remaining_days),
                    "hit_row_count": hit_count,
                    "hit_day_count": hit_day_count,
                    "hit_day_rate": round(hit_day_count / len(remaining_days), 6) if remaining_days else 0.0,
                    "positive_expectancy_hit_rate": round(positive_rate, 6),
                    "avg_expectancy_proxy_3d": round(avg_expectancy, 6),
                    "avg_max_adverse_return_3d": round(avg_adverse, 6),
                }
            )
            for row in hits:
                signal_trade_date = str(row["signal_trade_date"])
                hit_rows.append(
                    {
                        "variant_name": variant_name,
                        "signal_trade_date": signal_trade_date,
                        "symbol": str(row["symbol"]),
                        "board_avg_return": board_ret_map.get(signal_trade_date, 0.0),
                        "board_breadth": breadth_map.get(signal_trade_date, 0.0),
                        "under_exposure_gap": under_gap_map.get(signal_trade_date, 0.0),
                        "pc1_score": round(_to_float(row["pc1_score"]), 6),
                        "pc2_score": round(_to_float(row["pc2_score"]), 6),
                        "state_band": str(row["state_band"]),
                        "expectancy_proxy_3d": round(_to_float(row.get("expectancy_proxy_3d")), 6),
                        "max_adverse_return_3d": round(_to_float(row.get("max_adverse_return_3d")), 6),
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v116i_cpo_visible_only_wider_repaired_window_revalidation_v1",
            "wider_window_day_count": len(remaining_days),
            "candidate_base_row_count": len(candidate_base_rows),
            "recommended_next_posture": "use_wider_repaired_window_revalidation_to_decide_whether_visible_only_candidates_deserve_more_replay_expansion",
        }
        interpretation = [
            "V1.16I revalidates retained visible-only candidates against a wider repaired under-exposure window rather than the original strict nine-row sample.",
            "This is still audit-only: the goal is to see whether the retained candidates have any explanatory coverage over broader repaired strong-day misses.",
            "A candidate that cannot even touch wider repaired under-exposed windows should not receive broader replay expansion priority.",
        ]
        return V116ICpoVisibleOnlyWiderRepairedWindowRevalidationReport(
            summary=summary,
            variant_rows=variant_rows,
            hit_rows=hit_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V116ICpoVisibleOnlyWiderRepairedWindowRevalidationReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116ICpoVisibleOnlyWiderRepairedWindowRevalidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114h_payload=json.loads((repo_root / "reports" / "analysis" / "v114h_cpo_promoted_sizing_behavior_audit_v1.json").read_text(encoding="utf-8")),
        v116d_payload=json.loads((repo_root / "reports" / "analysis" / "v116d_cpo_visible_only_intraday_filter_refinement_v1.json").read_text(encoding="utf-8")),
        pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116i_cpo_visible_only_wider_repaired_window_revalidation_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
