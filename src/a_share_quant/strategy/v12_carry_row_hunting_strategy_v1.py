from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12CarryRowHuntingStrategyReport:
    summary: dict[str, Any]
    hunt_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "hunt_rows": self.hunt_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12CarryRowHuntingStrategyAnalyzer:
    """Freeze the next single-lane hunt order inside the existing v4 carry refresh."""

    def analyze(
        self,
        *,
        v4_manifest_payload: dict[str, Any],
        v4_first_lane_payload: dict[str, Any],
        training_manifest_payload: dict[str, Any],
    ) -> V12CarryRowHuntingStrategyReport:
        checked_symbol = str(dict(v4_first_lane_payload.get("summary", {})).get("top_driver", ""))
        manifest_rows = list(v4_manifest_payload.get("manifest_rows", []))

        target_priority = {
            "basis_spread_diversity": 1,
            "carry_duration_diversity": 2,
            "cross_dataset_carry_reuse": 3,
            "exit_alignment_diversity": 4,
        }

        hunt_rows: list[dict[str, Any]] = []
        for row in manifest_rows:
            symbol = str(row.get("symbol", ""))
            target = str(row.get("target_row_diversity", ""))
            if symbol == checked_symbol:
                continue
            hunt_rows.append(
                {
                    "symbol": symbol,
                    "target_row_diversity": target,
                    "carry_row_hypothesis": str(row.get("carry_row_hypothesis", "")),
                    "priority_bucket": int(target_priority.get(target, 99)),
                    "hunt_posture": (
                        "hunt_next"
                        if target in {"basis_spread_diversity", "carry_duration_diversity"}
                        else "defer_until_high_priority_tracks_checked"
                    ),
                }
            )

        hunt_rows.sort(key=lambda row: (int(row["priority_bucket"]), str(row["symbol"])))

        additional_carry_rows_needed = 0
        for row in training_manifest_payload.get("manifest_rows", []):
            if str(row.get("class_name")) == "carry_row_present":
                additional_carry_rows_needed = int(row.get("additional_rows_needed", 0))
                break

        summary = {
            "strategy_posture": "freeze_v12_carry_row_hunting_strategy_v1",
            "current_primary_bottleneck": "carry_row_diversity_gap",
            "checked_v4_symbol_count": 1 if checked_symbol else 0,
            "remaining_v4_symbol_count": len(hunt_rows),
            "additional_carry_rows_needed": additional_carry_rows_needed,
            "do_open_new_refresh_now": False,
            "do_widen_replay_now": False,
            "recommended_next_action": "hunt_one_v4_symbol_from_basis_or_duration_track",
            "recommended_next_symbol": str(hunt_rows[0]["symbol"]) if hunt_rows else "",
        }
        interpretation = [
            "The next carry-row hunt should stay inside the existing v4 refresh rather than opening another batch.",
            "Because the first checked v4 symbol surfaced as opening-led from the exit-alignment track, the next hunt should move to basis-spread or carry-duration targets first.",
            "This preserves single-lane discipline while still pursuing the actual carry-row-diversity bottleneck.",
        ]
        return V12CarryRowHuntingStrategyReport(
            summary=summary,
            hunt_rows=hunt_rows,
            interpretation=interpretation,
        )


def write_v12_carry_row_hunting_strategy_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12CarryRowHuntingStrategyReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
