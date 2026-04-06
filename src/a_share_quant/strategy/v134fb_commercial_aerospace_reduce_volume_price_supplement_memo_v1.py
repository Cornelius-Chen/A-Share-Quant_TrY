from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FBCommercialAerospaceReduceVolumePriceSupplementMemoV1Report:
    summary: dict[str, Any]
    memo_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "memo_rows": self.memo_rows,
            "interpretation": self.interpretation,
        }


class V134FBCommercialAerospaceReduceVolumePriceSupplementMemoV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.volume_price_audit_path = (
            repo_root / "reports" / "analysis" / "v134ai_commercial_aerospace_reversal_volume_price_confirmation_audit_v1.json"
        )
        self.local_veto_audit_path = (
            repo_root / "reports" / "analysis" / "v134ak_commercial_aerospace_rebound_cost_local_veto_audit_v1.json"
        )
        self.reduce_status_path = (
            repo_root / "reports" / "analysis" / "v134cv_commercial_aerospace_reduce_final_status_card_v1.json"
        )

    def analyze(self) -> V134FBCommercialAerospaceReduceVolumePriceSupplementMemoV1Report:
        volume_price = json.loads(self.volume_price_audit_path.read_text(encoding="utf-8"))
        local_veto = json.loads(self.local_veto_audit_path.read_text(encoding="utf-8"))
        reduce_status = json.loads(self.reduce_status_path.read_text(encoding="utf-8"))

        memo_rows = [
            {
                "component": "reversal_volume_price_confirmation",
                "status": "already_available_inside_reduce_governance",
                "detail": (
                    f"strongest_feature = {volume_price['summary']['strongest_feature']}, "
                    f"gap = {volume_price['summary']['strongest_feature_gap_rebound_minus_followthrough']}"
                ),
            },
            {
                "component": "rebound_cost_local_veto",
                "status": "already_available_inside_reduce_governance",
                "detail": (
                    f"up_share_threshold = {local_veto['summary']['best_up_share_threshold']}, "
                    f"open_burst_floor = {local_veto['summary']['best_open_burst_floor']}, "
                    f"precision = {local_veto['summary']['best_precision_rebound']}"
                ),
            },
            {
                "component": "reduce_mainline_status",
                "status": "frozen_handoff",
                "detail": (
                    f"reduce_reopen_ready = {reduce_status['summary']['reduce_reopen_ready']}, "
                    f"execution_blocker_count = {reduce_status['summary']['execution_blocker_count']}"
                ),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134fb_commercial_aerospace_reduce_volume_price_supplement_memo_v1",
            "strongest_reduce_volume_price_feature": volume_price["summary"]["strongest_feature"],
            "strongest_reduce_volume_price_gap": volume_price["summary"]["strongest_feature_gap_rebound_minus_followthrough"],
            "best_local_veto_up_share_threshold": local_veto["summary"]["best_up_share_threshold"],
            "best_local_veto_open_burst_floor": local_veto["summary"]["best_open_burst_floor"],
            "reduce_execution_blocker_count": reduce_status["summary"]["execution_blocker_count"],
            "authoritative_rule": (
                "the frozen reduce handoff should explicitly retain its quantity-price confirmation layer and its local rebound-cost veto as governance appendices"
            ),
        }
        interpretation = [
            "V1.34FB does not reopen reduce; it only makes the existing quantity-price supplement explicit inside the frozen handoff package.",
            "This keeps the reduce branch honest: volume-price already adds value there, but it remains governance-only until full execution infrastructure exists.",
        ]
        return V134FBCommercialAerospaceReduceVolumePriceSupplementMemoV1Report(
            summary=summary,
            memo_rows=memo_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FBCommercialAerospaceReduceVolumePriceSupplementMemoV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FBCommercialAerospaceReduceVolumePriceSupplementMemoV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fb_commercial_aerospace_reduce_volume_price_supplement_memo_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
