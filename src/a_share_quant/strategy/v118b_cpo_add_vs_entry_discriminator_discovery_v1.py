from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FEATURES = (
    "f30_breakout_efficiency_rz",
    "f60_breakout_efficiency_rz",
    "f30_high_time_ratio_rz",
    "d5_30_close_vs_vwap_rz",
    "d15_60_close_vs_vwap_rz",
    "f60_last_bar_return_rz",
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _is_positive_add(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "add_vs_hold"
        and str(row.get("action_favored_3d")) == "True"
        and _to_float(row.get("expectancy_proxy_3d")) > 0.0
        and _to_float(row.get("max_adverse_return_3d")) > -0.04
    )


def _base_controlled_score(row: dict[str, Any]) -> float:
    d5_last = max(_to_float(row.get("d5_30_last_bar_return_rz")), 0.0)
    f60_high = max(_to_float(row.get("f60_high_time_ratio_rz")) - 750000000.0, 0.0)
    close_stretch = max(_to_float(row.get("f60_close_location_rz")) - 850000000.0, 0.0)
    base = (
        -_to_float(row.get("d5_30_last_bar_return_rz"))
        + _to_float(row.get("f30_last_bar_return_rz"))
        + _to_float(row.get("f30_afternoon_volume_share_rz"))
        + _to_float(row.get("f60_afternoon_volume_share_rz"))
        + _to_float(row.get("f30_high_time_ratio_rz"))
        + _to_float(row.get("f60_high_time_ratio_rz"))
        + _to_float(row.get("f60_close_vs_vwap_rz"))
        - _to_float(row.get("d5_30_close_vs_vwap_rz"))
        - _to_float(row.get("d15_60_close_vs_vwap_rz"))
        - _to_float(row.get("f30_close_location_rz"))
        - _to_float(row.get("f60_close_location_rz"))
    )
    return base - (d5_last + f60_high + close_stretch)


def _entry_separation_score(row: dict[str, Any]) -> float:
    return (
        _to_float(row.get("f30_breakout_efficiency_rz"))
        + _to_float(row.get("f60_breakout_efficiency_rz"))
        + _to_float(row.get("f30_high_time_ratio_rz"))
        - _to_float(row.get("d5_30_close_vs_vwap_rz"))
        - _to_float(row.get("d15_60_close_vs_vwap_rz"))
        - _to_float(row.get("f60_last_bar_return_rz"))
    )


@dataclass(slots=True)
class V118BCpoAddVsEntryDiscriminatorDiscoveryReport:
    summary: dict[str, Any]
    feature_rows: list[dict[str, Any]]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_rows": self.feature_rows,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V118BCpoAddVsEntryDiscriminatorDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path, carried_threshold: float) -> V118BCpoAddVsEntryDiscriminatorDiscoveryReport:
        rows = _load_csv_rows(rows_path)
        positive_add_rows = [row for row in rows if _is_positive_add(row)]
        leaked_entry_rows = [
            row
            for row in rows
            if str(row.get("action_context")) == "entry_vs_skip"
            and _base_controlled_score(row) >= carried_threshold
        ]

        feature_rows: list[dict[str, Any]] = []
        for feature_name in FEATURES:
            add_mean = sum(_to_float(row.get(feature_name)) for row in positive_add_rows) / len(positive_add_rows)
            entry_mean = sum(_to_float(row.get(feature_name)) for row in leaked_entry_rows) / len(leaked_entry_rows)
            feature_rows.append(
                {
                    "feature_name": feature_name,
                    "positive_add_mean": round(add_mean, 6),
                    "leaked_entry_mean": round(entry_mean, 6),
                    "mean_gap_add_minus_entry": round(add_mean - entry_mean, 6),
                    "abs_gap": round(abs(add_mean - entry_mean), 6),
                }
            )
        feature_rows.sort(key=lambda row: row["abs_gap"], reverse=True)

        candidate_rows: list[dict[str, Any]] = []
        for row in positive_add_rows:
            candidate_rows.append(
                {
                    "label_family": "positive_add",
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "score": round(_entry_separation_score(row), 6),
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                }
            )
        for row in leaked_entry_rows:
            candidate_rows.append(
                {
                    "label_family": "leaked_entry",
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "score": round(_entry_separation_score(row), 6),
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                }
            )
        candidate_rows.sort(key=lambda row: (row["label_family"] != "positive_add", -_to_float(row["score"])))

        pos_mean = sum(_to_float(row["score"]) for row in candidate_rows if row["label_family"] == "positive_add") / len(positive_add_rows)
        neg_mean = sum(_to_float(row["score"]) for row in candidate_rows if row["label_family"] == "leaked_entry") / len(leaked_entry_rows)
        summary = {
            "acceptance_posture": "freeze_v118b_cpo_add_vs_entry_discriminator_discovery_v1",
            "candidate_name": "add_vs_strong_entry_separation_score_candidate",
            "positive_add_row_count": len(positive_add_rows),
            "leaked_entry_row_count": len(leaked_entry_rows),
            "mean_gap_positive_add_minus_leaked_entry": round(pos_mean - neg_mean, 6),
            "top_separation_feature": feature_rows[0]["feature_name"],
            "recommended_next_posture": "audit_candidate_on_full_add_vs_all_entry_pool_and_keep_candidate_only",
        }
        interpretation = [
            "V1.18B does not search for another generic false-positive filter. It targets the now-authoritative problem directly: separating true add windows from strong entry windows that look add-like.",
            "The score intentionally rewards stronger breakout efficiency and persistent intraday occupancy while punishing overly warm prior anchors and late-bar chase behavior.",
            "This is still discovery only. It becomes real only if it survives a full add-vs-all-entry external audit next.",
        ]
        return V118BCpoAddVsEntryDiscriminatorDiscoveryReport(
            summary=summary,
            feature_rows=feature_rows,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118BCpoAddVsEntryDiscriminatorDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V118BCpoAddVsEntryDiscriminatorDiscoveryAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        carried_threshold=489402000.0,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118b_cpo_add_vs_entry_discriminator_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
