from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


def _safe_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    return float(value)


def _safe_close_location(high_value: float, low_value: float, close_value: float) -> float | None:
    span = high_value - low_value
    if span <= 0:
        return None
    return (close_value - low_value) / span


@dataclass(slots=True)
class V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Report:
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


class V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Analyzer:
    SNAPSHOT_MINUTES = (5, 15, 30, 60)

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_supervision_registry_v1.csv"
        )
        self.feed_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_point_in_time_seed_feed_v1.csv"
        )

    @staticmethod
    def _label_tier(seed_family: str, supervision_tier: str) -> str:
        if supervision_tier == "blocked_add_seed":
            return "blocked_board_lockout_add"
        if supervision_tier == "failed_add_seed":
            return "failed_impulse_chase_add"
        if seed_family == "preheat_full_add" and supervision_tier == "allowed_add_seed":
            return "allowed_preheat_full_add"
        if seed_family == "preheat_probe_add" and supervision_tier == "allowed_add_seed":
            return "allowed_preheat_probe_add"
        return "unclassified_add_seed"

    def _build_session_snapshots(self) -> list[dict[str, Any]]:
        registry_rows: list[dict[str, str]]
        with self.registry_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            registry_rows = list(csv.DictReader(handle))

        registry_map = {
            (row["execution_trade_date"], row["symbol"], row["action"]): row
            for row in registry_rows
        }

        session_bars: dict[tuple[str, str, str], list[dict[str, str]]] = {}
        with self.feed_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                key = (row["execution_trade_date"], row["symbol"], row["action"])
                session_bars.setdefault(key, []).append(row)

        session_snapshots: list[dict[str, Any]] = []
        for key, bars in session_bars.items():
            bars.sort(key=lambda row: int(row["minute_index"]))
            registry_row = registry_map[key]
            label_tier = self._label_tier(registry_row["seed_family"], registry_row["supervision_tier"])
            session_row: dict[str, Any] = {
                "execution_trade_date": registry_row["execution_trade_date"],
                "signal_trade_date": registry_row["signal_trade_date"],
                "symbol": registry_row["symbol"],
                "action": registry_row["action"],
                "seed_family": registry_row["seed_family"],
                "supervision_tier": registry_row["supervision_tier"],
                "label_tier": label_tier,
                "board_lockout_active": registry_row["board_lockout_active"] == "True",
                "local_only_rebound_guard": registry_row["local_only_rebound_guard"] == "True",
                "weight_vs_initial_capital": float(registry_row["weight_vs_initial_capital"]),
            }
            session_open_px = float(bars[0]["bar_open_px"])
            for minute in self.SNAPSHOT_MINUTES:
                snapshot = bars[minute - 1]
                high_values = [float(row["bar_high_px"]) for row in bars[:minute]]
                low_values = [float(row["bar_low_px"]) for row in bars[:minute]]
                close_px = float(snapshot["bar_close_px"])
                session_row[f"open_to_{minute}m"] = close_px / session_open_px - 1.0
                session_row[f"close_loc_{minute}m"] = _safe_close_location(max(high_values), min(low_values), close_px)
                for feature in ("ret_1m_lag1", "ret_3m_lag1", "ret_5m_lag1", "draw_from_open_lag1", "draw_15m_lag1"):
                    session_row[f"{feature}_{minute}m"] = _safe_float(snapshot[feature])
            session_snapshots.append(session_row)

        return session_snapshots

    def analyze(self) -> V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Report:
        session_snapshots = self._build_session_snapshots()
        label_tiers = [
            "allowed_preheat_probe_add",
            "allowed_preheat_full_add",
            "failed_impulse_chase_add",
            "blocked_board_lockout_add",
        ]

        metric_fields = [
            "open_to_5m",
            "close_loc_5m",
            "open_to_15m",
            "close_loc_15m",
            "open_to_30m",
            "close_loc_30m",
            "open_to_60m",
            "close_loc_60m",
        ]
        tier_rows: list[dict[str, Any]] = []
        for label_tier in label_tiers:
            subset = [row for row in session_snapshots if row["label_tier"] == label_tier]
            tier_row: dict[str, Any] = {
                "label_tier": label_tier,
                "session_count": len(subset),
                "seed_family_count": len({row["seed_family"] for row in subset}),
                "board_lockout_active_count": sum(1 for row in subset if row["board_lockout_active"]),
                "local_only_rebound_guard_count": sum(1 for row in subset if row["local_only_rebound_guard"]),
            }
            for field in metric_fields:
                values = [row[field] for row in subset if row[field] is not None]
                tier_row[f"{field}_mean"] = round(mean(values), 8) if values else None
                tier_row[f"{field}_min"] = round(min(values), 8) if values else None
                tier_row[f"{field}_max"] = round(max(values), 8) if values else None
            tier_rows.append(tier_row)

        proposed_label_rules = [
            {
                "label_tier": "allowed_preheat_probe_add",
                "rule_name": "soft_preheat_probe_participation",
                "rule_text": (
                    "label allowed_preheat_probe_add when seed_family = preheat_probe_add, board_lockout_active = false, "
                    "failed_add_seed is false, and the first-15-minute session shape stays broadly stable "
                    "(open_to_15m around flat and close_loc_15m materially above hard-collapse territory)"
                ),
                "motivation": "captures the broader, softer participation layer that historically entered during preheat probe without demanding immediate early strength.",
            },
            {
                "label_tier": "allowed_preheat_full_add",
                "rule_name": "high_quality_preheat_full_acceptance",
                "rule_text": (
                    "label allowed_preheat_full_add when seed_family = preheat_full_add, board_lockout_active = false, "
                    "failed_add_seed is false, and the first-15-minute shape shows positive acceptance "
                    "(open_to_15m > 0 and close_loc_15m concentrated near the upper half of the early range)"
                ),
                "motivation": "separates the stronger preheat-full participation layer from the softer probe adds.",
            },
            {
                "label_tier": "failed_impulse_chase_add",
                "rule_name": "impulse_chase_hard_failure",
                "rule_text": (
                    "label failed_impulse_chase_add when seed_family = impulse_full_add while the first 5 to 15 minutes "
                    "immediately collapse from the open (open_to_5m deeply negative and close_loc_15m near the session floor)"
                ),
                "motivation": "formalizes the two canonical failed impulse-add seeds without pretending they belong to the same family as healthy preheat participation.",
            },
            {
                "label_tier": "blocked_board_lockout_add",
                "rule_name": "board_lockout_or_local_only_rebound_block",
                "rule_text": (
                    "label blocked_board_lockout_add whenever board_lockout_active = true; local_only_rebound_guard is treated as reinforcing negative evidence, "
                    "not as a source of add permission"
                ),
                "motivation": "keeps the add frontier subordinate to the higher-level board veto stack and avoids confusing local rebounds with valid add reopening.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134ep_commercial_aerospace_intraday_add_tiered_label_specification_v1",
            "registry_row_count": len(session_snapshots),
            "label_tier_count": len(label_tiers),
            "seed_family_count": len({row["seed_family"] for row in session_snapshots}),
            "authoritative_rule": (
                "the intraday-add frontier should now move from registry-plus-feed bootstrap into explicit supervision tiers: "
                "allowed preheat probe, allowed preheat full, failed impulse chase, and blocked board lockout add"
            ),
        }
        interpretation = [
            "V1.34EP converts the first intraday-add registry plus point-in-time seed feed into explicit add supervision tiers.",
            "The result is still supervision-only: it defines a canonical add vocabulary before any minute-level execution or replay binding is attempted.",
        ]
        return V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Report(
            summary=summary,
            tier_rows=tier_rows,
            proposed_label_rules=proposed_label_rules,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ep_commercial_aerospace_intraday_add_tiered_label_specification_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
