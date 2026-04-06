from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1 import (
    V134HKCommercialAerospaceNamedLocalReboundCounterexampleAuditV1Analyzer,
)


@dataclass(slots=True)
class V134HLCommercialAerospaceHKNamedCounterexampleDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HLCommercialAerospaceHKNamedCounterexampleDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134HLCommercialAerospaceHKNamedCounterexampleDirectionTriageV1Report:
        audit = V134HKCommercialAerospaceNamedLocalReboundCounterexampleAuditV1Analyzer(self.repo_root).analyze()

        triage_rows: list[dict[str, Any]] = []
        for row in audit.symbol_rows:
            family = row["counterexample_family"]
            if family == "lockout_outlier_breakout_then_fade":
                direction = "learn_as_board_locked_outlier_breakout_not_board_restart"
            elif family == "raw_only_post_lockout_breakout_without_board_context":
                direction = "learn_as_post_lockout_raw_breakout_without_unlock_authority"
            elif family == "raw_only_near_high_rebound_without_breakout":
                direction = "learn_as_post_lockout_raw_near_high_without_board_permission"
            elif family == "locked_board_weak_repair_only":
                direction = "learn_as_weak_repair_inside_locked_board"
            else:
                direction = "learn_as_coverage_or_activity_gap_not_restart_evidence"
            triage_rows.append(
                {
                    "symbol": row["symbol"],
                    "display_name": row["display_name"],
                    "counterexample_family": family,
                    "direction": direction,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v134hl_commercial_aerospace_hk_named_counterexample_direction_triage_v1",
            "analysis_symbol_count": audit.summary["analysis_symbol_count"],
            "crossed_pre_lockout_peak_count": audit.summary["crossed_pre_lockout_peak_count"],
            "authoritative_status": (
                "retain_named_local_rebound_counterexamples_as_negative_label_candidates_and_do_not_treat_named_strength_as_board_restart_evidence"
            ),
        }
        interpretation = [
            "V1.34HL turns the named-symbol scan into direction: even strong local rebounds are kept as negative-label candidates unless they also rebuild legal board context.",
            "The point is to learn why strong single-name rebounds can coexist with a board that still should not be re-entered.",
        ]
        return V134HLCommercialAerospaceHKNamedCounterexampleDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HLCommercialAerospaceHKNamedCounterexampleDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HLCommercialAerospaceHKNamedCounterexampleDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hl_commercial_aerospace_hk_named_counterexample_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
