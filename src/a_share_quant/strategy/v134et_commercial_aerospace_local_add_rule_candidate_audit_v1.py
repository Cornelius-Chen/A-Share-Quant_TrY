from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ep_commercial_aerospace_intraday_add_tiered_label_specification_v1 import (
    V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Analyzer,
)


def _predict_label_tier(row: dict[str, Any]) -> str:
    if row["board_lockout_active"]:
        return "blocked_board_lockout_add"
    if row["open_to_5m"] <= -0.05 and row["close_loc_15m"] <= 0.05:
        return "failed_impulse_chase_add"
    if (
        row["seed_family"] == "preheat_full_add"
        and row["open_to_15m"] > -0.04
        and row["close_loc_15m"] >= 0.13
    ):
        return "allowed_preheat_full_add"
    if (
        row["seed_family"] == "preheat_probe_add"
        and row["open_to_15m"] > -0.05
    ):
        return "allowed_preheat_probe_add"
    return "unmatched_add_seed"


@dataclass(slots=True)
class V134ETCommercialAerospaceLocalAddRuleCandidateAuditV1Report:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V134ETCommercialAerospaceLocalAddRuleCandidateAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ETCommercialAerospaceLocalAddRuleCandidateAuditV1Report:
        spec_analyzer = V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Analyzer(self.repo_root)
        session_rows = spec_analyzer._build_session_snapshots()

        candidate_rows: list[dict[str, Any]] = []
        matched_count = 0
        unmatched_count = 0
        for row in session_rows:
            predicted_label_tier = _predict_label_tier(row)
            matched = predicted_label_tier == row["label_tier"]
            if matched:
                matched_count += 1
            if predicted_label_tier == "unmatched_add_seed":
                unmatched_count += 1
            candidate_rows.append(
                {
                    "execution_trade_date": row["execution_trade_date"],
                    "symbol": row["symbol"],
                    "action": row["action"],
                    "seed_family": row["seed_family"],
                    "label_tier": row["label_tier"],
                    "predicted_label_tier": predicted_label_tier,
                    "matched": matched,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v134et_commercial_aerospace_local_add_rule_candidate_audit_v1",
            "registry_row_count": len(candidate_rows),
            "matched_count": matched_count,
            "match_rate": round(matched_count / len(candidate_rows), 8) if candidate_rows else 0.0,
            "unmatched_count": unmatched_count,
            "authoritative_rule": (
                "the first local add rule candidates are acceptable only as governed seed rules if they preserve the frozen four-tier add ordering "
                "on the current supervision registry"
            ),
        }
        interpretation = [
            "V1.34ET applies the first explicit local add rules back onto the frozen 55-row add seed surface.",
            "This is a seed-side audit only: the question is whether the rules preserve the allowed/failed/blocked ordering before any broader expansion is attempted.",
        ]
        return V134ETCommercialAerospaceLocalAddRuleCandidateAuditV1Report(
            summary=summary,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ETCommercialAerospaceLocalAddRuleCandidateAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ETCommercialAerospaceLocalAddRuleCandidateAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134et_commercial_aerospace_local_add_rule_candidate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
