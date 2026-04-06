from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


@dataclass(slots=True)
class V132ACommercialAerospaceMinuteTieredLabelSpecificationReport:
    summary: dict[str, Any]
    tier_rows: list[dict[str, Any]]
    proposed_label_rules: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "tier_rows": self.tier_rows,
            "proposed_label_rules": self.proposed_label_rules,
            "interpretation": self.interpretation,
        }


class V132ACommercialAerospaceMinuteTieredLabelSpecificationAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_report_path = (
            repo_root / "reports" / "analysis" / "v131y_commercial_aerospace_intraday_supervision_registry_v1.json"
        )

    @staticmethod
    def _safe_float(value: Any) -> float:
        return float(value) if value not in ("", None) else 0.0

    def analyze(self) -> V132ACommercialAerospaceMinuteTieredLabelSpecificationReport:
        registry = json.loads(self.registry_report_path.read_text(encoding="utf-8"))
        rows = registry["registry_rows"]

        metrics = [
            "open_to_close_return",
            "close_location",
            "ret15",
            "ret30",
            "ret60",
            "draw15",
            "draw60",
            "close_loc15",
            "close_loc60",
        ]

        tier_rows: list[dict[str, Any]] = []
        for tier in ["severe_override_positive", "reversal_watch", "mild_override_watch"]:
            subset = [row for row in rows if row["severity_tier"] == tier]
            tier_row: dict[str, Any] = {"severity_tier": tier, "row_count": len(subset)}
            for metric in metrics:
                vals = [self._safe_float(row[metric]) for row in subset]
                tier_row[f"{metric}_mean"] = round(mean(vals), 8)
                tier_row[f"{metric}_min"] = round(min(vals), 8)
                tier_row[f"{metric}_max"] = round(max(vals), 8)
            tier_rows.append(tier_row)

        proposed_label_rules = [
            {
                "tier": "severe_override_positive",
                "rule_name": "hard_collapse_or_delayed_flush_severe",
                "rule_text": (
                    "label severe_override_positive when either "
                    "(ret15 <= -0.05 and close_loc15 <= 0.05 and open_to_close_return <= -0.09) "
                    "or (ret60 <= -0.048 and close_loc60 <= 0.02 and open_to_close_return <= -0.08)"
                ),
                "motivation": "covers both the immediate hard collapse and the delayed first-hour flush seen in the two severe retained seeds",
            },
            {
                "tier": "reversal_watch",
                "rule_name": "early_crack_or_delayed_rollover_reversal",
                "rule_text": (
                    "label reversal_watch when ret60 <= -0.05 and close_loc60 <= 0.20 and open_to_close_return <= -0.06 "
                    "while the severe rule is not satisfied"
                ),
                "motivation": "keeps the first-hour reversal class broad enough to include both early cracks and delayed rollovers without collapsing into the severe tier",
            },
            {
                "tier": "mild_override_watch",
                "rule_name": "persistent_soft_collapse_watch",
                "rule_text": (
                    "label mild_override_watch when ret60 <= -0.045 and draw60 <= -0.045 and close_loc60 <= 0.05 "
                    "while neither severe nor reversal rules are satisfied"
                ),
                "motivation": "captures the weaker but still real persistent deterioration cases that were initially surfaced as ambiguous hits",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v132a_commercial_aerospace_minute_tiered_label_specification_v1",
            "registry_row_count": len(rows),
            "severity_tier_count": len(tier_rows),
            "authoritative_rule": "the minute branch should now move from loose case supervision to explicit tiered label specification using severe, reversal, and mild override tiers",
        }
        interpretation = [
            "V1.32A converts the frozen intraday supervision registry into explicit minute-tier label envelopes.",
            "The goal is not replay modification; the goal is to define a canonical supervision vocabulary for later 1-minute formalization.",
        ]
        return V132ACommercialAerospaceMinuteTieredLabelSpecificationReport(
            summary=summary,
            tier_rows=tier_rows,
            proposed_label_rules=proposed_label_rules,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132ACommercialAerospaceMinuteTieredLabelSpecificationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132ACommercialAerospaceMinuteTieredLabelSpecificationAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132a_commercial_aerospace_minute_tiered_label_specification_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
