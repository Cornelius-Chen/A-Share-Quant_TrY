from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


def _parse_date_ymd(value: str) -> datetime:
    return datetime.strptime(value, "%Y%m%d")


@dataclass(slots=True)
class V132MCommercialAerospaceLocal1MinHitConcentrationAuditReport:
    summary: dict[str, Any]
    month_rows: list[dict[str, Any]]
    regime_rows: list[dict[str, Any]]
    event_overlap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "month_rows": self.month_rows,
            "regime_rows": self.regime_rows,
            "event_overlap_rows": self.event_overlap_rows,
            "interpretation": self.interpretation,
        }


class V132MCommercialAerospaceLocal1MinHitConcentrationAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.expansion_report_path = (
            repo_root / "reports" / "analysis" / "v132k_commercial_aerospace_local_1min_session_expansion_audit_v1.json"
        )
        self.event_report_path = (
            repo_root / "reports" / "analysis" / "v125m_commercial_aerospace_decisive_event_protocol_v1.json"
        )
        self.regime_report_path = (
            repo_root / "reports" / "analysis" / "v125n_commercial_aerospace_structural_regime_discovery_v1.json"
        )
        self.primary_attr_report_path = (
            repo_root / "reports" / "analysis" / "v128a_commercial_aerospace_current_primary_attribution_v1.json"
        )

    def analyze(self) -> V132MCommercialAerospaceLocal1MinHitConcentrationAuditReport:
        expansion = json.loads(self.expansion_report_path.read_text(encoding="utf-8"))
        event_report = json.loads(self.event_report_path.read_text(encoding="utf-8"))
        regime_report = json.loads(self.regime_report_path.read_text(encoding="utf-8"))
        primary_attr = json.loads(self.primary_attr_report_path.read_text(encoding="utf-8"))

        hit_rows = expansion["hit_rows"]
        regime_map = {row["trade_date"]: row["regime_semantic"] for row in regime_report["date_rows"]}

        decisive_events_by_date: dict[str, list[str]] = {}
        for row in event_report["decisive_rows"]:
            if not row.get("decisive_retained"):
                continue
            ts = row.get("public_release_time", "")
            if not ts:
                continue
            event_date = ts.split(" ")[0].replace("-", "")
            decisive_events_by_date.setdefault(event_date, []).append(row["decisive_semantic"])

        main_window = primary_attr["summary"]["largest_new_drawdown_window"]
        main_start, main_end = main_window.split("->")
        main_start_dt = _parse_date_ymd(main_start)
        main_end_dt = _parse_date_ymd(main_end)

        month_counts: dict[str, int] = {}
        regime_counts: dict[str, int] = {}
        event_overlap_counts = {
            "same_day_continuation_enabler": 0,
            "same_day_turning_point_watch": 0,
            "same_day_termination_or_regulation_risk": 0,
            "same_day_any_decisive_event": 0,
        }
        main_window_count = 0
        unique_dates = set()

        for row in hit_rows:
            unique_dates.add(row["trade_date"])
            month_counts[row["month_bucket"]] = month_counts.get(row["month_bucket"], 0) + 1
            regime = regime_map.get(row["trade_date"], "unknown")
            regime_counts[regime] = regime_counts.get(regime, 0) + 1

            trade_dt = _parse_date_ymd(row["trade_date"])
            if main_start_dt <= trade_dt <= main_end_dt:
                main_window_count += 1

            semantics = decisive_events_by_date.get(row["trade_date"], [])
            if semantics:
                event_overlap_counts["same_day_any_decisive_event"] += 1
            if "continuation_enabler" in semantics:
                event_overlap_counts["same_day_continuation_enabler"] += 1
            if "turning_point_watch" in semantics:
                event_overlap_counts["same_day_turning_point_watch"] += 1
            if "termination_or_regulation_risk" in semantics:
                event_overlap_counts["same_day_termination_or_regulation_risk"] += 1

        month_rows = [
            {"month_bucket": month, "hit_count": count}
            for month, count in sorted(month_counts.items())
        ]
        regime_rows = [
            {
                "regime_semantic": regime,
                "hit_count": count,
                "hit_share": round(count / len(hit_rows), 8) if hit_rows else 0.0,
            }
            for regime, count in sorted(regime_counts.items())
        ]
        event_overlap_rows = [
            {"event_overlap_metric": key, "count": value}
            for key, value in event_overlap_counts.items()
        ]

        summary = {
            "acceptance_posture": "freeze_v132m_commercial_aerospace_local_1min_hit_concentration_audit_v1",
            "expanded_hit_count": len(hit_rows),
            "unique_hit_trade_date_count": len(unique_dates),
            "main_window": main_window,
            "main_window_hit_count": main_window_count,
            "main_window_hit_share": round(main_window_count / len(hit_rows), 8) if hit_rows else 0.0,
            "top_month_bucket": max(month_counts, key=month_counts.get) if month_counts else "",
            "top_regime_semantic": max(regime_counts, key=regime_counts.get) if regime_counts else "",
            **event_overlap_counts,
            "authoritative_rule": "the broader local 1min hit surface is more credible when it clusters in the board's main risk window and aligns with risk-oriented regime structure rather than spraying uniformly through time",
        }
        interpretation = [
            "V1.32M studies whether the broader 1-minute hit surface is temporally concentrated in the board's major risk windows and structure regimes.",
            "The goal is to distinguish a semantically aligned downside detector from a generic weakness screen that would fire uniformly across unrelated sessions.",
        ]
        return V132MCommercialAerospaceLocal1MinHitConcentrationAuditReport(
            summary=summary,
            month_rows=month_rows,
            regime_rows=regime_rows,
            event_overlap_rows=event_overlap_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132MCommercialAerospaceLocal1MinHitConcentrationAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132MCommercialAerospaceLocal1MinHitConcentrationAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132m_commercial_aerospace_local_1min_hit_concentration_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
