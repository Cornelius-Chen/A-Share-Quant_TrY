from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FCCommercialAerospaceFBReduceVolumePriceDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134FCCommercialAerospaceFBReduceVolumePriceDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.memo_report_path = (
            repo_root / "reports" / "analysis" / "v134fb_commercial_aerospace_reduce_volume_price_supplement_memo_v1.json"
        )

    def analyze(self) -> V134FCCommercialAerospaceFBReduceVolumePriceDirectionTriageV1Report:
        memo = json.loads(self.memo_report_path.read_text(encoding="utf-8"))
        status = "freeze_reduce_volume_price_supplement_inside_frozen_handoff_package"
        triage_rows = [
            {
                "component": "reduce_volume_price_confirmation",
                "status": "retain_as_governance_appendix",
                "rationale": "reversal-side quantity-price confirmation already helps distinguish rebound-cost cases from follow-through benefit cases",
            },
            {
                "component": "reduce_local_veto",
                "status": "retain_as_local_supervision_only",
                "rationale": "the local veto improves interpretation for rebound-cost residue without reopening the frozen reduce mainline",
            },
            {
                "component": "reduce_execution_authority",
                "status": "still_blocked",
                "rationale": "the supplement strengthens frozen governance but does not change the execution blocker count",
            },
        ]
        interpretation = [
            "V1.34FC makes the reduce-side quantity-price supplement explicit in governance language.",
            "The branch stays frozen, but its handoff package is now clearer: price-only reduce research was not the endpoint; quantity-price context is part of the retained governance stack.",
        ]
        return V134FCCommercialAerospaceFBReduceVolumePriceDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134fc_commercial_aerospace_fb_reduce_volume_price_direction_triage_v1",
                "authoritative_status": status,
                "strongest_reduce_volume_price_feature": memo["summary"]["strongest_reduce_volume_price_feature"],
                "best_local_veto_up_share_threshold": memo["summary"]["best_local_veto_up_share_threshold"],
                "authoritative_rule": (
                    "the reduce branch remains frozen, but its quantity-price supplement is now an explicit part of the frozen handoff governance package"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FCCommercialAerospaceFBReduceVolumePriceDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FCCommercialAerospaceFBReduceVolumePriceDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fc_commercial_aerospace_fb_reduce_volume_price_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
