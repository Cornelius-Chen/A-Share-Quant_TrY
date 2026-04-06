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


@dataclass(slots=True)
class V116ECpoVisibleOnlyCandidateAuditReport:
    summary: dict[str, Any]
    audit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "audit_rows": self.audit_rows,
            "interpretation": self.interpretation,
        }


class V116ECpoVisibleOnlyCandidateAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v115q_payload: dict[str, Any],
        v116d_payload: dict[str, Any],
    ) -> V116ECpoVisibleOnlyCandidateAuditReport:
        timing_rows = list(v115q_payload.get("timing_rows", []))
        variant_rows = list(v116d_payload.get("variant_rows", []))
        threshold_rows = list(v116d_payload.get("threshold_rows", []))
        threshold_map = {
            str(row["quantile"]).replace(".", "p"): {
                "pc1_low_threshold": _to_float(row["pc1_low_threshold"]),
                "pc2_low_threshold": _to_float(row["pc2_low_threshold"]),
            }
            for row in threshold_rows
        }

        candidate_rows = [row for row in timing_rows if str(row.get("timing_bucket")) == "intraday_same_session"]
        checkpoint_rows = [
            row for row in list(v115q_payload.get("checkpoint_rows", [])) if str(row.get("checkpoint")) == "10:30"
        ]
        checkpoint_map = {(str(row["signal_trade_date"]), str(row["symbol"])): row for row in checkpoint_rows}
        enriched_rows = []
        for row in candidate_rows:
            checkpoint = checkpoint_map.get((str(row.get("signal_trade_date")), str(row.get("symbol"))))
            if checkpoint is None:
                continue
            enriched_rows.append(
                {
                    **row,
                    "visible_pc1_score": _to_float(checkpoint.get("pc1_score")),
                    "visible_pc2_score": _to_float(checkpoint.get("pc2_score")),
                }
            )
        top_miss_keys = {
            (str(row.get("signal_trade_date")), str(row.get("symbol")))
            for row in enriched_rows
            if str(row.get("group")) == "top_miss"
        }

        def _predicate_for_variant(name: str):
            if name == "all_intraday_strict_visible":
                return lambda row: True
            parts = name.split("_q_")
            if len(parts) != 2:
                return None
            family = parts[0]
            q_tag = parts[1]
            threshold = threshold_map.get(q_tag)
            if threshold is None:
                return None
            pc1_low = threshold["pc1_low_threshold"]
            pc2_low = threshold["pc2_low_threshold"]
            if family == "pc1_only":
                return lambda row: _to_float(row.get("visible_pc1_score")) <= pc1_low
            if family == "pc2_only":
                return lambda row: _to_float(row.get("visible_pc2_score")) <= pc2_low
            if family == "pc1_or_pc2":
                return lambda row: _to_float(row.get("visible_pc1_score")) <= pc1_low or _to_float(row.get("visible_pc2_score")) <= pc2_low
            if family == "pc1_and_pc2":
                return lambda row: _to_float(row.get("visible_pc1_score")) <= pc1_low and _to_float(row.get("visible_pc2_score")) <= pc2_low
            return None

        selected_variant_names = {
            "all_intraday_strict_visible",
            "pc1_only_q_0p2",
            "pc2_only_q_0p25",
            "pc1_or_pc2_q_0p25",
        }

        audit_rows: list[dict[str, Any]] = []
        for variant in variant_rows:
            variant_name = str(variant["variant_name"])
            if variant_name not in selected_variant_names:
                continue
            predicate = _predicate_for_variant(variant_name)
            if predicate is None:
                continue
            hits = [row for row in enriched_rows if predicate(row)]
            hit_count = len(hits)
            if hit_count <= 0:
                positive_rate = 0.0
                favored_rate = 0.0
                both_rate = 0.0
                avg_expectancy = 0.0
                avg_adverse = 0.0
                top_miss_hit_count = 0
            else:
                positive_rate = sum(1 for row in hits if _to_float(row.get("expectancy_proxy_3d")) > 0) / hit_count
                favored_rate = sum(1 for row in hits if str(row.get("action_favored_3d")).lower() == "true") / hit_count
                both_rate = sum(
                    1
                    for row in hits
                    if _to_float(row.get("expectancy_proxy_3d")) > 0 and str(row.get("action_favored_3d")).lower() == "true"
                ) / hit_count
                avg_expectancy = sum(_to_float(row.get("expectancy_proxy_3d")) for row in hits) / hit_count
                avg_adverse = sum(_to_float(row.get("max_adverse_return_3d")) for row in hits) / hit_count
                top_miss_hit_count = sum(
                    1 for row in hits if (str(row.get("signal_trade_date")), str(row.get("symbol"))) in top_miss_keys
                )

            audit_rows.append(
                {
                    "variant_name": variant_name,
                    "candidate_signal_count": hit_count,
                    "executed_order_count": int(variant["executed_order_count"]),
                    "final_equity": _to_float(variant["final_equity"]),
                    "max_drawdown": _to_float(variant["max_drawdown"]),
                    "positive_expectancy_hit_rate": round(positive_rate, 6),
                    "action_favored_hit_rate": round(favored_rate, 6),
                    "positive_and_favored_hit_rate": round(both_rate, 6),
                    "avg_expectancy_proxy_3d": round(avg_expectancy, 6),
                    "avg_max_adverse_return_3d": round(avg_adverse, 6),
                    "top_miss_hit_count": top_miss_hit_count,
                    "top_miss_hit_rate": round(top_miss_hit_count / hit_count, 6) if hit_count > 0 else 0.0,
                    "audit_only_note": "future labels are used here only for evaluation, never for filter definition",
                }
            )

        best_clean = min(
            [row for row in audit_rows if row["executed_order_count"] > 0],
            key=lambda row: (row["max_drawdown"], -row["final_equity"]),
        ) if any(row["executed_order_count"] > 0 for row in audit_rows) else None
        best_expressive = max(
            [row for row in audit_rows if row["executed_order_count"] > 0 and row["variant_name"] != "all_intraday_strict_visible"],
            key=lambda row: row["final_equity"],
        ) if any(row["executed_order_count"] > 0 and row["variant_name"] != "all_intraday_strict_visible" for row in audit_rows) else None
        summary = {
            "acceptance_posture": "freeze_v116e_cpo_visible_only_candidate_audit_v1",
            "variant_count": len(audit_rows),
            "cleanest_executing_candidate": None if best_clean is None else str(best_clean["variant_name"]),
            "most_expressive_non_ceiling_candidate": None if best_expressive is None else str(best_expressive["variant_name"]),
            "recommended_next_posture": "trigger_three_run_adversarial_review_for_v116c_v116d_v116e",
        }
        interpretation = [
            "V1.16E audits visible-only executing variants using future labels strictly as after-the-fact evaluation and not as filter inputs.",
            "The goal is to understand which visible-only candidate is cleanest and which one is the best expressive middle posture before the next adversarial review.",
            "This completes the three-run block V116C/V116D/V116E and should now trigger mandatory three-subagent review.",
        ]
        return V116ECpoVisibleOnlyCandidateAuditReport(
            summary=summary,
            audit_rows=audit_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V116ECpoVisibleOnlyCandidateAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116ECpoVisibleOnlyCandidateAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v115q_payload=json.loads((repo_root / "reports" / "analysis" / "v115q_cpo_broader_strict_add_timing_audit_v1.json").read_text(encoding="utf-8")),
        v116d_payload=json.loads((repo_root / "reports" / "analysis" / "v116d_cpo_visible_only_intraday_filter_refinement_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116e_cpo_visible_only_candidate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
