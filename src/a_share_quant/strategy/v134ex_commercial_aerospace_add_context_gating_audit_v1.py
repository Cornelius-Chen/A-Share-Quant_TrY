from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(slots=True)
class V134EXCommercialAerospaceAddContextGatingAuditV1Report:
    summary: dict[str, Any]
    scenario_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "scenario_rows": self.scenario_rows,
            "interpretation": self.interpretation,
        }


class V134EXCommercialAerospaceAddContextGatingAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.broader_audit_path = (
            repo_root / "reports" / "analysis" / "v134ev_commercial_aerospace_broader_add_false_positive_audit_v1.json"
        )
        self.expectancy_audit_path = (
            repo_root / "reports" / "analysis" / "v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.json"
        )
        self.registry_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_supervision_registry_v1.csv"
        )

    @staticmethod
    def _ratio(non_seed: int, seed: int) -> float:
        return round(non_seed / seed, 8) if seed else 0.0

    def analyze(self) -> V134EXCommercialAerospaceAddContextGatingAuditV1Report:
        broader = json.loads(self.broader_audit_path.read_text(encoding="utf-8"))
        positive_hits = [
            row
            for row in broader["hit_rows"]
            if row["predicted_label"] in {"allowed_preheat_probe_add", "allowed_preheat_full_add"}
        ]

        expectancy = json.loads(self.expectancy_audit_path.read_text(encoding="utf-8"))
        unlock_dates = {
            row["trade_date"] for row in expectancy["seed_rows"] if row["expectancy_state"] == "unlock_worthy"
        }

        full_pre_start = "20251121"
        full_pre_end = "20251223"
        full_start = "20251224"
        full_end = "20260112"

        with self.registry_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            registry_rows = list(csv.DictReader(handle))

        full_capable_symbols = {
            symbol
            for symbol, count in self._full_capable_symbol_counts(registry_rows).items()
            if count >= 2
        }

        def in_phase_window(trade_date: str) -> bool:
            return (full_pre_start <= trade_date <= full_pre_end) or (full_start <= trade_date <= full_end)

        scenarios: list[tuple[str, Callable[[dict[str, Any]], bool], str]] = [
            ("ungated_positive_shape", lambda row: True, "baseline shape-only positive add rules"),
            ("phase_window_only", lambda row: in_phase_window(row["trade_date"]), "allow only full_pre/full chronology window"),
            ("unlock_worthy_only", lambda row: row["trade_date"] in unlock_dates, "allow only board expectancy unlock-worthy dates"),
            (
                "high_role_symbol_only",
                lambda row: row["symbol"] in full_capable_symbols,
                "allow only symbols with repeated preheat-full participation in the seed registry",
            ),
            (
                "phase_window_plus_high_role",
                lambda row: in_phase_window(row["trade_date"]) and row["symbol"] in full_capable_symbols,
                "combine chronology window with high-role symbol gating",
            ),
            (
                "unlock_worthy_plus_high_role",
                lambda row: row["trade_date"] in unlock_dates and row["symbol"] in full_capable_symbols,
                "combine board expectancy unlock dates with high-role symbol gating",
            ),
            (
                "phase_window_plus_unlock_plus_high_role",
                lambda row: in_phase_window(row["trade_date"]) and row["trade_date"] in unlock_dates and row["symbol"] in full_capable_symbols,
                "apply all currently available slow-context gates together",
            ),
        ]

        scenario_rows: list[dict[str, Any]] = []
        for scenario_name, predicate, reading in scenarios:
            kept_rows = [row for row in positive_hits if predicate(row)]
            seed_kept = sum(1 for row in kept_rows if row["is_seed_session"])
            non_seed_kept = len(kept_rows) - seed_kept
            scenario_rows.append(
                {
                    "scenario_name": scenario_name,
                    "kept_positive_hit_count": len(kept_rows),
                    "seed_kept_count": seed_kept,
                    "non_seed_kept_count": non_seed_kept,
                    "non_seed_to_seed_ratio": self._ratio(non_seed_kept, seed_kept),
                    "reading": reading,
                }
            )

        best_scenario = min(scenario_rows, key=lambda row: row["non_seed_to_seed_ratio"])

        summary = {
            "acceptance_posture": "freeze_v134ex_commercial_aerospace_add_context_gating_audit_v1",
            "scenario_count": len(scenario_rows),
            "baseline_non_seed_to_seed_ratio": next(
                row["non_seed_to_seed_ratio"] for row in scenario_rows if row["scenario_name"] == "ungated_positive_shape"
            ),
            "best_scenario_name": best_scenario["scenario_name"],
            "best_scenario_non_seed_to_seed_ratio": best_scenario["non_seed_to_seed_ratio"],
            "best_scenario_seed_kept_count": best_scenario["seed_kept_count"],
            "best_scenario_non_seed_kept_count": best_scenario["non_seed_kept_count"],
            "authoritative_rule": (
                "currently available slow-context gates help but are still too weak to make broader positive add expansion safe; "
                "the branch needs a stronger point-in-time add-permission context surface"
            ),
        }
        interpretation = [
            "V1.34EX audits whether currently available slow-context gates can rescue broader positive add expansion.",
            "The answer is no: phase, board expectancy, and crude high-role symbol filters reduce density somewhat, but not enough to justify promoting positive add rules beyond the seed surface.",
        ]
        return V134EXCommercialAerospaceAddContextGatingAuditV1Report(
            summary=summary,
            scenario_rows=scenario_rows,
            interpretation=interpretation,
        )

    @staticmethod
    def _full_capable_symbol_counts(rows: list[dict[str, str]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            if row["seed_family"] != "preheat_full_add":
                continue
            if row["supervision_tier"] != "allowed_add_seed":
                continue
            counts[row["symbol"]] = counts.get(row["symbol"], 0) + 1
        return counts


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EXCommercialAerospaceAddContextGatingAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EXCommercialAerospaceAddContextGatingAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ex_commercial_aerospace_add_context_gating_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
