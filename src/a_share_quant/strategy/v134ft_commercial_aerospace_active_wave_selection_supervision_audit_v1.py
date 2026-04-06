from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FTCommercialAerospaceActiveWaveSelectionSupervisionAuditV1Report:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    state_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "state_rows": self.state_rows,
            "interpretation": self.interpretation,
        }


class V134FTCommercialAerospaceActiveWaveSelectionSupervisionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.context_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_permission_context_sessions_v1.csv"
        )
        self.orders_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )
        self.day_level_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_wave_state_authority_days_v1.csv"
        )
        self.output_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_active_wave_selection_candidates_v1.csv"
        )

    @staticmethod
    def _candidate_match(row: dict[str, Any]) -> bool:
        return (
            row["unlock_worthy"] == "True"
            and row["high_role_symbol"] == "True"
            and row["predicted_label"] == "allowed_preheat_full_add"
            and row["close_loc_15m"] is not None
            and row["close_loc_15m"] >= 0.63
            and row["open_to_60m"] >= 0.015
            and row["burst_amount_share_15"] <= 0.4
        )

    def analyze(self) -> V134FTCommercialAerospaceActiveWaveSelectionSupervisionAuditV1Report:
        with self.day_level_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            day_rows = list(csv.DictReader(handle))
        active_wave_days = {
            row["trade_date"] for row in day_rows if row["wave_state"] == "active_wave_selection_day"
        }

        with self.context_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            context_rows = list(csv.DictReader(handle))
        for row in context_rows:
            row["open_to_15m"] = float(row["open_to_15m"])
            row["open_to_60m"] = float(row["open_to_60m"])
            row["close_loc_15m"] = float(row["close_loc_15m"]) if row["close_loc_15m"] else None
            row["burst_amount_share_15"] = float(row["burst_amount_share_15"])

        trading_calendar = sorted(set(row["trade_date"] for row in context_rows))
        trading_index = {trade_date: idx for idx, trade_date in enumerate(trading_calendar)}

        candidate_rows = [
            row for row in context_rows if row["trade_date"] in active_wave_days and self._candidate_match(row)
        ]

        with self.orders_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            order_rows = list(csv.DictReader(handle))

        actual_add_by_day: dict[str, set[str]] = defaultdict(set)
        symbol_history: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in order_rows:
            symbol_history[row["symbol"]].append(row)
            if row["action"] in {"open", "add"}:
                actual_add_by_day[row["execution_trade_date"]].add(row["symbol"])
        for rows in symbol_history.values():
            rows.sort(key=lambda row: row["execution_trade_date"])

        enriched_rows: list[dict[str, Any]] = []
        state_counter: dict[str, dict[str, int]] = defaultdict(lambda: {"selected": 0, "displaced": 0})
        for row in sorted(candidate_rows, key=lambda item: (item["trade_date"], item["symbol"])):
            symbol = row["symbol"]
            trade_date = row["trade_date"]
            prior_actions = [action for action in symbol_history[symbol] if action["execution_trade_date"] < trade_date]
            last_action = prior_actions[-1] if prior_actions else None
            last_action_name = last_action["action"] if last_action else ""
            last_action_trade_date = last_action["execution_trade_date"] if last_action else ""
            last_action_gap = None
            if last_action_trade_date:
                last_action_gap = trading_index[trade_date] - trading_index[last_action_trade_date]

            if last_action_name in {"open", "add"}:
                selection_state = "same_symbol_continuation_selected"
            elif last_action_name in {"reduce", "close"} and last_action_gap is not None and last_action_gap <= 3:
                selection_state = "recent_reduce_residue_candidate"
            else:
                selection_state = "clean_reset_candidate"

            was_selected = symbol in actual_add_by_day.get(trade_date, set())
            selection_outcome = "selected" if was_selected else "displaced"
            state_counter[selection_state][selection_outcome] += 1

            enriched_rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": symbol,
                    "selection_state": selection_state,
                    "selection_outcome": selection_outcome,
                    "last_action_name": last_action_name,
                    "last_action_trade_date": last_action_trade_date,
                    "trading_days_since_last_action": last_action_gap,
                    "open_to_15m": round(row["open_to_15m"], 8),
                    "open_to_60m": round(row["open_to_60m"], 8),
                    "close_loc_15m": round(row["close_loc_15m"], 8) if row["close_loc_15m"] is not None else None,
                    "burst_amount_share_15": round(row["burst_amount_share_15"], 8),
                }
            )

        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(enriched_rows[0].keys()))
            writer.writeheader()
            writer.writerows(enriched_rows)

        state_rows = [
            {
                "selection_state": state,
                "selected_count": counts["selected"],
                "displaced_count": counts["displaced"],
            }
            for state, counts in sorted(state_counter.items())
        ]

        summary = {
            "acceptance_posture": "freeze_v134ft_commercial_aerospace_active_wave_selection_supervision_audit_v1",
            "active_wave_day_count": len(active_wave_days),
            "candidate_count": len(enriched_rows),
            "selected_candidate_count": sum(1 for row in enriched_rows if row["selection_outcome"] == "selected"),
            "displaced_candidate_count": sum(1 for row in enriched_rows if row["selection_outcome"] == "displaced"),
            "recent_reduce_residue_displaced_count": state_counter["recent_reduce_residue_candidate"]["displaced"],
            "same_symbol_continuation_selected_count": state_counter["same_symbol_continuation_selected"]["selected"],
            "clean_reset_selected_count": state_counter["clean_reset_candidate"]["selected"],
            "candidate_rows_csv": str(self.output_csv_path.relative_to(self.repo_root)),
            "authoritative_rule": (
                "inside active add waves, recent symbol-level reduce residue looks like a displacement clue, while same-symbol continuation and clean-reset candidates remain the currently selected states"
            ),
        }
        interpretation = [
            "V1.34FT narrows the add frontier again by studying only the active-wave days and asking what selection-state each same-day candidate was in.",
            "The goal is not to overclaim a complete daily ranker, but to see whether one simple supervision split already separates the displaced case from the selected ones.",
        ]
        return V134FTCommercialAerospaceActiveWaveSelectionSupervisionAuditV1Report(
            summary=summary,
            candidate_rows=enriched_rows,
            state_rows=state_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FTCommercialAerospaceActiveWaveSelectionSupervisionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FTCommercialAerospaceActiveWaveSelectionSupervisionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ft_commercial_aerospace_active_wave_selection_supervision_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
