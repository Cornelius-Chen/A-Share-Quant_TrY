from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hm_commercial_aerospace_crowded_local_rebound_supervision_audit_v1 import (
    V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134HOCommercialAerospaceCrowdingVsWeakRepairContrastAuditV1Report:
    summary: dict[str, Any]
    contrast_rows: list[dict[str, Any]]
    supporting_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "contrast_rows": self.contrast_rows,
            "supporting_rows": self.supporting_rows,
            "interpretation": self.interpretation,
        }


class V134HOCommercialAerospaceCrowdingVsWeakRepairContrastAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _mean(rows: list[dict[str, Any]], key: str) -> float | None:
        values = [float(row[key]) for row in rows if row.get(key) not in {"", None}]
        if not values:
            return None
        return round(sum(values) / len(values), 8)

    def analyze(self) -> V134HOCommercialAerospaceCrowdingVsWeakRepairContrastAuditV1Report:
        base = V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Analyzer(self.repo_root).analyze()

        crowding_rows = [
            row for row in base.symbol_rows if row["crowded_rebound_family"] == "crowding_like_shelter_rebound"
        ]
        weak_rows = [row for row in base.symbol_rows if row["crowded_rebound_family"] == "locked_board_weak_repair"]
        high_beta_rows = [row for row in base.symbol_rows if row["crowded_rebound_family"] == "high_beta_raw_only_rebound"]

        crowding_peak_gap = self._mean(crowding_rows, "post_lockout_max_vs_pre_lockout_peak")
        weak_peak_gap = self._mean(weak_rows, "post_lockout_max_vs_pre_lockout_peak")
        crowding_avg_turnover = self._mean(crowding_rows, "avg_turnover_rate_f")
        weak_avg_turnover = self._mean(weak_rows, "avg_turnover_rate_f")
        crowding_max_turnover = self._mean(crowding_rows, "max_turnover_rate_f")
        weak_max_turnover = self._mean(weak_rows, "max_turnover_rate_f")
        crowding_avg_vr = self._mean(crowding_rows, "avg_volume_ratio")
        weak_avg_vr = self._mean(weak_rows, "avg_volume_ratio")
        crowding_net = self._mean(crowding_rows, "net_mf_amount_total")
        weak_net = self._mean(weak_rows, "net_mf_amount_total")

        contrast_rows = [
            {
                "contrast_name": "peak_proximity_gap",
                "crowding_like_shelter_rebound_mean": crowding_peak_gap,
                "locked_board_weak_repair_mean": weak_peak_gap,
                "mean_gap": round(crowding_peak_gap - weak_peak_gap, 8) if crowding_peak_gap is not None and weak_peak_gap is not None else "",
                "reading": "crowding names recover materially closer to prior peak than weak-repair names",
            },
            {
                "contrast_name": "avg_turnover_rate_f_gap",
                "crowding_like_shelter_rebound_mean": crowding_avg_turnover,
                "locked_board_weak_repair_mean": weak_avg_turnover,
                "mean_gap": round(crowding_avg_turnover - weak_avg_turnover, 8) if crowding_avg_turnover is not None and weak_avg_turnover is not None else "",
                "reading": "crowding names sustain higher average turnover than weak-repair names",
            },
            {
                "contrast_name": "max_turnover_rate_f_gap",
                "crowding_like_shelter_rebound_mean": crowding_max_turnover,
                "locked_board_weak_repair_mean": weak_max_turnover,
                "mean_gap": round(crowding_max_turnover - weak_max_turnover, 8) if crowding_max_turnover is not None and weak_max_turnover is not None else "",
                "reading": "crowding names spike harder in peak turnover than weak-repair names",
            },
            {
                "contrast_name": "avg_volume_ratio_gap",
                "crowding_like_shelter_rebound_mean": crowding_avg_vr,
                "locked_board_weak_repair_mean": weak_avg_vr,
                "mean_gap": round(crowding_avg_vr - weak_avg_vr, 8) if crowding_avg_vr is not None and weak_avg_vr is not None else "",
                "reading": "crowding names only mildly exceed weak-repair names on volume-ratio; the bigger distinction is turnover and near-high persistence",
            },
            {
                "contrast_name": "net_mf_amount_total_gap",
                "crowding_like_shelter_rebound_mean": crowding_net,
                "locked_board_weak_repair_mean": weak_net,
                "mean_gap": round(crowding_net - weak_net, 8) if crowding_net is not None and weak_net is not None else "",
                "reading": "crowding names can still carry negative aggregate moneyflow; crowding here is a shelter-style concentration clue, not a pure net-inflow clue",
            },
        ]

        supporting_rows = []
        for row in crowding_rows + weak_rows + high_beta_rows:
            supporting_rows.append(
                {
                    "symbol": row["symbol"],
                    "display_name": row["display_name"],
                    "crowded_rebound_family": row["crowded_rebound_family"],
                    "post_lockout_max_vs_pre_lockout_peak": row["post_lockout_max_vs_pre_lockout_peak"],
                    "avg_turnover_rate_f": row["avg_turnover_rate_f"],
                    "max_turnover_rate_f": row["max_turnover_rate_f"],
                    "avg_volume_ratio": row["avg_volume_ratio"],
                    "net_mf_amount_total": row["net_mf_amount_total"],
                }
            )

        summary = {
            "acceptance_posture": "freeze_v134ho_commercial_aerospace_crowding_vs_weak_repair_contrast_audit_v1",
            "crowding_like_shelter_rebound_count": len(crowding_rows),
            "locked_board_weak_repair_count": len(weak_rows),
            "high_beta_raw_only_rebound_count": len(high_beta_rows),
            "peak_proximity_gap": round(crowding_peak_gap - weak_peak_gap, 8) if crowding_peak_gap is not None and weak_peak_gap is not None else "",
            "avg_turnover_rate_f_gap": round(crowding_avg_turnover - weak_avg_turnover, 8) if crowding_avg_turnover is not None and weak_avg_turnover is not None else "",
            "max_turnover_rate_f_gap": round(crowding_max_turnover - weak_max_turnover, 8) if crowding_max_turnover is not None and weak_max_turnover is not None else "",
            "authoritative_output": "commercial_aerospace_crowding_vs_weak_repair_contrast_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34HO contrasts crowded shelter rebounds with ordinary weak repairs inside the locked board.",
            "The point is not that crowded names are healthier; it is that they can run closer to prior highs and on heavier turnover while still failing the board-level restart test.",
        ]
        return V134HOCommercialAerospaceCrowdingVsWeakRepairContrastAuditV1Report(
            summary=summary,
            contrast_rows=contrast_rows,
            supporting_rows=supporting_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HOCommercialAerospaceCrowdingVsWeakRepairContrastAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HOCommercialAerospaceCrowdingVsWeakRepairContrastAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ho_commercial_aerospace_crowding_vs_weak_repair_contrast_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
