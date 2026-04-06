from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BKCommercialAerospaceLocalOnlyReboundAuditV1Report:
    summary: dict[str, Any]
    seed_rows: list[dict[str, Any]]
    threshold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "seed_rows": self.seed_rows,
            "threshold_rows": self.threshold_rows,
            "interpretation": self.interpretation,
        }


class V134BKCommercialAerospaceLocalOnlyReboundAuditV1Analyzer:
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
        self.unlock_path = (
            repo_root / "reports" / "analysis" / "v134bg_commercial_aerospace_board_revival_unlock_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_local_only_rebound_audit_v1.csv"
        )

    def analyze(self) -> V134BKCommercialAerospaceLocalOnlyReboundAuditV1Report:
        lockout = json.loads(self.lockout_path.read_text(encoding="utf-8"))
        unlock = json.loads(self.unlock_path.read_text(encoding="utf-8"))
        lockout_start = lockout["seed_rows"][0]["lockout_start_trade_date"] if lockout["seed_rows"] else ""
        positive_unlock_dates = {row["trade_date"] for row in unlock["positive_seed_rows"]}

        overlay_map: dict[str, dict[str, float]] = {}
        peak = 0.0
        with self.daily_state_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                overlay = float(row["board_overlay_equity"])
                peak = max(peak, overlay)
                overlay_map[row["trade_date"]] = {
                    "board_overlay_equity": overlay,
                    "board_overlay_drawdown": round(overlay / peak - 1.0, 8) if peak > 0 else 0.0,
                }

        by_date: dict[str, dict[str, Any]] = {}
        with self.phase_table_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                trade_date = row["trade_date"]
                if lockout_start and trade_date < lockout_start:
                    continue
                if trade_date not in overlay_map:
                    continue
                forward = row["forward_return_10"]
                if forward == "":
                    continue
                bucket = by_date.setdefault(
                    trade_date,
                    {
                        "trade_date": trade_date,
                        "probe_count": 0,
                        "full_count": 0,
                        "de_risk_count": 0,
                        "forward_rows": [],
                    },
                )
                bucket["forward_rows"].append((row["symbol"], float(forward)))
                label = row["supervised_action_label_pg"]
                if label == "probe_eligibility_target":
                    bucket["probe_count"] += 1
                elif label == "full_eligibility_target":
                    bucket["full_count"] += 1
                elif label == "de_risk_target":
                    bucket["de_risk_count"] += 1

        seed_rows: list[dict[str, Any]] = []
        for trade_date, bucket in sorted(by_date.items()):
            if trade_date in positive_unlock_dates:
                continue
            pos_rows = sorted((item for item in bucket["forward_rows"] if item[1] > 0), key=lambda item: item[1], reverse=True)
            if not pos_rows:
                continue
            top_symbol, top_forward = pos_rows[0]
            total_positive = sum(item[1] for item in pos_rows)
            top_share = round(top_forward / total_positive, 8) if total_positive > 0 else 0.0
            probe_plus_full = bucket["probe_count"] + bucket["full_count"]
            overlay = overlay_map[trade_date]
            board_drawdown = float(overlay["board_overlay_drawdown"])

            if top_forward < 0.15:
                continue
            if top_share < 0.45:
                continue
            if probe_plus_full > 3:
                continue
            if bucket["full_count"] > 1:
                continue
            if board_drawdown > -0.08:
                continue

            seed_rows.append(
                {
                    "trade_date": trade_date,
                    "top_symbol": top_symbol,
                    "top_symbol_forward_return_10": round(top_forward, 8),
                    "top_positive_forward_share": top_share,
                    "positive_symbol_count": len(pos_rows),
                    "probe_count": bucket["probe_count"],
                    "full_count": bucket["full_count"],
                    "probe_plus_full_count": probe_plus_full,
                    "de_risk_count": bucket["de_risk_count"],
                    "board_drawdown": board_drawdown,
                    "local_only_rebound_label": "local_only_rebound_watch",
                    "guidance": "treat_as_local_strength_inside_locked_board_not_board_revival",
                }
            )

        threshold_rows = [
            {
                "rule_name": "local_only_rebound_watch_seed",
                "top_symbol_forward_return_10_min": 0.15,
                "top_positive_forward_share_min": 0.45,
                "probe_plus_full_count_max": 3,
                "full_count_max": 1,
                "board_drawdown_max": -0.08,
                "guard": "keep_board_lockout_if_breadth_fails_even_when_single_names_rebound",
            }
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            fieldnames = list(seed_rows[0].keys()) if seed_rows else [
                "trade_date",
                "top_symbol",
                "top_symbol_forward_return_10",
                "top_positive_forward_share",
                "positive_symbol_count",
                "probe_count",
                "full_count",
                "probe_plus_full_count",
                "de_risk_count",
                "board_drawdown",
                "local_only_rebound_label",
                "guidance",
            ]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(seed_rows)

        summary = {
            "acceptance_posture": "freeze_v134bk_commercial_aerospace_local_only_rebound_audit_v1",
            "lockout_start_trade_date": lockout_start,
            "local_only_rebound_seed_count": len(seed_rows),
            "top_seed_trade_date": seed_rows[0]["trade_date"] if seed_rows else "",
            "top_seed_symbol": seed_rows[0]["top_symbol"] if seed_rows else "",
            "seed_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_local_only_rebound_guard_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BK isolates dates when one or a few symbols rebound sharply while the board itself still lacks unlock-quality breadth.",
            "These are exactly the days that can fool discretionary and quantitative systems into mistaking local strength for board revival.",
        ]
        return V134BKCommercialAerospaceLocalOnlyReboundAuditV1Report(
            summary=summary,
            seed_rows=seed_rows,
            threshold_rows=threshold_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BKCommercialAerospaceLocalOnlyReboundAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BKCommercialAerospaceLocalOnlyReboundAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bk_commercial_aerospace_local_only_rebound_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
