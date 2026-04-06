from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    idx = (len(sorted_values) - 1) * q
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_values[lo]
    weight = idx - lo
    return sorted_values[lo] * (1 - weight) + sorted_values[hi] * weight


@dataclass(slots=True)
class V116GCpoVisibleOnlyTimeSplitThresholdRebuildReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V116GCpoVisibleOnlyTimeSplitThresholdRebuildAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v115q_payload: dict[str, Any]) -> V116GCpoVisibleOnlyTimeSplitThresholdRebuildReport:
        timing_rows = [row for row in list(v115q_payload.get("timing_rows", [])) if str(row.get("timing_bucket")) == "intraday_same_session"]
        checkpoint_rows = [row for row in list(v115q_payload.get("checkpoint_rows", [])) if str(row.get("checkpoint")) == "10:30"]
        checkpoint_map = {(str(row["signal_trade_date"]), str(row["symbol"])): row for row in checkpoint_rows}
        rows: list[dict[str, Any]] = []
        for row in timing_rows:
            cp = checkpoint_map.get((str(row["signal_trade_date"]), str(row["symbol"])))
            if cp is None:
                continue
            rows.append(
                {
                    **row,
                    "visible_pc1_score": _to_float(cp.get("pc1_score")),
                    "visible_pc2_score": _to_float(cp.get("pc2_score")),
                    "signal_date": date.fromisoformat(str(row["signal_trade_date"])),
                }
            )
        early = [row for row in rows if row["signal_date"] < date(2024, 1, 1)]
        late = [row for row in rows if row["signal_date"] >= date(2024, 1, 1)]

        def _evaluate_split(calibration_rows: list[dict[str, Any]], validation_rows: list[dict[str, Any]], split_name: str) -> list[dict[str, Any]]:
            if not calibration_rows or not validation_rows:
                return []
            pc1_values = sorted(_to_float(row["visible_pc1_score"]) for row in calibration_rows)
            pc2_values = sorted(_to_float(row["visible_pc2_score"]) for row in calibration_rows)
            pc1_q20 = _quantile(pc1_values, 0.2)
            pc2_q25 = _quantile(pc2_values, 0.25)
            variants = {
                "all_intraday_strict_visible": lambda row: True,
                "pc1_only_q_0p2": lambda row, pc1_q20=pc1_q20: _to_float(row["visible_pc1_score"]) <= pc1_q20,
                "pc2_only_q_0p25": lambda row, pc2_q25=pc2_q25: _to_float(row["visible_pc2_score"]) <= pc2_q25,
                "pc1_or_pc2_q_0p25": lambda row, pc1_q20=pc1_q20, pc2_q25=pc2_q25: _to_float(row["visible_pc1_score"]) <= pc1_q20
                or _to_float(row["visible_pc2_score"]) <= pc2_q25,
            }
            split_rows: list[dict[str, Any]] = []
            for name, predicate in variants.items():
                hits = [row for row in validation_rows if predicate(row)]
                hit_count = len(hits)
                split_rows.append(
                    {
                        "split_name": split_name,
                        "variant_name": name,
                        "calibration_count": len(calibration_rows),
                        "validation_count": len(validation_rows),
                        "validation_hit_count": hit_count,
                        "validation_hit_rate": round(hit_count / len(validation_rows), 6) if validation_rows else 0.0,
                        "validation_positive_expectancy_rate": round(
                            sum(1 for row in hits if _to_float(row.get("expectancy_proxy_3d")) > 0) / hit_count, 6
                        ) if hit_count > 0 else 0.0,
                        "validation_avg_expectancy_proxy_3d": round(
                            sum(_to_float(row.get("expectancy_proxy_3d")) for row in hits) / hit_count, 6
                        ) if hit_count > 0 else 0.0,
                        "validation_avg_max_adverse_return_3d": round(
                            sum(_to_float(row.get("max_adverse_return_3d")) for row in hits) / hit_count, 6
                        ) if hit_count > 0 else 0.0,
                        "pc1_q20_from_calibration": round(pc1_q20, 6),
                        "pc2_q25_from_calibration": round(pc2_q25, 6),
                    }
                )
            return split_rows

        split_rows = []
        split_rows.extend(_evaluate_split(early, late, "early_to_late"))
        split_rows.extend(_evaluate_split(late, early, "late_to_early"))

        summary = {
            "acceptance_posture": "freeze_v116g_cpo_visible_only_time_split_threshold_rebuild_v1",
            "row_count": len(rows),
            "early_count": len(early),
            "late_count": len(late),
            "recommended_next_posture": "use_time_split_rows_as_the_primary_guardrail_against_same_sample_lucky_bands",
        }
        interpretation = [
            "V1.16G rebuilds visible-only thresholds on one time slice and audits them on the other slice, rather than cutting quantiles and judging them on the same nine windows.",
            "This is a direct response to the main methodological objection raised in the first visible-only adversarial review.",
            "The report is audit-only and should be used to demote same-sample lucky bands before any further replay expansion.",
        ]
        return V116GCpoVisibleOnlyTimeSplitThresholdRebuildReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V116GCpoVisibleOnlyTimeSplitThresholdRebuildReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116GCpoVisibleOnlyTimeSplitThresholdRebuildAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v115q_payload=json.loads((repo_root / "reports" / "analysis" / "v115q_cpo_broader_strict_add_timing_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116g_cpo_visible_only_time_split_threshold_rebuild_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
