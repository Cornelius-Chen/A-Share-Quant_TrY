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
class V116QCpoExpandedRepairedWindowManifestReport:
    summary: dict[str, Any]
    expanded_window_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "expanded_window_rows": self.expanded_window_rows,
            "interpretation": self.interpretation,
        }


class V116QCpoExpandedRepairedWindowManifestAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v114h_payload: dict[str, Any],
        v114w_payload: dict[str, Any],
    ) -> V116QCpoExpandedRepairedWindowManifestReport:
        top_miss_dates = {str(row["trade_date"]) for row in list(v114w_payload.get("top_opportunity_miss_rows", []))}
        remaining_rows = list(v114h_payload.get("remaining_under_exposed_rows", []))

        expanded_rows: list[dict[str, Any]] = []
        for row in remaining_rows:
            trade_date = str(row["trade_date"])
            expanded_rows.append(
                {
                    "trade_date": trade_date,
                    "board_avg_return": _to_float(row.get("board_avg_return")),
                    "board_breadth": _to_float(row.get("board_breadth")),
                    "baseline_exposure": _to_float(row.get("baseline_exposure")),
                    "promoted_exposure": _to_float(row.get("promoted_exposure")),
                    "under_exposure_gap": _to_float(row.get("under_exposure_gap")),
                    "is_original_top_miss": trade_date in top_miss_dates,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v116q_cpo_expanded_repaired_window_manifest_v1",
            "original_top_miss_day_count": len(top_miss_dates),
            "expanded_repaired_window_day_count": len(expanded_rows),
            "new_day_count_beyond_top_miss": sum(1 for row in expanded_rows if not row["is_original_top_miss"]),
            "recommended_next_posture": "use_expanded_repaired_window_as_next_visible_only_candidate_revalidation_surface",
        }
        interpretation = [
            "V1.16Q freezes an expanded repaired-window manifest so later visible-only candidate reviews stop orbiting only the original top-miss family.",
            "The expanded window uses all remaining under-exposed strong days from V114H, while preserving a marker for which rows belonged to the original repaired top-miss subset.",
            "This manifest is not yet a replay result; it is the widened audit surface required before further replay-facing expansion.",
        ]
        return V116QCpoExpandedRepairedWindowManifestReport(
            summary=summary,
            expanded_window_rows=expanded_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116QCpoExpandedRepairedWindowManifestReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116QCpoExpandedRepairedWindowManifestAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114h_payload=json.loads((repo_root / "reports" / "analysis" / "v114h_cpo_promoted_sizing_behavior_audit_v1.json").read_text(encoding="utf-8")),
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116q_cpo_expanded_repaired_window_manifest_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
