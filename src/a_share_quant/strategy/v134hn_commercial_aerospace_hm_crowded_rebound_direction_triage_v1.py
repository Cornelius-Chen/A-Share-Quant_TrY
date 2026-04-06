from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hm_commercial_aerospace_crowded_local_rebound_supervision_audit_v1 import (
    V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134HNCommercialAerospaceHMCrowdedReboundDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HNCommercialAerospaceHMCrowdedReboundDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134HNCommercialAerospaceHMCrowdedReboundDirectionTriageV1Report:
        audit = V134HMCommercialAerospaceCrowdedLocalReboundSupervisionAuditV1Analyzer(self.repo_root).analyze()
        triage_rows: list[dict[str, Any]] = []
        for row in audit.symbol_rows:
            family = row["crowded_rebound_family"]
            if family == "crowding_like_shelter_rebound":
                direction = "learn_as_crowded_shelter_rebound_not_board_restart"
            elif family == "high_beta_raw_only_rebound":
                direction = "learn_as_high_beta_raw_only_rebound_without_unlock"
            elif family == "lockout_outlier_breakout":
                direction = "learn_as_lockout_outlier_breakout_not_restart"
            elif family == "locked_board_weak_repair":
                direction = "learn_as_locked_board_weak_repair"
            else:
                direction = "learn_as_auxiliary_negative_evidence_only"
            triage_rows.append(
                {
                    "symbol": row["symbol"],
                    "display_name": row["display_name"],
                    "crowded_rebound_family": family,
                    "direction": direction,
                }
            )
        summary = {
            "acceptance_posture": "freeze_v134hn_commercial_aerospace_hm_crowded_rebound_direction_triage_v1",
            "analysis_symbol_count": audit.summary["analysis_symbol_count"],
            "crowding_like_shelter_rebound_count": audit.summary["crowding_like_shelter_rebound_count"],
            "authoritative_status": "retain_crowded_local_rebounds_as_negative_label_candidates_and_do_not_treat_symbol_crowding_as_board_unlock",
        }
        interpretation = [
            "V1.34HN turns crowded rebound supervision into direction.",
            "The supervision reading is that crowded strength in a few names should be learned as a board-negative context unless broad board unlock evidence reappears.",
        ]
        return V134HNCommercialAerospaceHMCrowdedReboundDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HNCommercialAerospaceHMCrowdedReboundDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HNCommercialAerospaceHMCrowdedReboundDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hn_commercial_aerospace_hm_crowded_rebound_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
