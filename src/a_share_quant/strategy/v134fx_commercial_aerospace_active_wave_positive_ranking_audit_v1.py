from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FXCommercialAerospaceActiveWavePositiveRankingAuditV1Report:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    contrast_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "contrast_rows": self.contrast_rows,
            "interpretation": self.interpretation,
        }


class V134FXCommercialAerospaceActiveWavePositiveRankingAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_report_path = (
            repo_root / "reports" / "analysis" / "v134ft_commercial_aerospace_active_wave_selection_supervision_audit_v1.json"
        )

    def analyze(self) -> V134FXCommercialAerospaceActiveWavePositiveRankingAuditV1Report:
        audit = json.loads(self.audit_report_path.read_text(encoding="utf-8"))
        selected_rows = [row for row in audit["candidate_rows"] if row["selection_outcome"] == "selected"]

        same_symbol = next(row for row in selected_rows if row["selection_state"] == "same_symbol_continuation_selected")
        clean_reset = next(row for row in selected_rows if row["selection_state"] == "clean_reset_candidate")

        contrast_rows = [
            {
                "metric": "open_to_15m",
                "same_symbol_continuation_selected": same_symbol["open_to_15m"],
                "clean_reset_selected": clean_reset["open_to_15m"],
                "higher_state": (
                    "same_symbol_continuation_selected"
                    if same_symbol["open_to_15m"] > clean_reset["open_to_15m"]
                    else "clean_reset_selected"
                ),
            },
            {
                "metric": "open_to_60m",
                "same_symbol_continuation_selected": same_symbol["open_to_60m"],
                "clean_reset_selected": clean_reset["open_to_60m"],
                "higher_state": (
                    "same_symbol_continuation_selected"
                    if same_symbol["open_to_60m"] > clean_reset["open_to_60m"]
                    else "clean_reset_selected"
                ),
            },
            {
                "metric": "close_loc_15m",
                "same_symbol_continuation_selected": same_symbol["close_loc_15m"],
                "clean_reset_selected": clean_reset["close_loc_15m"],
                "higher_state": (
                    "same_symbol_continuation_selected"
                    if same_symbol["close_loc_15m"] > clean_reset["close_loc_15m"]
                    else "clean_reset_selected"
                ),
            },
            {
                "metric": "burst_amount_share_15",
                "same_symbol_continuation_selected": same_symbol["burst_amount_share_15"],
                "clean_reset_selected": clean_reset["burst_amount_share_15"],
                "lower_state": (
                    "same_symbol_continuation_selected"
                    if same_symbol["burst_amount_share_15"] < clean_reset["burst_amount_share_15"]
                    else "clean_reset_selected"
                ),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134fx_commercial_aerospace_active_wave_positive_ranking_audit_v1",
            "selected_candidate_count": len(selected_rows),
            "state_count": len({row["selection_state"] for row in selected_rows}),
            "metric_count": len(contrast_rows),
            "same_symbol_higher_metric_count": sum(
                1 for row in contrast_rows if row.get("higher_state") == "same_symbol_continuation_selected"
            ),
            "clean_reset_higher_metric_count": sum(
                1 for row in contrast_rows if row.get("higher_state") == "clean_reset_selected"
            ),
            "authoritative_rule": (
                "the current active-wave sample supports exclusion better than positive ranking: the two retained selected states still split the simple positive metrics rather than collapsing into a single dominant positive ranker"
            ),
        }
        interpretation = [
            "V1.34FX asks the smallest honest positive-ranking question: after carving out the displaced candidate, do the two retained selected states already collapse into a simple internal ranker?",
            "The answer is no. The same-symbol continuation state is stronger on early strength, while the clean-reset state is stronger on close-location and hour-end continuation, so the branch should not pretend it already owns a positive daily ranker.",
        ]
        return V134FXCommercialAerospaceActiveWavePositiveRankingAuditV1Report(
            summary=summary,
            candidate_rows=selected_rows,
            contrast_rows=contrast_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FXCommercialAerospaceActiveWavePositiveRankingAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FXCommercialAerospaceActiveWavePositiveRankingAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fx_commercial_aerospace_active_wave_positive_ranking_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
