from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BGCommercialAerospaceBoardRevivalUnlockAuditV1Report:
    summary: dict[str, Any]
    positive_seed_rows: list[dict[str, Any]]
    false_bounce_rows: list[dict[str, Any]]
    unlock_rule_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "positive_seed_rows": self.positive_seed_rows,
            "false_bounce_rows": self.false_bounce_rows,
            "unlock_rule_rows": self.unlock_rule_rows,
            "interpretation": self.interpretation,
        }


class V134BGCommercialAerospaceBoardRevivalUnlockAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.phase_table_path = (
            repo_root / "data" / "training" / "commercial_aerospace_phase_geometry_label_table_v1.csv"
        )
        self.daily_state_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_daily_state_v1.csv"
        )
        self.lockout_path = (
            repo_root / "reports" / "analysis" / "v134be_commercial_aerospace_board_cooling_lockout_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_board_revival_unlock_audit_v1.csv"
        )

    def analyze(self) -> V134BGCommercialAerospaceBoardRevivalUnlockAuditV1Report:
        date_rows = self._aggregate_date_rows()
        lockout = json.loads(self.lockout_path.read_text(encoding="utf-8"))
        lockout_start = lockout["seed_rows"][0]["lockout_start_trade_date"] if lockout["seed_rows"] else ""

        positive_seed_rows = [
            row
            for row in date_rows
            if row["trade_date"] < lockout_start
            and row["full_count"] >= 2
            and row["probe_plus_full_count"] >= 6
            and row["de_risk_count"] == 0
            and row["forward_board_return_20d"] != ""
            and float(row["forward_board_return_20d"]) > 0
        ]

        false_bounce_rows = [
            row
            for row in date_rows
            if row["trade_date"] >= lockout_start
            and row["probe_plus_full_count"] >= 1
            and row["forward_board_return_20d"] != ""
            and float(row["forward_board_return_20d"]) < 0
        ]

        unlock_rule_rows = [
            {
                "rule_name": "board_revival_unlock_seed",
                "probe_plus_full_count_min": 6,
                "full_count_min": 2,
                "de_risk_count_max": 0,
                "forward_board_return_20d_sign": "positive_for_supervision_seed",
                "guard": "block_small_range_rebound_if_de_risk_count_remains_positive_or_full_count_is_zero",
            }
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            fieldnames = [
                "trade_date",
                "probe_count",
                "full_count",
                "probe_plus_full_count",
                "de_risk_count",
                "phase_window_semantic",
                "regime_proxy_semantic",
                "event_state",
                "board_overlay_equity",
                "board_drawdown",
                "forward_board_return_20d",
                "forward_board_return_40d",
                "seed_role",
            ]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in positive_seed_rows:
                payload = dict(row)
                payload["seed_role"] = "positive_revival_unlock_seed"
                writer.writerow(payload)
            for row in false_bounce_rows:
                payload = dict(row)
                payload["seed_role"] = "false_bounce_block_seed"
                writer.writerow(payload)

        summary = {
            "acceptance_posture": "freeze_v134bg_commercial_aerospace_board_revival_unlock_audit_v1",
            "positive_seed_count": len(positive_seed_rows),
            "false_bounce_seed_count": len(false_bounce_rows),
            "lockout_start_trade_date": lockout_start,
            "unlock_seed_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_board_revival_unlock_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BG asks what board-level shape historically looked like when revival was real rather than a small-range rebound.",
            "The unlock seed is broad by construction: enough full/probe breadth must return and de-risk breadth must collapse, otherwise the move is still treated as a false bounce under lockout.",
        ]
        return V134BGCommercialAerospaceBoardRevivalUnlockAuditV1Report(
            summary=summary,
            positive_seed_rows=positive_seed_rows,
            false_bounce_rows=false_bounce_rows,
            unlock_rule_rows=unlock_rule_rows,
            interpretation=interpretation,
        )

    def _aggregate_date_rows(self) -> list[dict[str, Any]]:
        date_map: dict[str, dict[str, Any]] = {}
        with self.phase_table_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                trade_date = row["trade_date"]
                bucket = date_map.setdefault(
                    trade_date,
                    {
                        "trade_date": trade_date,
                        "probe_count": 0,
                        "full_count": 0,
                        "de_risk_count": 0,
                        "neutral_count": 0,
                        "phase_window_semantic": row["phase_window_semantic"],
                        "regime_proxy_semantic": row["regime_proxy_semantic"],
                        "event_state": row["event_state"],
                    },
                )
                label = row["supervised_action_label_pg"]
                if label == "probe_eligibility_target":
                    bucket["probe_count"] += 1
                elif label == "full_eligibility_target":
                    bucket["full_count"] += 1
                elif label == "de_risk_target":
                    bucket["de_risk_count"] += 1
                else:
                    bucket["neutral_count"] += 1

        daily_rows = []
        with self.daily_state_path.open("r", encoding="utf-8-sig", newline="") as handle:
            daily_rows = list(csv.DictReader(handle))

        trade_dates = [row["trade_date"] for row in daily_rows]
        overlay_map = {row["trade_date"]: row for row in daily_rows}
        out: list[dict[str, Any]] = []
        for trade_date, row in sorted(date_map.items()):
            if trade_date not in overlay_map:
                continue
            idx = trade_dates.index(trade_date)

            def _fwd(h: int) -> str | float:
                target = idx + h
                if target >= len(daily_rows):
                    return ""
                cur = float(overlay_map[trade_date]["board_overlay_equity"])
                fut = float(daily_rows[target]["board_overlay_equity"])
                return round(fut / cur - 1.0, 8)

            overlay = overlay_map[trade_date]
            out.append(
                {
                    "trade_date": trade_date,
                    "probe_count": row["probe_count"],
                    "full_count": row["full_count"],
                    "probe_plus_full_count": row["probe_count"] + row["full_count"],
                    "de_risk_count": row["de_risk_count"],
                    "phase_window_semantic": row["phase_window_semantic"],
                    "regime_proxy_semantic": row["regime_proxy_semantic"],
                    "event_state": row["event_state"],
                    "board_overlay_equity": float(overlay["board_overlay_equity"]),
                    "board_drawdown": float(overlay["drawdown"]),
                    "forward_board_return_20d": _fwd(20),
                    "forward_board_return_40d": _fwd(40),
                }
            )
        return out


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BGCommercialAerospaceBoardRevivalUnlockAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BGCommercialAerospaceBoardRevivalUnlockAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bg_commercial_aerospace_board_revival_unlock_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
