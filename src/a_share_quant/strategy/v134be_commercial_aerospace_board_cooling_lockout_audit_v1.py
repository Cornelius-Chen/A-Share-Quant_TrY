from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BECommercialAerospaceBoardCoolingLockoutAuditV1Report:
    summary: dict[str, Any]
    seed_rows: list[dict[str, Any]]
    cluster_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "seed_rows": self.seed_rows,
            "cluster_rows": self.cluster_rows,
            "interpretation": self.interpretation,
        }


class V134BECommercialAerospaceBoardCoolingLockoutAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_state_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_daily_state_v1.csv"
        )
        self.regime_path = (
            repo_root / "reports" / "analysis" / "v125n_commercial_aerospace_structural_regime_discovery_v1.json"
        )
        self.phase_state_path = (
            repo_root / "reports" / "analysis" / "v128w_commercial_aerospace_phase_state_machine_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_board_cooling_lockout_audit_v1.csv"
        )

    @staticmethod
    def _future_value(rows: list[dict[str, Any]], start_idx: int, horizon: int) -> float | None:
        target_idx = start_idx + horizon
        if target_idx >= len(rows):
            return None
        return float(rows[target_idx]["board_overlay_equity"])

    def analyze(self) -> V134BECommercialAerospaceBoardCoolingLockoutAuditV1Report:
        with self.daily_state_path.open("r", encoding="utf-8-sig", newline="") as handle:
            daily_rows = list(csv.DictReader(handle))
        regime_payload = json.loads(self.regime_path.read_text(encoding="utf-8"))
        phase_payload = json.loads(self.phase_state_path.read_text(encoding="utf-8"))
        full_end = str(phase_payload["summary"]["full_end"])

        regime_map = {row["trade_date"]: row for row in regime_payload["date_rows"]}

        peak = 0.0
        drawdown_rows: list[dict[str, Any]] = []
        for idx, row in enumerate(daily_rows):
            overlay = float(row["board_overlay_equity"])
            peak = max(peak, overlay)
            drawdown = overlay / peak - 1.0 if peak > 0 else 0.0
            regime_row = regime_map.get(row["trade_date"], {})
            forward_20 = self._future_value(daily_rows, idx, 20)
            forward_40 = self._future_value(daily_rows, idx, 40)
            drawdown_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "board_overlay_equity": overlay,
                    "board_drawdown_from_peak": round(drawdown, 8),
                    "regime_semantic": regime_row.get("regime_semantic", ""),
                    "turning_point_risk": float(regime_row.get("turning_point_risk", 0.0)),
                    "continuation_support": float(regime_row.get("continuation_support", 0.0)),
                    "forward_board_return_20d": round(forward_20 / overlay - 1.0, 8) if forward_20 else "",
                    "forward_board_return_40d": round(forward_40 / overlay - 1.0, 8) if forward_40 else "",
                }
            )

        candidate_rows = [
            row
            for row in drawdown_rows
            if row["trade_date"] > full_end
            and row["regime_semantic"] in {"weak_drift_chop", "risk_off_deterioration"}
            and float(row["board_drawdown_from_peak"]) <= -0.10
        ]

        cluster_rows: list[dict[str, Any]] = []
        current_cluster: list[dict[str, Any]] = []
        previous_trade_date = ""
        for row in candidate_rows:
            trade_date = row["trade_date"]
            if not current_cluster:
                current_cluster = [row]
                previous_trade_date = trade_date
                continue
            previous_idx = next(i for i, r in enumerate(drawdown_rows) if r["trade_date"] == previous_trade_date)
            current_idx = next(i for i, r in enumerate(drawdown_rows) if r["trade_date"] == trade_date)
            if current_idx - previous_idx <= 5:
                current_cluster.append(row)
            else:
                cluster_rows.append(self._cluster_summary(current_cluster))
                current_cluster = [row]
            previous_trade_date = trade_date
        if current_cluster:
            cluster_rows.append(self._cluster_summary(current_cluster))

        seed_rows: list[dict[str, Any]] = []
        for cluster in cluster_rows:
            if cluster["start_trade_date"] == "" or cluster["start_trade_date"] <= full_end:
                continue
            if cluster["start_forward_board_return_20d"] == "" or cluster["start_forward_board_return_40d"] == "":
                continue
            if float(cluster["start_forward_board_return_20d"]) > 0 or float(cluster["start_forward_board_return_40d"]) > 0:
                continue
            if float(cluster["min_drawdown_in_cluster"]) > -0.10:
                continue
            seed_rows.append(
                {
                    "lockout_start_trade_date": cluster["start_trade_date"],
                    "lockout_end_trade_date": cluster["end_trade_date"],
                    "cluster_day_count": cluster["cluster_day_count"],
                    "dominant_regime_semantic": cluster["dominant_regime_semantic"],
                    "start_drawdown_from_peak": cluster["start_drawdown_from_peak"],
                    "start_forward_board_return_20d": cluster["start_forward_board_return_20d"],
                    "start_forward_board_return_40d": cluster["start_forward_board_return_40d"],
                    "lockout_label": "board_cooling_lockout_watch",
                    "cooldown_guidance": "treat_as_multi_month_cooling_until_clear_board_rebuild_context",
                    "suggested_min_cooldown_trading_days": 60,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(seed_rows[0].keys()) if seed_rows else [
                "lockout_start_trade_date",
                "lockout_end_trade_date",
                "cluster_day_count",
                "dominant_regime_semantic",
                "start_drawdown_from_peak",
                "start_forward_board_return_20d",
                "start_forward_board_return_40d",
                "lockout_label",
                "cooldown_guidance",
                "suggested_min_cooldown_trading_days",
            ])
            writer.writeheader()
            writer.writerows(seed_rows)

        summary = {
            "acceptance_posture": "freeze_v134be_commercial_aerospace_board_cooling_lockout_audit_v1",
            "post_full_candidate_count": len(candidate_rows),
            "cluster_count": len(cluster_rows),
            "lockout_seed_count": len(seed_rows),
            "earliest_lockout_seed_trade_date": seed_rows[0]["lockout_start_trade_date"] if seed_rows else "",
            "suggested_min_cooldown_trading_days": 60 if seed_rows else "",
            "seed_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_board_cooling_lockout_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BE asks whether some post-impulse weakness is no longer a rebuild problem at all, but a board-level cooling lockout.",
            "This stays at supervision level and uses board overlay drawdown plus structure-regime persistence, not single-stock weakness, to name the lockout seed.",
        ]
        return V134BECommercialAerospaceBoardCoolingLockoutAuditV1Report(
            summary=summary,
            seed_rows=seed_rows,
            cluster_rows=cluster_rows,
            interpretation=interpretation,
        )

    @staticmethod
    def _cluster_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
        regime_counts: dict[str, int] = {}
        for row in rows:
            regime = str(row["regime_semantic"])
            regime_counts[regime] = regime_counts.get(regime, 0) + 1
        dominant_regime = max(regime_counts.items(), key=lambda item: item[1])[0]
        start_row = rows[0]
        return {
            "start_trade_date": start_row["trade_date"],
            "end_trade_date": rows[-1]["trade_date"],
            "cluster_day_count": len(rows),
            "dominant_regime_semantic": dominant_regime,
            "min_drawdown_in_cluster": round(min(float(row["board_drawdown_from_peak"]) for row in rows), 8),
            "start_drawdown_from_peak": start_row["board_drawdown_from_peak"],
            "start_forward_board_return_20d": start_row["forward_board_return_20d"],
            "start_forward_board_return_40d": start_row["forward_board_return_40d"],
            "max_turning_point_risk_in_cluster": round(max(float(row["turning_point_risk"]) for row in rows), 8),
        }


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BECommercialAerospaceBoardCoolingLockoutAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BECommercialAerospaceBoardCoolingLockoutAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134be_commercial_aerospace_board_cooling_lockout_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
