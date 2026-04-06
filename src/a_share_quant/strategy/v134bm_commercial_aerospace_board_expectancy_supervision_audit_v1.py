from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BMCommercialAerospaceBoardExpectancySupervisionAuditV1Report:
    summary: dict[str, Any]
    seed_rows: list[dict[str, Any]]
    expectancy_rule_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "seed_rows": self.seed_rows,
            "expectancy_rule_rows": self.expectancy_rule_rows,
            "interpretation": self.interpretation,
        }


class V134BMCommercialAerospaceBoardExpectancySupervisionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_state_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_daily_state_v1.csv"
        )
        self.phase_table_path = (
            repo_root / "data" / "training" / "commercial_aerospace_phase_geometry_label_table_v1.csv"
        )
        self.lockout_path = (
            repo_root / "reports" / "analysis" / "v134be_commercial_aerospace_board_cooling_lockout_audit_v1.json"
        )
        self.unlock_path = (
            repo_root / "reports" / "analysis" / "v134bg_commercial_aerospace_board_revival_unlock_audit_v1.json"
        )
        self.local_only_path = (
            repo_root / "reports" / "analysis" / "v134bk_commercial_aerospace_local_only_rebound_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_board_expectancy_supervision_audit_v1.csv"
        )

    def analyze(self) -> V134BMCommercialAerospaceBoardExpectancySupervisionAuditV1Report:
        series = self._load_daily_series()
        phase_counts = self._load_phase_counts()
        lockout = json.loads(self.lockout_path.read_text(encoding="utf-8"))
        unlock = json.loads(self.unlock_path.read_text(encoding="utf-8"))
        local_only = json.loads(self.local_only_path.read_text(encoding="utf-8"))

        seed_map: dict[tuple[str, str], dict[str, Any]] = {}

        for row in unlock["positive_seed_rows"]:
            trade_date = str(row["trade_date"])
            metrics = series[trade_date]
            seed_map[(trade_date, "unlock_worthy")] = {
                "trade_date": trade_date,
                "expectancy_state": "unlock_worthy",
                "breadth_state": "broad_revival",
                "probe_count": row["probe_count"],
                "full_count": row["full_count"],
                "de_risk_count": row["de_risk_count"],
                "board_drawdown": row["board_drawdown"],
                "trailing_board_return_5d": metrics["trailing_board_return_5d"],
                "trailing_board_return_20d": metrics["trailing_board_return_20d"],
                "trailing_board_return_60d": metrics["trailing_board_return_60d"],
                "forward_board_return_20d": metrics["forward_board_return_20d"],
                "forward_board_return_40d": metrics["forward_board_return_40d"],
                "max_favorable_return_20d": metrics["max_favorable_return_20d"],
                "max_adverse_return_20d": metrics["max_adverse_return_20d"],
                "reward_risk_ratio_20d": metrics["reward_risk_ratio_20d"],
                "supporting_evidence": "positive_revival_unlock_seed",
            }

        for row in local_only["seed_rows"]:
            trade_date = str(row["trade_date"])
            metrics = series[trade_date]
            phase = phase_counts.get(trade_date, {"probe_count": 0, "full_count": 0, "de_risk_count": 0})
            seed_map[(trade_date, "false_bounce_only")] = {
                "trade_date": trade_date,
                "expectancy_state": "false_bounce_only",
                "breadth_state": "local_only_rebound",
                "probe_count": phase["probe_count"],
                "full_count": phase["full_count"],
                "de_risk_count": phase["de_risk_count"],
                "board_drawdown": row["board_drawdown"],
                "trailing_board_return_5d": metrics["trailing_board_return_5d"],
                "trailing_board_return_20d": metrics["trailing_board_return_20d"],
                "trailing_board_return_60d": metrics["trailing_board_return_60d"],
                "forward_board_return_20d": metrics["forward_board_return_20d"],
                "forward_board_return_40d": metrics["forward_board_return_40d"],
                "max_favorable_return_20d": metrics["max_favorable_return_20d"],
                "max_adverse_return_20d": metrics["max_adverse_return_20d"],
                "reward_risk_ratio_20d": metrics["reward_risk_ratio_20d"],
                "supporting_evidence": f"local_only_rebound_top_symbol={row['top_symbol']}",
            }

        for row in lockout["seed_rows"]:
            trade_date = str(row["lockout_start_trade_date"])
            metrics = series[trade_date]
            phase = phase_counts.get(trade_date, {"probe_count": 0, "full_count": 0, "de_risk_count": 0})
            seed_map[(trade_date, "lockout_worthy")] = {
                "trade_date": trade_date,
                "expectancy_state": "lockout_worthy",
                "breadth_state": "board_cooling_cluster",
                "probe_count": phase["probe_count"],
                "full_count": phase["full_count"],
                "de_risk_count": phase["de_risk_count"],
                "board_drawdown": row["start_drawdown_from_peak"],
                "trailing_board_return_5d": metrics["trailing_board_return_5d"],
                "trailing_board_return_20d": metrics["trailing_board_return_20d"],
                "trailing_board_return_60d": metrics["trailing_board_return_60d"],
                "forward_board_return_20d": metrics["forward_board_return_20d"],
                "forward_board_return_40d": metrics["forward_board_return_40d"],
                "max_favorable_return_20d": metrics["max_favorable_return_20d"],
                "max_adverse_return_20d": metrics["max_adverse_return_20d"],
                "reward_risk_ratio_20d": metrics["reward_risk_ratio_20d"],
                "supporting_evidence": "board_cooling_lockout_seed",
            }

        seed_rows = sorted(seed_map.values(), key=lambda item: (item["trade_date"], item["expectancy_state"]))

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(seed_rows[0].keys()))
            writer.writeheader()
            writer.writerows(seed_rows)

        expectancy_rule_rows = [
            {
                "rule_name": "unlock_worthy_expectancy",
                "state": "unlock_worthy",
                "reading": "broad participation plus positive forward board expectancy and positive reward-risk",
            },
            {
                "rule_name": "false_bounce_only_expectancy",
                "state": "false_bounce_only",
                "reading": "isolated strong names inside weak breadth with non-positive board expectancy",
            },
            {
                "rule_name": "lockout_worthy_expectancy",
                "state": "lockout_worthy",
                "reading": "deep board drawdown with persistently negative 20d/40d expectancy and poor reward-risk",
            },
        ]

        def _avg(rows: list[dict[str, Any]], key: str) -> float:
            vals = [float(r[key]) for r in rows if r[key] != ""]
            return round(sum(vals) / len(vals), 8) if vals else 0.0

        unlock_rows = [r for r in seed_rows if r["expectancy_state"] == "unlock_worthy"]
        false_rows = [r for r in seed_rows if r["expectancy_state"] == "false_bounce_only"]
        lockout_rows = [r for r in seed_rows if r["expectancy_state"] == "lockout_worthy"]

        summary = {
            "acceptance_posture": "freeze_v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1",
            "seed_count": len(seed_rows),
            "unlock_worthy_count": len(unlock_rows),
            "false_bounce_only_count": len(false_rows),
            "lockout_worthy_count": len(lockout_rows),
            "unlock_worthy_mean_forward_20d": _avg(unlock_rows, "forward_board_return_20d"),
            "false_bounce_only_mean_forward_20d": _avg(false_rows, "forward_board_return_20d"),
            "lockout_worthy_mean_forward_20d": _avg(lockout_rows, "forward_board_return_20d"),
            "unlock_worthy_mean_rr20": _avg(unlock_rows, "reward_risk_ratio_20d"),
            "false_bounce_only_mean_rr20": _avg(false_rows, "reward_risk_ratio_20d"),
            "lockout_worthy_mean_rr20": _avg(lockout_rows, "reward_risk_ratio_20d"),
            "seed_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_board_expectancy_supervision_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BM reframes board state as expectancy rather than shape: what matters is whether board-level forward return and reward-risk are worth touching.",
            "Weekly/monthly context is approximated here by trailing 20d/60d board returns as slow variables; they help condition board state without pretending to solve execution timing.",
        ]
        return V134BMCommercialAerospaceBoardExpectancySupervisionAuditV1Report(
            summary=summary,
            seed_rows=seed_rows,
            expectancy_rule_rows=expectancy_rule_rows,
            interpretation=interpretation,
        )

    def _load_daily_series(self) -> dict[str, dict[str, Any]]:
        with self.daily_state_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        dates = [row["trade_date"] for row in rows]
        overlays = [float(row["board_overlay_equity"]) for row in rows]
        out: dict[str, dict[str, Any]] = {}
        for idx, trade_date in enumerate(dates):
            current = overlays[idx]

            def _trailing(h: int) -> str | float:
                target = idx - h
                if target < 0:
                    return ""
                base = overlays[target]
                return round(current / base - 1.0, 8) if base else ""

            def _forward(h: int) -> str | float:
                target = idx + h
                if target >= len(overlays):
                    return ""
                fut = overlays[target]
                return round(fut / current - 1.0, 8) if current else ""

            def _max_favorable(h: int) -> str | float:
                end = min(len(overlays), idx + h + 1)
                if idx + 1 >= end:
                    return ""
                best = max(overlays[idx + 1 : end])
                return round(best / current - 1.0, 8) if current else ""

            def _max_adverse(h: int) -> str | float:
                end = min(len(overlays), idx + h + 1)
                if idx + 1 >= end:
                    return ""
                worst = min(overlays[idx + 1 : end])
                return round(worst / current - 1.0, 8) if current else ""

            max_fav_20 = _max_favorable(20)
            max_adv_20 = _max_adverse(20)
            rr_20 = ""
            if max_fav_20 != "" and max_adv_20 != "" and float(max_adv_20) < 0:
                rr_20 = round(float(max_fav_20) / abs(float(max_adv_20)), 8)

            out[trade_date] = {
                "trailing_board_return_5d": _trailing(5),
                "trailing_board_return_20d": _trailing(20),
                "trailing_board_return_60d": _trailing(60),
                "forward_board_return_20d": _forward(20),
                "forward_board_return_40d": _forward(40),
                "max_favorable_return_20d": max_fav_20,
                "max_adverse_return_20d": max_adv_20,
                "reward_risk_ratio_20d": rr_20,
            }
        return out

    def _load_phase_counts(self) -> dict[str, dict[str, int]]:
        by_date: dict[str, dict[str, int]] = {}
        with self.phase_table_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                bucket = by_date.setdefault(
                    row["trade_date"],
                    {"probe_count": 0, "full_count": 0, "de_risk_count": 0},
                )
                label = row["supervised_action_label_pg"]
                if label == "probe_eligibility_target":
                    bucket["probe_count"] += 1
                elif label == "full_eligibility_target":
                    bucket["full_count"] += 1
                elif label == "de_risk_target":
                    bucket["de_risk_count"] += 1
        return by_date


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BMCommercialAerospaceBoardExpectancySupervisionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BMCommercialAerospaceBoardExpectancySupervisionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
