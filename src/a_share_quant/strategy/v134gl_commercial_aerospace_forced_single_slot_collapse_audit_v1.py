from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GLCommercialAerospaceForcedSingleSlotCollapseAuditV1Report:
    summary: dict[str, Any]
    collapse_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "collapse_rows": self.collapse_rows,
            "interpretation": self.interpretation,
        }


class V134GLCommercialAerospaceForcedSingleSlotCollapseAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.ranking_report_path = (
            repo_root / "reports" / "analysis" / "v134fx_commercial_aerospace_active_wave_positive_ranking_audit_v1.json"
        )
        self.allocation_report_path = (
            repo_root / "reports" / "analysis" / "v134gb_commercial_aerospace_dual_slot_allocation_supervision_audit_v1.json"
        )
        self.fallback_report_path = (
            repo_root / "reports" / "analysis" / "v134gj_commercial_aerospace_single_slot_fallback_supervision_audit_v1.json"
        )

    def analyze(self) -> V134GLCommercialAerospaceForcedSingleSlotCollapseAuditV1Report:
        ranking = json.loads(self.ranking_report_path.read_text(encoding="utf-8"))
        allocation = json.loads(self.allocation_report_path.read_text(encoding="utf-8"))
        fallback = json.loads(self.fallback_report_path.read_text(encoding="utf-8"))

        by_symbol = {row["symbol"]: row for row in ranking["candidate_rows"]}
        by_slot = {row["slot_name"]: row for row in allocation["allocation_rows"]}

        reset = by_symbol[by_slot["reset_slot"]["symbol"]]
        continuation = by_symbol[by_slot["continuation_slot"]["symbol"]]

        reset_higher_metric_count = 0
        continuation_higher_metric_count = 0

        if reset["open_to_60m"] > continuation["open_to_60m"]:
            reset_higher_metric_count += 1
        else:
            continuation_higher_metric_count += 1

        if reset["close_loc_15m"] > continuation["close_loc_15m"]:
            reset_higher_metric_count += 1
        else:
            continuation_higher_metric_count += 1

        if reset["burst_amount_share_15"] < continuation["burst_amount_share_15"]:
            reset_higher_metric_count += 1
        else:
            continuation_higher_metric_count += 1

        if reset["open_to_15m"] > continuation["open_to_15m"]:
            reset_higher_metric_count += 1
        else:
            continuation_higher_metric_count += 1

        weight_ratio = allocation["summary"]["reset_to_continuation_weight_ratio"]
        collapse_rows = [
            {
                "collapse_state": "forced_one_slot_local_reading",
                "status": "prefer_reset_slot_surrogate",
                "trade_date": by_slot["reset_slot"]["trade_date"],
                "preferred_slot": "reset_slot",
                "preferred_symbol": reset["symbol"],
                "supporting_reading": (
                    f"metric_edge={reset_higher_metric_count}:{continuation_higher_metric_count}|"
                    f"weight_ratio={weight_ratio:.8f}"
                ),
            },
            {
                "collapse_state": "continuation_slot_counterfactual",
                "status": "retain_only_as_companion",
                "trade_date": by_slot["continuation_slot"]["trade_date"],
                "preferred_slot": "continuation_slot",
                "preferred_symbol": continuation["symbol"],
                "supporting_reading": (
                    f"open_to_15m_edge={continuation['open_to_15m']:.8f}|"
                    f"secondary_weight={by_slot['continuation_slot']['weight_vs_initial_capital']:.6f}"
                ),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134gl_commercial_aerospace_forced_single_slot_collapse_audit_v1",
            "dual_slot_reference_trade_date": by_slot["reset_slot"]["trade_date"],
            "preferred_surrogate_slot": "reset_slot",
            "preferred_surrogate_symbol": reset["symbol"],
            "reset_higher_metric_count": reset_higher_metric_count,
            "continuation_higher_metric_count": continuation_higher_metric_count,
            "reset_to_continuation_weight_ratio": weight_ratio,
            "weak_surrogate_count": fallback["summary"]["weak_surrogate_count"],
            "authoritative_rule": (
                "if the lone observed dual-slot day is forcibly collapsed into one slot, the reset slot has the stronger local claim; "
                "this remains a forced-collapse surrogate, not an observed single-slot template"
            ),
        }
        interpretation = [
            "V1.34GL asks the smallest possible follow-up after single-slot fallback remains unobserved: on the lone dual-slot day, which slot survives a forced collapse into one slot?",
            "The answer stays narrow. Reset survives the forced collapse because it combines the larger local allocation weight with stronger close-location and hour-end continuation, while continuation keeps only an early-impulse companion edge.",
        ]
        return V134GLCommercialAerospaceForcedSingleSlotCollapseAuditV1Report(
            summary=summary,
            collapse_rows=collapse_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GLCommercialAerospaceForcedSingleSlotCollapseAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GLCommercialAerospaceForcedSingleSlotCollapseAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gl_commercial_aerospace_forced_single_slot_collapse_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
