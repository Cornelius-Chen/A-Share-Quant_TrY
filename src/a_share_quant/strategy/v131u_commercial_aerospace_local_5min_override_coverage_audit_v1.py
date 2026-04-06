from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131UCommercialAerospaceLocal5MinOverrideCoverageAuditReport:
    summary: dict[str, Any]
    label_breakdown_rows: list[dict[str, Any]]
    semantic_breakdown_rows: list[dict[str, Any]]
    flagged_non_override_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "label_breakdown_rows": self.label_breakdown_rows,
            "semantic_breakdown_rows": self.semantic_breakdown_rows,
            "flagged_non_override_rows": self.flagged_non_override_rows,
            "interpretation": self.interpretation,
        }


class V131UCommercialAerospaceLocal5MinOverrideCoverageAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.prototype_report_path = (
            repo_root / "reports" / "analysis" / "v131s_commercial_aerospace_local_5min_override_prototype_audit_v1.json"
        )

    @staticmethod
    def _safe_float(value: Any) -> float:
        return float(value) if value not in ("", None) else 0.0

    def analyze(self) -> V131UCommercialAerospaceLocal5MinOverrideCoverageAuditReport:
        prototype = json.loads(self.prototype_report_path.read_text(encoding="utf-8"))
        rows = prototype["prototype_rows"]

        label_breakdown_rows: list[dict[str, Any]] = []
        for label in sorted({row["supervision_label"] for row in rows}):
            subset = [row for row in rows if row["supervision_label"] == label]
            hit_count = sum(1 for row in subset if bool(row["prototype_flag"]))
            label_breakdown_rows.append(
                {
                    "supervision_label": label,
                    "row_count": len(subset),
                    "prototype_hit_count": hit_count,
                    "prototype_hit_rate": round(hit_count / len(subset), 8) if subset else 0.0,
                    "mean_ret15": round(sum(self._safe_float(row["ret15"]) for row in subset) / len(subset), 8)
                    if subset
                    else 0.0,
                    "mean_ret60": round(sum(self._safe_float(row["ret60"]) for row in subset) / len(subset), 8)
                    if subset
                    else 0.0,
                    "mean_close_loc60": round(
                        sum(self._safe_float(row["close_loc60"]) for row in subset) / len(subset), 8
                    )
                    if subset
                    else 0.0,
                }
            )

        semantic_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for row in rows:
            key = (row["phase_window_semantic"], row["signal_label_pg"], row["action"])
            semantic_groups.setdefault(key, []).append(row)

        semantic_breakdown_rows: list[dict[str, Any]] = []
        for key, subset in sorted(semantic_groups.items()):
            hit_count = sum(1 for row in subset if bool(row["prototype_flag"]))
            semantic_breakdown_rows.append(
                {
                    "phase_window_semantic": key[0],
                    "signal_label_pg": key[1],
                    "action": key[2],
                    "row_count": len(subset),
                    "prototype_hit_count": hit_count,
                    "prototype_hit_rate": round(hit_count / len(subset), 8),
                }
            )

        flagged_non_override_rows = [
            {
                "signal_trade_date": row["signal_trade_date"],
                "execution_trade_date": row["execution_trade_date"],
                "symbol": row["symbol"],
                "action": row["action"],
                "signal_label_pg": row["signal_label_pg"],
                "phase_window_semantic": row["phase_window_semantic"],
                "supervision_label": row["supervision_label"],
                "ret15": round(self._safe_float(row["ret15"]), 8),
                "ret60": round(self._safe_float(row["ret60"]), 8),
                "draw60": round(self._safe_float(row["draw60"]), 8),
                "close_loc60": round(self._safe_float(row["close_loc60"]), 8),
            }
            for row in rows
            if bool(row["prototype_flag"]) and row["supervision_label"] not in {"override_positive", "reversal_watch"}
        ]

        ambiguous_total = sum(1 for row in rows if row["supervision_label"] == "ambiguous_non_override")
        ambiguous_hits = sum(
            1
            for row in rows
            if row["supervision_label"] == "ambiguous_non_override" and bool(row["prototype_flag"])
        )
        clean_total = sum(1 for row in rows if row["supervision_label"] == "clean_control")
        clean_hits = sum(
            1 for row in rows if row["supervision_label"] == "clean_control" and bool(row["prototype_flag"])
        )

        summary = {
            "acceptance_posture": "freeze_v131u_commercial_aerospace_local_5min_override_coverage_audit_v1",
            "buy_execution_row_count": len(rows),
            "true_positive_seed_hits": sum(
                1
                for row in rows
                if bool(row["prototype_flag"]) and row["supervision_label"] in {"override_positive", "reversal_watch"}
            ),
            "non_override_flagged_count": len(flagged_non_override_rows),
            "ambiguous_hit_count": ambiguous_hits,
            "ambiguous_total": ambiguous_total,
            "ambiguous_hit_rate": round(ambiguous_hits / ambiguous_total, 8) if ambiguous_total else 0.0,
            "clean_control_hit_count": clean_hits,
            "clean_control_total": clean_total,
            "clean_control_hit_rate": round(clean_hits / clean_total, 8) if clean_total else 0.0,
            "authoritative_rule": "the local 5min prototype remains valuable only if it behaves like a severe-case supervision layer and keeps ordinary clean buys untouched",
        }
        interpretation = [
            "V1.31U expands V1.31S from raw retained-case hits into a full-buy-execution coverage and false-positive audit.",
            "The key governance question is not only whether the prototype catches severe cases, but whether its non-override hits remain concentrated in ambiguous edge cases rather than ordinary clean controls.",
        ]
        return V131UCommercialAerospaceLocal5MinOverrideCoverageAuditReport(
            summary=summary,
            label_breakdown_rows=label_breakdown_rows,
            semantic_breakdown_rows=semantic_breakdown_rows,
            flagged_non_override_rows=flagged_non_override_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131UCommercialAerospaceLocal5MinOverrideCoverageAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131UCommercialAerospaceLocal5MinOverrideCoverageAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131u_commercial_aerospace_local_5min_override_coverage_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
