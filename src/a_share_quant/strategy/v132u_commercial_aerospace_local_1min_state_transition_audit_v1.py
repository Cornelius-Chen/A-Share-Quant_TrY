from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _symbol_to_archive_member(symbol: str) -> str:
    if symbol.startswith("6"):
        return f"sh{symbol}.csv"
    if symbol.startswith(("0", "3")):
        return f"sz{symbol}.csv"
    if symbol.startswith(("4", "8")):
        return f"bj{symbol}.csv"
    return f"{symbol}.csv"


STATE_RANK = {
    "neutral": 0,
    "mild_override_watch": 1,
    "reversal_watch": 2,
    "severe_override_positive": 3,
}


def _running_state(*, current_return: float, drawdown: float, close_location: float) -> str:
    if current_return <= -0.08 and close_location <= 0.05:
        return "severe_override_positive"
    if current_return <= -0.05 and drawdown <= -0.05 and close_location <= 0.20:
        return "reversal_watch"
    if current_return <= -0.03 and drawdown <= -0.04 and close_location <= 0.10:
        return "mild_override_watch"
    return "neutral"


@dataclass(slots=True)
class V132UCommercialAerospaceLocal1MinStateTransitionAuditReport:
    summary: dict[str, Any]
    tier_rows: list[dict[str, Any]]
    pattern_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "tier_rows": self.tier_rows,
            "pattern_rows": self.pattern_rows,
            "interpretation": self.interpretation,
        }


class V132UCommercialAerospaceLocal1MinStateTransitionAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.hit_rows_path = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_session_expansion_hits_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"

    def _session_transition(self, trade_date: str, symbol: str) -> dict[str, Any]:
        zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
        member_name = _symbol_to_archive_member(symbol)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name, "r") as member:
                rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]

        base_open = float(rows[0][3])
        highs: list[float] = []
        lows: list[float] = []
        transition_path: list[str] = []
        first_onset = {
            "mild_override_watch": None,
            "reversal_watch": None,
            "severe_override_positive": None,
        }
        max_state = "neutral"

        for idx, row in enumerate(rows, start=1):
            current_close = float(row[4])
            current_high = float(row[5])
            current_low = float(row[6])
            highs.append(current_high)
            lows.append(current_low)
            high_so_far = max(highs)
            low_so_far = min(lows)
            current_return = current_close / base_open - 1.0
            drawdown = low_so_far / base_open - 1.0
            close_location = 0.5 if high_so_far == low_so_far else (current_close - low_so_far) / (high_so_far - low_so_far)
            state = _running_state(
                current_return=current_return,
                drawdown=drawdown,
                close_location=close_location,
            )

            if state != "neutral" and first_onset[state] is None:
                first_onset[state] = idx
            if STATE_RANK[state] > STATE_RANK[max_state]:
                max_state = state
                transition_path.append(state)

        return {
            "first_mild_minute": first_onset["mild_override_watch"],
            "first_reversal_minute": first_onset["reversal_watch"],
            "first_severe_minute": first_onset["severe_override_positive"],
            "max_state_reached": max_state,
            "transition_pattern": "neutral" if not transition_path else "neutral>" + ">".join(transition_path),
        }

    def analyze(self) -> V132UCommercialAerospaceLocal1MinStateTransitionAuditReport:
        with self.hit_rows_path.open("r", encoding="utf-8-sig", newline="") as handle:
            hit_rows = list(csv.DictReader(handle))

        enriched_rows: list[dict[str, Any]] = []
        pattern_counts: dict[str, int] = {}
        for row in hit_rows:
            transition = self._session_transition(row["trade_date"], row["symbol"])
            combined = {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "predicted_tier": row["predicted_tier"],
                **transition,
            }
            enriched_rows.append(combined)
            pattern_counts[combined["transition_pattern"]] = pattern_counts.get(combined["transition_pattern"], 0) + 1

        tier_rows: list[dict[str, Any]] = []
        for tier in ("severe_override_positive", "reversal_watch", "mild_override_watch"):
            subset = [row for row in enriched_rows if row["predicted_tier"] == tier]
            if subset:
                tier_rows.append(
                    {
                        "predicted_tier": tier,
                        "row_count": len(subset),
                        "max_state_same_as_tier_count": sum(1 for row in subset if row["max_state_reached"] == tier),
                        "reached_reversal_or_higher_count": sum(
                            1
                            for row in subset
                            if STATE_RANK[row["max_state_reached"]] >= STATE_RANK["reversal_watch"]
                        ),
                        "reached_severe_count": sum(
                            1
                            for row in subset
                            if row["max_state_reached"] == "severe_override_positive"
                        ),
                        "mean_first_mild_minute": round(
                            sum(row["first_mild_minute"] for row in subset if row["first_mild_minute"] is not None)
                            / max(1, sum(1 for row in subset if row["first_mild_minute"] is not None)),
                            2,
                        ),
                        "mean_first_reversal_minute": round(
                            sum(row["first_reversal_minute"] for row in subset if row["first_reversal_minute"] is not None)
                            / max(1, sum(1 for row in subset if row["first_reversal_minute"] is not None)),
                            2,
                        ),
                        "mean_first_severe_minute": round(
                            sum(row["first_severe_minute"] for row in subset if row["first_severe_minute"] is not None)
                            / max(1, sum(1 for row in subset if row["first_severe_minute"] is not None)),
                            2,
                        ),
                    }
                )

        pattern_rows = [
            {"transition_pattern": pattern, "count": count}
            for pattern, count in sorted(pattern_counts.items(), key=lambda item: (-item[1], item[0]))
        ]

        severe_subset = [row for row in enriched_rows if row["predicted_tier"] == "severe_override_positive"]
        summary = {
            "acceptance_posture": "freeze_v132u_commercial_aerospace_local_1min_state_transition_audit_v1",
            "hit_row_count": len(enriched_rows),
            "unique_transition_pattern_count": len(pattern_rows),
            "top_transition_pattern": pattern_rows[0]["transition_pattern"] if pattern_rows else "",
            "severe_hits_with_prior_reversal_share": round(
                sum(
                    1
                    for row in severe_subset
                    if row["first_reversal_minute"] is not None
                    and row["first_severe_minute"] is not None
                    and row["first_reversal_minute"] <= row["first_severe_minute"]
                )
                / len(severe_subset),
                8,
            )
            if severe_subset
            else 0.0,
            "authoritative_rule": "the local 1min branch is stronger as a governance state machine when broader hit sessions show ordered intraday escalation rather than random isolated tier labels",
        }
        interpretation = [
            "V1.32U studies whether the broader local 1-minute hit sessions evolve through ordered intraday state transitions.",
            "The goal is to check whether severe / reversal / mild behave like a real escalation ladder over the session rather than only as terminal labels.",
        ]
        return V132UCommercialAerospaceLocal1MinStateTransitionAuditReport(
            summary=summary,
            tier_rows=tier_rows,
            pattern_rows=pattern_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132UCommercialAerospaceLocal1MinStateTransitionAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132UCommercialAerospaceLocal1MinStateTransitionAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132u_commercial_aerospace_local_1min_state_transition_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
