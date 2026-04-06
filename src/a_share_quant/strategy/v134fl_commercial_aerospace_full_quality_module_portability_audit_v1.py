from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(slots=True)
class V134FLCommercialAerospaceFullQualityModulePortabilityAuditV1Report:
    summary: dict[str, Any]
    scenario_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "scenario_rows": self.scenario_rows,
            "interpretation": self.interpretation,
        }


class V134FLCommercialAerospaceFullQualityModulePortabilityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.context_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_permission_context_sessions_v1.csv"
        )

    def analyze(self) -> V134FLCommercialAerospaceFullQualityModulePortabilityAuditV1Report:
        with self.context_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        for row in rows:
            row["open_to_15m"] = float(row["open_to_15m"])
            row["open_to_60m"] = float(row["open_to_60m"])
            row["burst_amount_share_15"] = float(row["burst_amount_share_15"])
            row["close_loc_15m"] = float(row["close_loc_15m"]) if row["close_loc_15m"] not in ("", None) else None
            row["continuation_15_to_60m"] = row["open_to_60m"] - row["open_to_15m"]
            row["is_seed_allowed"] = row["is_seed_allowed"] == "True"

        scenarios: list[tuple[str, Callable[[dict[str, Any]], bool], str]] = [
            (
                "archetype_only",
                lambda row: row["close_loc_15m"] is not None and row["close_loc_15m"] >= 0.63,
                "the pure full-quality archetype anchor applied directly to the broader positive add surface",
            ),
            (
                "local_confirmation_plus_archetype",
                lambda row: row["open_to_60m"] >= 0.01
                and row["continuation_15_to_60m"] >= 0.005
                and row["burst_amount_share_15"] <= 0.4
                and row["close_loc_15m"] is not None
                and row["close_loc_15m"] >= 0.63,
                "the strongest local confirmation chain plus the full-quality archetype anchor",
            ),
            (
                "unlock_high_role_module",
                lambda row: row["unlock_worthy"] == "True"
                and row["high_role_symbol"] == "True"
                and row["burst_amount_share_15"] <= 0.4,
                "the narrow high-confidence permission clue from V1.34EZ",
            ),
            (
                "unlock_high_role_full_archetype",
                lambda row: row["unlock_worthy"] == "True"
                and row["high_role_symbol"] == "True"
                and row["predicted_label"] == "allowed_preheat_full_add"
                and row["close_loc_15m"] is not None
                and row["close_loc_15m"] >= 0.63
                and row["open_to_60m"] >= 0.015,
                "slow-context gating plus the full-quality archetype inside the broader positive surface",
            ),
            (
                "unlock_high_role_full_archetype_with_burst",
                lambda row: row["unlock_worthy"] == "True"
                and row["high_role_symbol"] == "True"
                and row["predicted_label"] == "allowed_preheat_full_add"
                and row["close_loc_15m"] is not None
                and row["close_loc_15m"] >= 0.63
                and row["open_to_60m"] >= 0.015
                and row["burst_amount_share_15"] <= 0.4,
                "the strongest portable-looking candidate once the archetype, slow context, and burst moderation are all applied together",
            ),
        ]

        scenario_rows: list[dict[str, Any]] = []
        for scenario_name, predicate, reading in scenarios:
            kept_rows = [row for row in rows if predicate(row)]
            seed_kept = sum(1 for row in kept_rows if row["is_seed_allowed"])
            non_seed_kept = len(kept_rows) - seed_kept
            scenario_rows.append(
                {
                    "scenario_name": scenario_name,
                    "kept_positive_hit_count": len(kept_rows),
                    "seed_kept_count": seed_kept,
                    "non_seed_kept_count": non_seed_kept,
                    "non_seed_to_seed_ratio": round(non_seed_kept / seed_kept, 8) if seed_kept else 0.0,
                    "reading": reading,
                }
            )

        best_scenario = min(
            [row for row in scenario_rows if row["seed_kept_count"] > 0],
            key=lambda row: (row["non_seed_to_seed_ratio"], -row["seed_kept_count"], row["non_seed_kept_count"]),
        )

        summary = {
            "acceptance_posture": "freeze_v134fl_commercial_aerospace_full_quality_module_portability_audit_v1",
            "scenario_count": len(scenario_rows),
            "best_scenario_name": best_scenario["scenario_name"],
            "best_scenario_non_seed_to_seed_ratio": best_scenario["non_seed_to_seed_ratio"],
            "best_scenario_seed_kept_count": best_scenario["seed_kept_count"],
            "best_scenario_non_seed_kept_count": best_scenario["non_seed_kept_count"],
            "authoritative_rule": (
                "the strongest local add archetype still does not port cleanly into a broader high-confidence module; it remains a local supervision anchor"
            ),
        }
        interpretation = [
            "V1.34FL tests whether the strongest local add archetype can escape the narrow supervision ladder and become a broader high-confidence module.",
            "The answer is still no: even the best portable-looking scenario remains too noisy relative to the number of retained seed sessions.",
        ]
        return V134FLCommercialAerospaceFullQualityModulePortabilityAuditV1Report(
            summary=summary,
            scenario_rows=scenario_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FLCommercialAerospaceFullQualityModulePortabilityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FLCommercialAerospaceFullQualityModulePortabilityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fl_commercial_aerospace_full_quality_module_portability_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
